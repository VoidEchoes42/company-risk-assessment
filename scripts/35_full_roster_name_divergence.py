"""
Step 4.3g: Extend the name-divergence check (originally script 32,
acquisition-bucket only) to the FULL current roster. Dynamic Nutra
Enterprises Holdings was a genuine shell company hiding inside
"acquisition," there's no structural reason a similarly chaotic shell
couldn't be sitting in "unclear," "bankruptcy," or even "actively_filing"
instead, none of those buckets have had this specific check run against
them at all.

Same logic as script 32, reused rather than rewritten: current
SEC-registered name compared against the name on file using the
established Jaccard token-overlap scorer. A near-zero score means the
company's identity has changed so completely that the entity being
studied and the entity currently on record may not really be the same
business, worth a human look regardless of which outcome bucket it's
currently sitting in.

Run with: python scripts/35_full_roster_name_divergence.py

Input:  data/processed/final_roster.csv
Output: data/processed/full_name_divergence_check.csv
"""

import re
import time
from pathlib import Path

import pandas as pd
import requests

ROSTER_PATH = Path("data/processed/final_roster.csv")
OUT_PATH = Path("data/processed/full_name_divergence_check.csv")

DIVERGENCE_THRESHOLD = 0.15

SUFFIXES = {
    "INC", "INCORPORATED", "CORP", "CORPORATION", "LTD", "LIMITED", "LLC",
    "PLC", "CO", "COMPANY", "HOLDING", "HOLDINGS", "GROUP", "BV", "NV", "SA",
    "AG", "SE", "THE",
}

HEADERS = {
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json",
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


def get_current_registered_name(cik10: str):
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return None
    return resp.json().get("name")


if __name__ == "__main__":
    roster = pd.read_csv(ROSTER_PATH, dtype={"cik": str})
    roster["cik"] = roster["cik"].str.zfill(10)
    print(f"Checking all {len(roster)} companies in the current roster for "
          "name divergence, not just the acquisition bucket this time.")

    rows = []
    for i, (idx, row) in enumerate(roster.iterrows()):
        current_name = get_current_registered_name(row["cik"])
        score = name_match_score(row["company_name"], current_name) if current_name else None
        flagged = score is not None and score < DIVERGENCE_THRESHOLD

        rows.append({
            "company_name": row["company_name"], "cik": row["cik"],
            "current_registered_name": current_name,
            "name_match_score": score, "flagged_for_review": flagged,
        })
        if flagged:
            print(f"  FLAGGED: {row['company_name']!r} -> now {current_name!r} "
                  f"(match score {score:.2f})")

        if (i + 1) % 25 == 0:
            n_flagged = sum(r["flagged_for_review"] for r in rows)
            print(f"{i + 1}/{len(roster)} checked, {n_flagged} flagged so far")
        time.sleep(0.15)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUT_PATH, index=False)

    n_flagged = out_df["flagged_for_review"].sum()
    print(f"\n{n_flagged} of {len(out_df)} flagged across the full roster, "
          f"written to {OUT_PATH}.")
    print("Some of these will already be the 13 already-resolved acquisition "
          "cases from before, expected, not new work. Anything NEW showing up "
          "here (from unclear/bankruptcy/actively_filing) is the actual find "
          "worth individual research.")
