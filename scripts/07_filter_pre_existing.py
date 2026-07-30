"""
Step 4.1f: Two integrity passes on roster_final.csv before it's usable.

1. Deduplicate by CIK. Same CIK means same legal SEC filer no matter what
   two display names got captured for it. When a duplicate pair has one
   Ritter-verified row (real ticker, real IPO date) and one recovered
   row, keep the verified one, it's the trustworthy source.

2. Flag recovered (non-Ritter-verified) companies whose SEC filing
   history goes back well before 2012. Reverse mergers and corporate
   renames are extremely common among small-cap biotechs, an old,
   sometimes completely unrelated shell company gets renamed into a
   "new" biotech instead of that biotech doing a traditional IPO. If a
   company was already filing with the SEC years before our window,
   whatever the cross-check search matched almost certainly wasn't a
   first-time IPO. Those get pulled out for review, not silently kept.

Note: this reads only each CIK's "recent" filings list, which SEC caps
for companies with very long histories. If a company's earliest filing
has aged out of that cap, this will still show *something* well before
2012 as long as anything old survived in the recent list, but it isn't
a perfect earliest-filing lookup. Good enough to catch the pattern seen
here, not a substitute for spot-checking the flagged list by hand.

Run with: python scripts/07_filter_pre_existing.py

Input:  data/processed/roster_final.csv
Output: data/processed/roster_clean.csv       (deduped, confirmed recent)
        data/processed/roster_flagged_old.csv (pre-existing, needs review)
"""

import time
from pathlib import Path

import pandas as pd
import requests

IN_PATH = Path("data/processed/roster_final.csv")
CLEAN_PATH = Path("data/processed/roster_clean.csv")
FLAGGED_PATH = Path("data/processed/roster_flagged_old.csv")

WINDOW_START = "2011-01-01"  # a little slack before 2012 for filing lag

HEADERS = {
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json",
}


def earliest_filing_date(cik10: str):
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return None
    data = resp.json()
    dates = data.get("filings", {}).get("recent", {}).get("filingDate", [])
    return min(dates) if dates else None


if __name__ == "__main__":
    df = pd.read_csv(IN_PATH, dtype={"cik": str})
    df["cik"] = df["cik"].str.zfill(10)

    has_date_col = "ipo_date" in df.columns
    df["has_ipo_date"] = df["ipo_date"].notna() if has_date_col else False
    df = df.sort_values("has_ipo_date", ascending=False)
    before = len(df)
    df = df.drop_duplicates(subset="cik", keep="first")
    print(f"Deduped by CIK: {before} -> {len(df)} rows "
          f"({before - len(df)} duplicate CIKs merged, "
          "Ritter-verified kept where one existed).")

    needs_check = df[~df["has_ipo_date"]]
    print(f"Checking filing history for {len(needs_check)} recovered "
          "(non-Ritter-verified) companies.")

    earliest_by_idx = {}
    for i, (idx, row) in enumerate(needs_check.iterrows()):
        earliest = earliest_filing_date(row["cik"])
        earliest_by_idx[idx] = earliest
        if earliest and earliest < WINDOW_START:
            print(f"  OLD: {row['company_name']!r}, earliest filing {earliest}")
        if (i + 1) % 50 == 0:
            print(f"{i + 1}/{len(needs_check)} checked")
        time.sleep(0.15)

    df["earliest_filing_date"] = df.index.map(earliest_by_idx)
    df["likely_pre_existing"] = df["earliest_filing_date"].apply(
        lambda d: pd.notna(d) and d < WINDOW_START
    )

    clean = df[~df["likely_pre_existing"]].drop(columns=["has_ipo_date"])
    flagged = df[df["likely_pre_existing"]].drop(columns=["has_ipo_date"])

    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(CLEAN_PATH, index=False)
    flagged.to_csv(FLAGGED_PATH, index=False)

    print(f"\n{len(clean)} companies confirmed as genuine post-2011 filers, "
          f"written to {CLEAN_PATH}")
    print(f"{len(flagged)} flagged as likely pre-existing (reverse merger "
          f"or rename), written to {FLAGGED_PATH}. Don't just discard that "
          "file, skim it, some may still be legitimate edge cases.")
