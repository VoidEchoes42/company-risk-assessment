"""
Step 4.1e: Reconcile the ticker-based roster against the ticker-independent
EDGAR filing search, recovering companies the ticker method missed or
mismatched entirely.

Why: roster_edgar_crosscheck.csv (640 companies) came from searching
EDGAR's own filing index directly by SIC code and date, no ticker
involved anywhere. Anything genuinely life-science in our IPO window
should show up there regardless of what happened to its ticker since.

What this does:
  1. For each of the 640 cross-check companies, check by name whether
     it's already in the 117 verified companies. If yes, already have
     it correctly, skip.
  2. If not, fetch its real SIC directly from EDGAR (the cross-check
     file doesn't store SIC) and add it, but only if that SIC is
     genuinely one of the four life-science codes, confirmed off the
     entity record itself rather than trusted from the search index.
  3. Check which of the 6 original suspects (Adeptus Health and friends)
     ended up recovered this way, and which are still stuck.

Run with: python scripts/05_recover_via_crosscheck.py

Inputs:
  data/processed/roster_life_science_verified.csv
  data/processed/roster_life_science_suspect.csv
  data/processed/roster_edgar_crosscheck.csv

Outputs:
  data/processed/roster_final.csv        (verified + recovered, trust this)
  data/processed/roster_needs_manual.csv (couldn't resolve automatically)
"""

import re
import time
from pathlib import Path

import pandas as pd
import requests

VERIFIED_PATH = Path("data/processed/roster_life_science_verified.csv")
SUSPECT_PATH = Path("data/processed/roster_life_science_suspect.csv")
CROSSCHECK_PATH = Path("data/processed/roster_edgar_crosscheck.csv")
FINAL_PATH = Path("data/processed/roster_final.csv")
MANUAL_PATH = Path("data/processed/roster_needs_manual.csv")

MATCH_THRESHOLD = 0.5
LIFE_SCIENCE_SIC = {"2830", "2834", "2835", "2836"}

HEADERS = {
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json",
}

SUFFIXES = {
    "INC", "INCORPORATED", "CORP", "CORPORATION", "LTD", "LIMITED", "LLC",
    "PLC", "CO", "COMPANY", "HOLDING", "HOLDINGS", "GROUP", "BV", "NV", "SA",
    "AG", "SE", "THE",
}


def clean_company_name(name: str) -> str:
    # EDGAR's full-text-search display_names sometimes appends
    # disambiguating parentheticals, e.g. "Epizyme, Inc.  (CIK 0001571498)"
    # or "OptiNose, Inc.  (OPTN)  (CIK 0001494650)". These are display
    # artifacts, not part of the real company name, and they wreck name
    # matching if left in.
    name = re.sub(r"\s*\([^)]*\)\s*", " ", str(name))
    return re.sub(r"\s+", " ", name).strip()


def normalize_name(name: str) -> set:
    # Periods removed BEFORE the alphanumeric filter, not replaced with
    # spaces, so "N.V." collapses to "NV" instead of splitting into the
    # two junk tokens "N" and "V". That distinction is what let
    # "Prosensa Holding BV" and "Prosensa Holding N.V." match correctly.
    name = str(name).upper().replace(".", "")
    name = re.sub(r"[^A-Z0-9 ]", " ", name)
    return {t for t in name.split() if t not in SUFFIXES}


def name_match_score(a: str, b: str) -> float:
    # Jaccard similarity (intersection over UNION), not intersection over
    # the smaller name. The earlier version used the smaller-name
    # denominator, which let any two names sharing one common industry
    # word ("Health", "Therapeutics") score an automatic 0.5, regardless
    # of how different the rest of the name was. Adeptus Health matched
    # three unrelated "Animal Health" companies that way, and Audentes
    # Therapeutics matched two unrelated "Therapeutics" companies.
    ta, tb = normalize_name(a), normalize_name(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def fetch_sic(cik10: str) -> tuple:
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return None, None
    data = resp.json()
    return data.get("sic"), data.get("sicDescription")


if __name__ == "__main__":
    verified = pd.read_csv(VERIFIED_PATH, dtype={"cik": str})
    suspect = pd.read_csv(SUSPECT_PATH, dtype={"cik": str})
    crosscheck = pd.read_csv(CROSSCHECK_PATH, dtype={"cik": str})
    verified["cik"] = verified["cik"].str.zfill(10)
    crosscheck["company_name"] = crosscheck["company_name"].apply(clean_company_name)

    verified_names = verified["company_name"].tolist()
    print(f"Checking {len(crosscheck)} cross-check companies against "
          f"{len(verified)} already-verified companies.")

    recovered_rows = []
    already_have = 0
    for i, row in crosscheck.iterrows():
        cik_raw = str(row.get("cik", "")).strip()
        if not cik_raw or cik_raw.lower() == "nan":
            continue

        best = max(
            (name_match_score(row["company_name"], vn) for vn in verified_names),
            default=0.0,
        )
        if best >= MATCH_THRESHOLD:
            already_have += 1
            continue

        cik10 = cik_raw.zfill(10)
        sic, sic_desc = fetch_sic(cik10)
        if sic in LIFE_SCIENCE_SIC:
            recovered_rows.append(
                {
                    "company_name": row["company_name"],
                    "cik": cik10,
                    "sic": sic,
                    "sic_description": sic_desc,
                    "source": "edgar_crosscheck",
                }
            )
        if (i + 1) % 50 == 0:
            print(f"{i + 1}/{len(crosscheck)} checked, "
                  f"{len(recovered_rows)} new so far")
        time.sleep(0.15)

    print(f"\n{already_have} already had a verified match. "
          f"{len(recovered_rows)} new companies recovered.")

    recovered = pd.DataFrame(recovered_rows)
    final = pd.concat([verified, recovered], ignore_index=True)
    final = final.drop_duplicates(subset="company_name")

    final_names = final["company_name"].tolist()
    still_stuck = [
        row["company_name"]
        for _, row in suspect.iterrows()
        if max(
            (name_match_score(row["company_name"], fn) for fn in final_names),
            default=0.0,
        )
        < MATCH_THRESHOLD
    ]

    FINAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    final.to_csv(FINAL_PATH, index=False)
    pd.DataFrame({"company_name": still_stuck}).to_csv(MANUAL_PATH, index=False)

    print(f"\n{len(final)} companies in the final roster, written to {FINAL_PATH}")
    print(f"{len(still_stuck)} still need a manual CIK lookup: {still_stuck}")
    print("If Adeptus Health is in that list, that's correct, drop it, it "
          "isn't a life-science company. The ticker collision is the only "
          "reason it was ever in this pipeline.")
