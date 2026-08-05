"""
Fix for a real miss in script 28: Viela Bio was genuinely acquired by
Horizon Therapeutics at a roughly 53% premium, a clean success case,
but it landed in likely_failure_delisted because the deal's tender-
offer structure didn't surface an SC 14D9 in that search. Rather than
add more form types to an already-incomplete list, this checks for 8-K
Item 2.01, "Completion of Acquisition or Disposition of Assets", the
one disclosure that fires regardless of deal structure, tender offer,
straight merger, or asset sale.

Rechecks every company currently in likely_failure_delisted or unclear,
not just the ones recognized by name, since if Viela Bio was missed,
others plausibly were too.

Run with: python scripts/30_check_acquisition_completion.py

Input:  data/processed/exit_reasons.csv
Output: data/processed/exit_reasons.csv (overwritten, reclassified to
        acquisition where Item 2.01 is found)
"""

import time
from pathlib import Path

import pandas as pd
import requests

EXIT_PATH = Path("data/processed/exit_reasons.csv")

FTS_URL = "https://efts.sec.gov/LATEST/search-index"
ACQUISITION_ITEM = "2.01"

HEADERS = {
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json",
}


def check_acquisition_completion(cik10: str) -> str:
    resp = requests.get(FTS_URL, params={"forms": "8-K", "ciks": cik10}, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return None
    hits = resp.json().get("hits", {}).get("hits", [])
    dates = [
        hit.get("_source", {}).get("file_date")
        for hit in hits
        if ACQUISITION_ITEM in (hit.get("_source", {}).get("items") or [])
    ]
    dates = [d for d in dates if d]
    return max(dates) if dates else None  # latest, closest to the actual exit


if __name__ == "__main__":
    df = pd.read_csv(EXIT_PATH, dtype={"cik": str})
    df["cik"] = df["cik"].str.zfill(10)
    to_recheck = df[df["exit_reason"].isin(["likely_failure_delisted", "unclear"])]
    print(f"Rechecking {len(to_recheck)} companies for an Item 2.01 "
          "acquisition-completion disclosure.")

    reclassified = 0
    for i, (idx, row) in enumerate(to_recheck.iterrows()):
        completion_date = check_acquisition_completion(row["cik"])
        if completion_date:
            print(f"  {row['company_name']}: Item 2.01 found ({completion_date}), "
                  f"was {row['exit_reason']!r}, reclassified to acquisition.")
            df.at[idx, "exit_reason"] = "acquisition"
            df.at[idx, "acquisition_completion_date"] = completion_date
            reclassified += 1
        if (i + 1) % 25 == 0:
            print(f"{i + 1}/{len(to_recheck)} checked, {reclassified} reclassified so far")
        time.sleep(0.15)

    df.to_csv(EXIT_PATH, index=False)
    print(f"\n{reclassified} of {len(to_recheck)} reclassified to acquisition.")
    print(df["exit_reason"].value_counts())
