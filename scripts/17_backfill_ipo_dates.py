"""
Fix for the missing-ipo_date bug traced to script 05: companies recovered
via the EDGAR cross-check path were never given an ipo_date, only
company_name, cik, sic, and source. That's roughly 355 of 472 roster
companies. This backfills it using each company's own 424B4 filing
(the final prospectus, filed right when an IPO actually prices), which
is a tight, direct proxy for the real IPO date, tighter than the S-1
itself, which can be filed months before the deal actually closes.

Falls back to s1_filing_date (already on hand from the business summary
work) only if no 424B-family filing is found, flagged explicitly via
ipo_date_source so you always know which rows are precise vs
approximate.

Run with: python scripts/17_backfill_ipo_dates.py

Input:  data/processed/final_roster.csv
        data/processed/business_summaries_updated.csv (for the s1_filing_date fallback)
Output: data/processed/final_roster.csv (overwritten, ipo_date filled in
        + new ipo_date_source column)
"""

import time
from pathlib import Path

import pandas as pd
import requests

ROSTER_PATH = Path("data/processed/final_roster.csv")
SUMMARIES_PATH = Path("data/processed/business_summaries_updated.csv")

PROSPECTUS_FORMS = ["424B4", "424B1", "424B2", "424B3"]

HEADERS = {
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json",
}


def find_prospectus_date(cik10: str):
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return None
    data = resp.json()
    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    matches = sorted(d for f, d in zip(forms, dates) if f in PROSPECTUS_FORMS)
    return matches[0] if matches else None  # earliest 424B filing


if __name__ == "__main__":
    roster = pd.read_csv(ROSTER_PATH, dtype={"cik": str})
    roster["cik"] = roster["cik"].str.zfill(10)
    roster["ipo_date"] = pd.to_datetime(roster["ipo_date"], errors="coerce")

    missing_mask = roster["ipo_date"].isna()
    missing_count = missing_mask.sum()
    print(f"{missing_count} of {len(roster)} companies are missing ipo_date, backfilling now.")

    roster["ipo_date_source"] = roster["ipo_date"].apply(
        lambda d: "ritter_verified" if pd.notna(d) else None
    )

    # s1_filing_date fallback, already on hand, no network needed for this part.
    if SUMMARIES_PATH.exists():
        summaries = pd.read_csv(SUMMARIES_PATH, dtype={"cik": str})
        summaries["cik"] = summaries["cik"].str.zfill(10)
        s1_dates = dict(zip(summaries["cik"], summaries["s1_filing_date"]))
    else:
        s1_dates = {}

    filled_424b, filled_s1_fallback, still_missing = 0, 0, 0
    for idx in roster[missing_mask].index:
        cik10 = roster.at[idx, "cik"]
        prospectus_date = find_prospectus_date(cik10)

        if prospectus_date:
            roster.at[idx, "ipo_date"] = pd.to_datetime(prospectus_date)
            roster.at[idx, "ipo_date_source"] = "424b_filing"
            filled_424b += 1
        elif cik10 in s1_dates and pd.notna(s1_dates[cik10]):
            roster.at[idx, "ipo_date"] = pd.to_datetime(s1_dates[cik10])
            roster.at[idx, "ipo_date_source"] = "s1_filing_date_proxy"
            filled_s1_fallback += 1
        else:
            still_missing += 1

        done = filled_424b + filled_s1_fallback + still_missing
        if done % 25 == 0:
            print(f"{done}/{missing_count} processed")
        time.sleep(0.15)

    roster.to_csv(ROSTER_PATH, index=False)

    print(f"\nBackfilled {filled_424b} from actual 424B prospectus filings (precise).")
    print(f"Backfilled {filled_s1_fallback} from S-1 filing date (approximate, slightly "
          "conservative, biases toward excluding borderline trials rather than leaking them).")
    print(f"{still_missing} still missing, no prospectus or S-1 date found at all, "
          "these need a manual look.")
    print(f"\n{ROSTER_PATH} overwritten with the fix. Rerun "
          "scripts/15_fetch_pipeline_features.py now that ipo_date is complete.")
