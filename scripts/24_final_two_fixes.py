"""
Closes out the roster-integrity work: the last 2 companies with a
missing ipo_date, each resolved individually against a confirmed
primary source, same as FibroGen, bluebird bio, and Alkermes before them.

1. PTC Therapeutics Inc: real IPO priced June 20, 2013, closed June 25,
   2013 (J.P. Morgan and Credit Suisse as bookrunners), already
   confirmed earlier in this project during the withdrawn-S-1
   investigation. Setting the date directly.

2. HORIZON PHARMA, INC.: real IPO priced and closed July 28, 2011,
   confirmed directly from its own SEC filings. That is before 2012,
   outside Step 1's declared 2012-2019 window, not merely a missing
   date. It slipped through the predates-window check because that
   check used a 2011-01-01 buffer for filing lag, and July 2011 falls
   just after that cutoff despite still being pre-window. Removed
   rather than backfilled.

Run with: python scripts/24_final_two_fixes.py

Input:  data/processed/final_roster.csv
        data/processed/scope_violations_removed.csv
Output: both overwritten with these two fixes applied
"""

from pathlib import Path

import pandas as pd

ROSTER_PATH = Path("data/processed/final_roster.csv")
REMOVED_PATH = Path("data/processed/scope_violations_removed.csv")

PTC_IPO_DATE = "2013-06-25"
HORIZON_REASON = ("predates window (real IPO July 28, 2011, before the 2012-2019 "
                   "study window; missed by the predates-window check's "
                   "2011-01-01 buffer date), confirmed manually")

if __name__ == "__main__":
    dtype_map = {"cik": str, "sic": str, "sic_description": str,
                 "classification": str, "s1_url": str, "s1_filing_date": str,
                 "ipo_date_source": str}
    roster = pd.read_csv(ROSTER_PATH, dtype=dtype_map)
    removed = pd.read_csv(REMOVED_PATH, dtype={"cik": str})

    ptc_mask = roster["company_name"].str.contains("PTC Therapeutics", case=False, na=False)
    roster.loc[ptc_mask, "ipo_date"] = PTC_IPO_DATE
    roster.loc[ptc_mask, "ipo_date_source"] = "manual_verified"
    print(f"Set PTC Therapeutics ipo_date to {PTC_IPO_DATE}.")

    horizon_mask = roster["company_name"].str.contains("HORIZON PHARMA", case=False, na=False)
    horizon_rows = roster[horizon_mask]
    if len(horizon_rows):
        new_removal = horizon_rows[["company_name", "cik"]].copy()
        new_removal["reason"] = HORIZON_REASON
        removed = pd.concat([removed, new_removal], ignore_index=True)
        roster = roster[~horizon_mask]
        print(f"Removed Horizon Pharma: {HORIZON_REASON}")

    roster.to_csv(ROSTER_PATH, index=False)
    removed.to_csv(REMOVED_PATH, index=False)

    still_missing = roster["ipo_date"].isna().sum()
    print(f"\n{len(roster)} companies remain in {ROSTER_PATH}.")
    print(f"{still_missing} still missing ipo_date (should be 0).")
    print(f"{len(removed)} total companies in {REMOVED_PATH}.")
