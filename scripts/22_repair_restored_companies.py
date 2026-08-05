"""
Fix for the column-loss bug in script 21: restored companies only had
company_name/cik/reason available (that's all scope_violations_removed.csv
ever stored), so gluing them back onto the 14-column roster left ipo_date,
classification, sic, s1_url, and everything else blank. This rebuilds
those specific columns for exactly the restored rows, from sources that
still have the real data:

  classification, s1_url, s1_filing_date  <- business_summaries_updated.csv
  sic, sic_description                    <- SEC EDGAR (re-derived live)
  ipo_date                                <- same 424B-then-S1 logic as
                                              script 17, since these
                                              companies never got a
                                              real backfill the first
                                              time (they were wrongly
                                              excluded before script 17
                                              even mattered for them)

ticker and founding_year are NOT rebuilt here. They originate from
Ritter's file specifically and aren't reliably recoverable by CIK alone.
This is a pre-existing, already-accepted gap for any company that came
through the recovered (non-Ritter-verified) path elsewhere in the
roster too, not a new problem introduced by this fix.

Run with: python scripts/22_repair_restored_companies.py

Input:  data/processed/final_roster.csv
        data/processed/business_summaries_updated.csv
Output: data/processed/final_roster.csv (overwritten, gaps filled for
        the restored rows only, everything else untouched)
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


def get_sic(cik10: str):
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return None, None
    data = resp.json()
    return data.get("sic"), data.get("sicDescription")


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
    return matches[0] if matches else None


if __name__ == "__main__":
    dtype_map = {
        "cik": str, "sic": str, "sic_description": str,
        "classification": str, "s1_url": str, "s1_filing_date": str,
        "ipo_date_source": str,
    }
    roster = pd.read_csv(ROSTER_PATH, dtype=dtype_map)
    roster["cik"] = roster["cik"].str.zfill(10)

    broken_mask = roster["ipo_date"].isna()
    broken = roster[broken_mask]
    print(f"{len(broken)} companies found with missing ipo_date, these are "
          "the ones script 21 restored without their real data. Repairing now.")

    summaries = pd.read_csv(SUMMARIES_PATH, dtype={"cik": str}) if SUMMARIES_PATH.exists() else pd.DataFrame()
    if len(summaries):
        summaries["cik"] = summaries["cik"].str.zfill(10)
        summaries_by_cik = summaries.set_index("cik")

    for idx in broken.index:
        cik10 = roster.at[idx, "cik"]
        name = roster.at[idx, "company_name"]

        if len(summaries) and cik10 in summaries_by_cik.index:
            srow = summaries_by_cik.loc[cik10]
            roster.at[idx, "classification"] = srow.get("classification")
            roster.at[idx, "s1_url"] = srow.get("s1_url")
            roster.at[idx, "s1_filing_date"] = srow.get("s1_filing_date")
            print(f"  {name}: classification/s1_url/s1_filing_date recovered "
                  "from business_summaries_updated.csv")
        else:
            print(f"  {name}: NOT found in business_summaries_updated.csv, "
                  "classification/s1_url stay blank, needs a manual look")

        sic, sic_desc = get_sic(cik10)
        roster.at[idx, "sic"] = sic
        roster.at[idx, "sic_description"] = sic_desc

        prospectus_date = find_prospectus_date(cik10)
        if prospectus_date:
            roster.at[idx, "ipo_date"] = prospectus_date
            roster.at[idx, "ipo_date_source"] = "424b_filing"
        elif len(summaries) and cik10 in summaries_by_cik.index:
            s1_date = summaries_by_cik.loc[cik10].get("s1_filing_date")
            if pd.notna(s1_date):
                roster.at[idx, "ipo_date"] = s1_date
                roster.at[idx, "ipo_date_source"] = "s1_filing_date_proxy"

        time.sleep(0.15)

    still_missing = roster.loc[broken.index, "ipo_date"].isna().sum()
    roster.to_csv(ROSTER_PATH, index=False)

    print(f"\nRepaired {len(broken) - still_missing} of {len(broken)} companies "
          f"with a real ipo_date. {still_missing} still missing one, "
          "these need a manual look before any feature script touches them.")
    print(f"Note: ticker and founding_year were not rebuilt for these rows, "
          "not reliably recoverable by CIK alone, same accepted gap as "
          "other recovered-path companies elsewhere in the roster.")
