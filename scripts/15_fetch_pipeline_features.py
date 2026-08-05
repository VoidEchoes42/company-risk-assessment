"""
Step 4.2a: Pull pipeline features (trial phase, prior failures, indications
targeted) per company from ClinicalTrials.gov, restricted to trials that
started before each company's own IPO date.

Two integrity checks built in, both learned the hard way earlier in this
project:
  1. Leakage guard: every trial is checked against its own start date.
     Only trials that started before the company's IPO date count. A
     company that simply existed longer will otherwise look like it "did
     more," which is leakage, not signal.
  2. Lead-sponsor verification: query.spons matches sponsor OR
     collaborator name, so a raw hit doesn't mean the company actually
     ran that trial, it might be a minor collaborator on someone else's.
     Every hit gets checked against the true lead sponsor name using the
     same name-matching logic already proven on the roster.

Confirmed against ClinicalTrials.gov's own API v2 reference: base URL,
no key required, query.spons for sponsor search, and the module
structure below. NOT independently confirmed: the exact field name for
a trial's start date (inferred from the API's consistent *DateStruct
pattern, not seen directly in the reference used). The script prints
the raw statusModule for the first real hit specifically so this can be
checked immediately instead of trusting it blindly.

Run with: python scripts/15_fetch_pipeline_features.py

Input:  data/processed/final_roster.csv
Output: data/processed/pipeline_features.csv
"""

import re
import time
from pathlib import Path

import pandas as pd
import requests

ROSTER_PATH = Path("data/processed/final_roster.csv")
OUT_PATH = Path("data/processed/pipeline_features.csv")

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
HEADERS = {"User-Agent": "Aman <your_email@example.com>"}

PHASE_RANK = {
    "EARLY_PHASE1": 0, "PHASE1": 1, "PHASE2": 2, "PHASE3": 3, "PHASE4": 4,
}
FAILURE_STATUSES = {"TERMINATED", "WITHDRAWN"}

SUFFIXES = {
    "INC", "INCORPORATED", "CORP", "CORPORATION", "LTD", "LIMITED", "LLC",
    "PLC", "CO", "COMPANY", "HOLDING", "HOLDINGS", "GROUP", "BV", "NV", "SA",
    "AG", "SE", "THE",
}


def normalize_name(name: str) -> set:
    name = str(name).upper().replace(".", "")
    name = re.sub(r"[^A-Z0-9 ]", " ", name)
    return {t for t in name.split() if t not in SUFFIXES}


def name_match_score(a: str, b: str) -> float:
    ta, tb = normalize_name(a), normalize_name(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def query_name(company_name: str) -> str:
    """Strip corporate suffixes for a cleaner search term, full legal
    names with 'Inc'/'Corp' tend to search worse than the core name."""
    tokens = [t for t in re.split(r"[,\.\s]+", str(company_name))
              if t.upper() not in SUFFIXES and t]
    return " ".join(tokens)


def fetch_studies(sponsor_query: str) -> list:
    studies, page_token = [], None
    while True:
        params = {"query.spons": sponsor_query, "pageSize": 100}
        if page_token:
            params["pageToken"] = page_token
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            return studies
        data = resp.json()
        studies.extend(data.get("studies", []))
        page_token = data.get("pageToken")
        if not page_token:
            break
    return studies


def extract_features(company_name: str, ipo_date: str, studies: list, show_raw: bool = False):
    ipo_ts = pd.to_datetime(ipo_date, errors="coerce")
    pre_ipo_phases, conditions_seen, had_failure = [], set(), False
    matched_trials = 0

    for study in studies:
        protocol = study.get("protocolSection", {})
        sponsor_name = (
            protocol.get("sponsorCollaboratorsModule", {})
            .get("leadSponsor", {})
            .get("name", "")
        )
        if name_match_score(company_name, sponsor_name) < 0.5:
            continue  # collaborator-only hit, not this company's own trial

        status_module = protocol.get("statusModule", {})
        if show_raw:
            print(f"  Raw statusModule for first matched trial: {status_module}")

        start_date = (
            status_module.get("startDateStruct", {}).get("date")
            or status_module.get("startDateStruct", {}).get("startDate")
        )
        start_ts = pd.to_datetime(start_date, errors="coerce")
        if pd.isna(start_ts) or pd.isna(ipo_ts) or start_ts >= ipo_ts:
            continue  # leakage guard: after IPO, or date unusable, doesn't count

        matched_trials += 1
        for phase in protocol.get("designModule", {}).get("phases", []) or []:
            pre_ipo_phases.append(PHASE_RANK.get(phase, -1))
        conditions_seen.update(protocol.get("conditionsModule", {}).get("conditions", []) or [])
        if status_module.get("overallStatus") in FAILURE_STATUSES:
            had_failure = True

    return {
        "pre_ipo_trial_count": matched_trials,
        "pre_ipo_max_phase_rank": max(pre_ipo_phases) if pre_ipo_phases else None,
        "pre_ipo_conditions_targeted": len(conditions_seen),
        "pre_ipo_had_terminated_or_withdrawn": had_failure,
    }


if __name__ == "__main__":
    roster = pd.read_csv(ROSTER_PATH)
    print(f"Fetching pipeline features for {len(roster)} companies.")

    rows = []
    shown_raw = False
    for i, row in roster.iterrows():
        q = query_name(row["company_name"])
        studies = fetch_studies(q)
        features = extract_features(
            row["company_name"], row["ipo_date"], studies, show_raw=not shown_raw
        )
        if features["pre_ipo_trial_count"] > 0:
            shown_raw = True
        rows.append({"company_name": row["company_name"], "cik": row["cik"], **features})

        if (i + 1) % 25 == 0:
            with_trials = sum(1 for r in rows if r["pre_ipo_trial_count"] > 0)
            print(f"{i + 1}/{len(roster)} done, {with_trials} with at least one matched trial so far")
        time.sleep(0.15)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUT_PATH, index=False)

    zero_trials = (out_df["pre_ipo_trial_count"] == 0).sum()
    print(f"\nWritten to {OUT_PATH}.")
    print(f"{zero_trials} of {len(out_df)} companies show zero matched pre-IPO trials.")
    print("Expect some zeros (pre-clinical companies at IPO are real), but if "
          "this number is large, spot-check a few by hand on clinicaltrials.gov "
          "directly before trusting the rest, that would point to a name-matching "
          "or field-path problem rather than genuine pre-clinical status.")
