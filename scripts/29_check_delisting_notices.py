"""
Step 4.3c: Check the 'unclear' companies specifically for an Item 3.01
8-K, notice of delisting or failure to satisfy a continued listing rule.
This is a real gap in script 28, not a detection failure: most failing
biotechs never file formal bankruptcy, they quietly wind down instead,
so a lack of an Item 1.03 doesn't mean a lack of failure. Item 3.01 is
the closest thing EDGAR has to a structured "this company failed to
meet its exchange's minimum requirements" signal.

Only rechecks companies currently marked 'unclear', not all 224, to
keep this efficient. Reclassifies to 'likely_failure_delisted' rather
than a bare 'failure' label, since a delisting notice on its own is
strong evidence, not absolute proof (a company can sometimes cure a
deficiency and stay listed, though that is uncommon for a company that
never recovered afterward).

Run with: python scripts/29_check_delisting_notices.py

Input:  data/processed/exit_reasons.csv
Output: data/processed/exit_reasons.csv (overwritten, unclear rows
        reclassified where an Item 3.01 is found)
"""

import time
from pathlib import Path

import pandas as pd
import requests

EXIT_PATH = Path("data/processed/exit_reasons.csv")

FTS_URL = "https://efts.sec.gov/LATEST/search-index"
DELISTING_ITEM = "3.01"

HEADERS = {
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json",
}


def check_delisting_notice(cik10: str) -> str:
    resp = requests.get(FTS_URL, params={"forms": "8-K", "ciks": cik10}, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return None
    hits = resp.json().get("hits", {}).get("hits", [])
    dates = [
        hit.get("_source", {}).get("file_date")
        for hit in hits
        if DELISTING_ITEM in (hit.get("_source", {}).get("items") or [])
    ]
    dates = [d for d in dates if d]
    return min(dates) if dates else None


if __name__ == "__main__":
    df = pd.read_csv(EXIT_PATH, dtype={"cik": str})
    df["cik"] = df["cik"].str.zfill(10)
    unclear = df[df["exit_reason"] == "unclear"]
    print(f"Checking {len(unclear)} 'unclear' companies for an Item 3.01 delisting notice.")

    reclassified = 0
    for i, (idx, row) in enumerate(unclear.iterrows()):
        delisting_date = check_delisting_notice(row["cik"])
        if delisting_date:
            df.at[idx, "exit_reason"] = "likely_failure_delisted"
            df.at[idx, "delisting_notice_date"] = delisting_date
            reclassified += 1
            print(f"  {row['company_name']}: Item 3.01 found ({delisting_date}), reclassified.")
        if (i + 1) % 25 == 0:
            print(f"{i + 1}/{len(unclear)} checked, {reclassified} reclassified so far")
        time.sleep(0.15)

    df.to_csv(EXIT_PATH, index=False)
    print(f"\n{reclassified} of {len(unclear)} reclassified to likely_failure_delisted.")
    print(df["exit_reason"].value_counts())
    print("\nRemaining 'unclear' companies genuinely need an individual look, "
          "no more mechanical passes after this one.")
