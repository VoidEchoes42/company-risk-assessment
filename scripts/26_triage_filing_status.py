"""
Step 4.3a: Triage every company by current SEC filing status, the first
cut toward outcome labels. Not a final label on its own, splits 377
companies into groups that need different amounts of further digging,
rather than treating all 377 identically.

Three signals checked per company, from the SEC submissions API's
"recent" filings section (deliberately not the full paginated history
this time, we only care about RECENT activity near the Dec 31 2025
cutoff, so the recent section alone is enough and much faster):

  - latest_periodic_filing: most recent 10-K/10-K-A/10-Q/10-Q-A date.
    Recent means still actively reporting.
  - deregistration_date: earliest Form 15-12B/15-12G, the company's own
    filing to formally stop being a reporting company.
  - form25_date: earliest Form 25/25-NSE, the exchange's own notice of
    delisting.

Bucketed into:
  actively_filing:  recent periodic filing, no deregistration/delisting
                     signal. Presumptively still around, needs the
                     zombie check and clinical-advancement check later,
                     not yet a final "favorable" label.
  deregistered_or_delisted: formal stop signal found. Something
                     happened, acquisition or failure, needs digging
                     into 8-Ks and proxy statements to tell which.
  stalled_filing:   stopped filing periodics without any formal
                     deregistration/delisting signal. Unusual, and
                     worth its own look rather than assuming either way.

Run with: python scripts/26_triage_filing_status.py

Input:  data/processed/final_roster.csv
Output: data/processed/outcome_triage.csv
"""

import time
from pathlib import Path

import pandas as pd
import requests

ROSTER_PATH = Path("data/processed/final_roster.csv")
OUT_PATH = Path("data/processed/outcome_triage.csv")

CUTOFF_DATE = "2025-12-31"
RECENT_WINDOW_DAYS = 455  # about 15 months, covers one annual + a missed quarter

PERIODIC_FORMS = {"10-K", "10-K/A", "10-Q", "10-Q/A"}
DEREGISTRATION_FORMS = {"15-12B", "15-12G", "15-12B/A", "15-12G/A"}
DELISTING_FORMS = {"25", "25-NSE"}

HEADERS = {
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json",
}


def get_filing_status(cik10: str) -> dict:
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return {"latest_periodic_filing": None, "deregistration_date": None, "form25_date": None}

    data = resp.json()
    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])

    periodic_dates = [d for f, d in zip(forms, dates) if f in PERIODIC_FORMS]
    dereg_dates = [d for f, d in zip(forms, dates) if f in DEREGISTRATION_FORMS]
    delist_dates = [d for f, d in zip(forms, dates) if f in DELISTING_FORMS]

    return {
        "latest_periodic_filing": max(periodic_dates) if periodic_dates else None,
        "deregistration_date": min(dereg_dates) if dereg_dates else None,
        "form25_date": min(delist_dates) if delist_dates else None,
    }


def classify(status: dict) -> str:
    if status["deregistration_date"] or status["form25_date"]:
        return "deregistered_or_delisted"

    latest = status["latest_periodic_filing"]
    if latest:
        cutoff_ts = pd.to_datetime(CUTOFF_DATE)
        latest_ts = pd.to_datetime(latest)
        if (cutoff_ts - latest_ts).days <= RECENT_WINDOW_DAYS:
            return "actively_filing"

    return "stalled_filing"


if __name__ == "__main__":
    roster = pd.read_csv(ROSTER_PATH, dtype={"cik": str})
    roster["cik"] = roster["cik"].str.zfill(10)
    print(f"Checking current filing status for {len(roster)} companies.")

    rows = []
    for i, row in roster.iterrows():
        status = get_filing_status(row["cik"])
        bucket = classify(status)
        rows.append({
            "company_name": row["company_name"], "cik": row["cik"],
            "bucket": bucket, **status,
        })
        if (i + 1) % 25 == 0:
            counts = pd.Series([r["bucket"] for r in rows]).value_counts().to_dict()
            print(f"{i + 1}/{len(roster)} checked, {counts}")
        time.sleep(0.15)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUT_PATH, index=False)

    print(f"\nWritten to {OUT_PATH}.")
    print(out_df["bucket"].value_counts())
    print("\nNext: deregistered_or_delisted and stalled_filing need the "
          "acquisition-vs-bankruptcy digging (8-Ks, proxy statements). "
          "actively_filing companies get the zombie check and clinical-"
          "advancement check next, don't assume they're all 'favorable' yet.")
