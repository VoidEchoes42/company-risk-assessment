"""
Final targeted cleanup, three specific companies, each individually
confirmed by direct search of primary sources rather than another
mechanical rule:

1. FibroGen Inc: IPO closed November 19, 2014 (confirmed directly from
   FibroGen's own 10-K). A completely standard underwritten IPO,
   Goldman Sachs/Citigroup/Leerink as bookrunners. The automated 424B
   lookup failed on this one for an unconfirmed reason, not worth
   chasing further given the date is independently verified.

2. bluebird bio, Inc: IPO completed June 24, 2013 (confirmed directly
   from bluebird bio's own 10-K and 10-Q). Same situation, standard
   IPO, J.P. Morgan/BofA Merrill Lynch as bookrunners, automated lookup
   failed, manually verified instead.

3. Alkermes plc: CONFIRMED, via direct search, to be a 2011 corporate
   merger (Alkermes Inc. + Elan Drug Technologies, forming a new Irish
   holding company), immediately profitable with $450M+ in annual
   revenue at formation. Not a spinoff (wrong form type to be caught by
   script 20's Form 10 check) and its earliest filings under the new
   entity fall just after the 2011-01-01 cutoff (too late to be caught
   by the predates-window check either). A third distinct mechanism by
   which a non-startup slipped through, removed here by hand since no
   mechanical rule caught it.

Run with: python scripts/23_manual_verified_fixes.py

Input:  data/processed/final_roster.csv
        data/processed/scope_violations_removed.csv
Output: both overwritten with these three fixes applied
"""

from pathlib import Path

import pandas as pd

ROSTER_PATH = Path("data/processed/final_roster.csv")
REMOVED_PATH = Path("data/processed/scope_violations_removed.csv")

MANUAL_IPO_DATES = {
    "FIBROGEN INC": "2014-11-19",
    "bluebird bio, Inc.": "2013-06-24",
}

ALKERMES_NAME_FRAGMENT = "Alkermes"
ALKERMES_REASON = ("corporate merger/reorganization (Alkermes Inc. + Elan Drug "
                    "Technologies -> Alkermes plc, 2011), not an IPO, confirmed manually")


if __name__ == "__main__":
    dtype_map = {"cik": str, "sic": str, "sic_description": str,
                 "classification": str, "s1_url": str, "s1_filing_date": str,
                 "ipo_date_source": str}
    roster = pd.read_csv(ROSTER_PATH, dtype=dtype_map)
    removed = pd.read_csv(REMOVED_PATH, dtype={"cik": str}) if REMOVED_PATH.exists() else pd.DataFrame(
        columns=["company_name", "cik", "reason"]
    )

    # Fix 1 and 2: manually verified IPO dates.
    for name, date in MANUAL_IPO_DATES.items():
        mask = roster["company_name"] == name
        if not mask.any():
            print(f"WARNING: {name!r} not found in roster, nothing to fix.")
            continue
        roster.loc[mask, "ipo_date"] = date
        roster.loc[mask, "ipo_date_source"] = "manual_verified"
        print(f"Set {name!r} ipo_date to {date} (manually verified from its own 10-K/10-Q).")

    # Fix 3: remove Alkermes as a confirmed scope violation.
    alkermes_mask = roster["company_name"].str.contains(
        ALKERMES_NAME_FRAGMENT, case=False, na=False
    )
    alkermes_rows = roster[alkermes_mask]
    if len(alkermes_rows):
        for _, row in alkermes_rows.iterrows():
            print(f"Removing {row['company_name']!r}: {ALKERMES_REASON}")
        new_removal = alkermes_rows[["company_name", "cik"]].copy()
        new_removal["reason"] = ALKERMES_REASON
        removed = pd.concat([removed, new_removal], ignore_index=True)
        roster = roster[~alkermes_mask]
    else:
        print("WARNING: Alkermes not found in roster, nothing to remove.")

    roster.to_csv(ROSTER_PATH, index=False)
    removed.to_csv(REMOVED_PATH, index=False)

    still_missing = roster["ipo_date"].isna().sum()
    print(f"\n{len(roster)} companies remain in {ROSTER_PATH}.")
    print(f"{still_missing} companies still have a missing ipo_date after this "
          "fix, these are the genuinely unresolved ones needing an individual look.")
    print(f"{len(removed)} total companies now in {REMOVED_PATH}.")
