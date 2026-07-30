"""
Step 4.1h: One more refinement pass on the 203 still-flagged companies.

REGDEX was the single most common pre-2011 filing type in the flagged
group (145 of 203). It's tied to NASAA's old regional-review coordination
for exempt, Reg-D-style private offerings, the same private-placement
family as Form D, not evidence that a company was already public. I'm
not fully certain of this from the search I ran, so this script exists
specifically to test it empirically rather than assume it: exclude
REGDEX/REGDEX-A the same way Form D was excluded, and see how many of
the 203 were actually resting on REGDEX alone.

The genuinely damning filing types (10-K, 10-Q, 8-K, DEF 14A, S-8, SC
13D/G) all require the filer to already have registered, public
securities, no private company can file any of those. Those are staying
in the exclusion logic regardless, this pass is purely about REGDEX.

Run with: python scripts/10_recheck_regdex.py

Input:  data/processed/roster_flagged_old.csv
        data/processed/roster_clean.csv
Output: data/processed/roster_clean.csv       (overwritten, any recovered added)
        data/processed/roster_flagged_old.csv (overwritten, final precise list)
"""

import time
from pathlib import Path

import pandas as pd
import requests

FLAGGED_PATH = Path("data/processed/roster_flagged_old.csv")
CLEAN_PATH = Path("data/processed/roster_clean.csv")

WINDOW_START = "2011-01-01"
EXCLUDE_FORMS = {"D", "D/A", "REGDEX", "REGDEX/A"}

HEADERS = {
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json",
}


def earliest_substantive_filing(cik10: str):
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return None
    data = resp.json()
    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    substantive = [d for f, d in zip(forms, dates) if f not in EXCLUDE_FORMS]
    return min(substantive) if substantive else None


if __name__ == "__main__":
    flagged = pd.read_csv(FLAGGED_PATH, dtype={"cik": str})
    clean = pd.read_csv(CLEAN_PATH, dtype={"cik": str})
    flagged["cik"] = flagged["cik"].str.zfill(10)

    print(f"Re-checking {len(flagged)} still-flagged companies, REGDEX "
          "excluded this time too.")

    still_old, recovered = [], []
    for i, (idx, row) in enumerate(flagged.iterrows()):
        earliest = earliest_substantive_filing(row["cik"])
        row = row.copy()
        row["earliest_filing_date"] = earliest
        if pd.notna(earliest) and earliest < WINDOW_START:
            row["likely_pre_existing"] = True
            still_old.append(row)
        else:
            row["likely_pre_existing"] = False
            recovered.append(row)
        if (i + 1) % 50 == 0:
            print(f"{i + 1}/{len(flagged)} rechecked, "
                  f"{len(recovered)} recovered so far")
        time.sleep(0.15)

    recovered_df = pd.DataFrame(recovered)
    still_old_df = pd.DataFrame(still_old)

    clean_updated = pd.concat([clean, recovered_df], ignore_index=True)
    clean_updated.to_csv(CLEAN_PATH, index=False)
    still_old_df.to_csv(FLAGGED_PATH, index=False)

    print(f"\n{len(recovered_df)} more recovered once REGDEX was excluded "
          f"too, added to {CLEAN_PATH}.")
    print(f"{len(still_old_df)} remain flagged on real evidence (10-K, "
          f"10-Q, 8-K, DEF 14A, S-8, etc.), left in {FLAGGED_PATH}. This "
          "is the final number, no more filing-type refinements after this.")
