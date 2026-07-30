"""
Step 4.1g: Re-check the companies flagged by 07, correctly this time.

07's pre-existing-filing check counted ANY filing type, including Form D.
Form D is a routine notice private companies file every time they raise
a venture round under a Reg D exemption, it has nothing to do with
having been previously public. Nearly every VC-backed biotech files
several of these years before its actual IPO, so the original check
flagged a large number of completely normal companies as if they were
reverse-merger shells.

This re-checks only the already-flagged companies, this time excluding
Form D and D/A before taking the earliest date. What's left after that
really is evidence of prior public-company status (an earlier S-1, a
10-K, an 8-K), which Form D filings can't produce.

Run with: python scripts/08_recheck_flagged.py

Input:  data/processed/roster_flagged_old.csv
        data/processed/roster_clean.csv
Output: data/processed/roster_clean.csv       (overwritten, false alarms added back)
        data/processed/roster_flagged_old.csv (overwritten, now precise)
"""

import time
from pathlib import Path

import pandas as pd
import requests

FLAGGED_PATH = Path("data/processed/roster_flagged_old.csv")
CLEAN_PATH = Path("data/processed/roster_clean.csv")

WINDOW_START = "2011-01-01"
EXCLUDE_FORMS = {"D", "D/A"}

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

    print(f"Re-checking {len(flagged)} flagged companies, Form D excluded "
          "this time.")

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

    print(f"\n{len(recovered_df)} were false alarms (Form D was the only "
          f"'old' filing on record), moved back into {CLEAN_PATH}.")
    print(f"{len(still_old_df)} still show a genuine pre-2011 substantive "
          f"filing, these are the real reverse-merger/rename cases, left "
          f"in {FLAGGED_PATH}.")
