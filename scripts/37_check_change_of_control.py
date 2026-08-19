"""
Step 4.3i: Distinguish genuine reverse-merger-driven identity changes
from benign internal rebrands among the 42 newly-flagged, unresolved
companies, prioritizing the 36 sitting in actively_filing since that is
where a wrong label costs the most (we have been treating that bucket
as presumptively favorable).

The distinguishing signal: a real reverse merger changes who owns the
company, majority control passes to a new set of shareholders. That
specifically triggers 8-K Item 5.01 (Changes in Control of Registrant).
A plain rebrand via corporate charter amendment, no merger, no change
of ownership, triggers Item 5.03 instead, never 5.01. BeiGene's rename
to BeOne is exactly this second case: same company, same shareholders,
new brand. Conatus's reverse merger into Histogen is the first case.

This flags likely_reverse_merger vs likely_benign_rebrand. It does not
assign a final outcome label by itself, that still needs the same kind
of individual confirmation used for the acquisition-bucket companies,
this narrows down which of the 42 actually need that effort.

Run with: python scripts/37_check_change_of_control.py

Input:  data/processed/divergence_priority.csv
Output: data/processed/change_of_control_check.csv
"""

import time
from pathlib import Path

import pandas as pd
import requests

PRIORITY_PATH = Path("data/processed/divergence_priority.csv")
OUT_PATH = Path("data/processed/change_of_control_check.csv")

FTS_URL = "https://efts.sec.gov/LATEST/search-index"
CHANGE_OF_CONTROL_ITEM = "5.01"

HEADERS = {
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json",
}


def check_change_of_control(cik10: str) -> str:
    resp = requests.get(FTS_URL, params={"forms": "8-K", "ciks": cik10}, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return None
    hits = resp.json().get("hits", {}).get("hits", [])
    dates = [
        hit.get("_source", {}).get("file_date")
        for hit in hits
        if CHANGE_OF_CONTROL_ITEM in (hit.get("_source", {}).get("items") or [])
    ]
    dates = [d for d in dates if d]
    return min(dates) if dates else None


if __name__ == "__main__":
    df = pd.read_csv(PRIORITY_PATH, dtype={"cik": str})
    to_check = df[(~df["already_resolved"]) & (df["self_evident_keyword"].isna())]
    to_check["cik"] = to_check["cik"].str.zfill(10)
    print(f"Checking {len(to_check)} companies for a genuine change-of-control event.")

    rows = []
    for i, (idx, row) in enumerate(to_check.iterrows()):
        control_date = check_change_of_control(row["cik"])
        likely_type = "likely_reverse_merger" if control_date else "likely_benign_rebrand"
        rows.append({
            "company_name": row["company_name"], "cik": row["cik"],
            "current_status": row["current_status"],
            "current_registered_name": row["current_registered_name"],
            "change_of_control_date": control_date, "likely_type": likely_type,
        })
        print(f"  {row['company_name']} ({row['current_status']}): {likely_type}"
              + (f", control event {control_date}" if control_date else ""))
        if (i + 1) % 25 == 0:
            print(f"{i + 1}/{len(to_check)} checked")
        time.sleep(0.15)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUT_PATH, index=False)

    print(f"\nWritten to {OUT_PATH}.")
    print(out_df["likely_type"].value_counts())
    print("\nlikely_reverse_merger companies are the real priority for "
          "individual research next, that is where hidden failure is most "
          "plausible. likely_benign_rebrand companies (BeiGene should land "
          "here) probably don't need individual research, but spot-check a "
          "couple before fully trusting the mechanical call.")
