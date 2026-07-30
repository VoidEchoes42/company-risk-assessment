"""
Diagnostic, not a filter: for each still-flagged company, print every
pre-2011 filing (form type and date), so we can actually see what's
causing the flag instead of guessing again. Two theories on the table:

  A) An earlier, withdrawn S-1 attempt for the same business (2008-2009
     killed the IPO market for a couple of years, plenty of biotechs
     tried once, pulled it, and succeeded later). Not a reverse merger,
     just a delayed IPO, this company still belongs in the roster.
  B) Genuine 10-K/10-Q/proxy filings, meaning this CIK was an actual
     operating public reporting company under a different business
     before being renamed. That IS a reverse-merger case.

Run with: python scripts/09_inspect_flagged.py

Input: data/processed/roster_flagged_old.csv
"""

import time
from pathlib import Path

import pandas as pd
import requests

FLAGGED_PATH = Path("data/processed/roster_flagged_old.csv")

WINDOW_START = "2011-01-01"
EXCLUDE_FORMS = {"D", "D/A"}

HEADERS = {
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json",
}


def pre_window_filings(cik10: str):
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return []
    data = resp.json()
    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    return sorted(
        (f, d) for f, d in zip(forms, dates)
        if f not in EXCLUDE_FORMS and d < WINDOW_START
    )


if __name__ == "__main__":
    flagged = pd.read_csv(FLAGGED_PATH, dtype={"cik": str})
    flagged["cik"] = flagged["cik"].str.zfill(10)

    form_counts = {}
    for i, row in flagged.iterrows():
        pre = pre_window_filings(row["cik"])
        forms_seen = {f for f, d in pre}
        for f in forms_seen:
            form_counts[f] = form_counts.get(f, 0) + 1
        if i < 15:  # print full detail for a first look, not all 203
            print(f"{row['company_name']!r}: {pre[:6]}")
        if (i + 1) % 50 == 0:
            print(f"...{i + 1}/{len(flagged)} scanned")
        time.sleep(0.15)

    print("\nHow many flagged companies have each pre-2011 form type "
          "(a company can have more than one):")
    for form, count in sorted(form_counts.items(), key=lambda x: -x[1]):
        print(f"  {form}: {count}")
