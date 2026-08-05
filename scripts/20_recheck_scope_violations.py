"""
Integrity re-check across the whole roster, triggered by a patent-count
outlier (AbbVie showing 943 pre-IPO patents was the tell). Two distinct
problems found, both fixed here:

1. Corporate spinoffs: AbbVie (from Abbott, 2013) and Baxalta (from
   Baxter, 2015) both confirmed as Form 10 / 10-12B spinoff
   registrations, not IPOs, massive established businesses distributed
   to existing shareholders, not venture-backed startups. Any company
   with a Form 10-12B, 10-12B/A, 10-12G, or 10-12G/A anywhere in its
   history gets excluded outright.

2. Old companies whose true IPO predates our window entirely: MannKind
   actually IPO'd in 2004, confirmed by direct search, 11 years before
   the "earliest filing" our scripts 07/08/10 could see. Root cause:
   SEC's submissions API caps the "recent" filings list, and a company
   with enough filing volume (MannKind has over 20 years of 10-Ks,
   10-Qs, 8-Ks, proxies) can have its true early history pushed
   entirely out of that window. This fix follows SEC's own pagination
   links (filings.files) to see the FULL history, not just the capped
   recent section, closing the same blind spot for any other company
   quietly affected the same way.

Run with: python scripts/20_recheck_scope_violations.py

Input:  data/processed/final_roster.csv
Output: data/processed/final_roster.csv (overwritten, violations removed)
        data/processed/scope_violations_removed.csv (what got removed and why)
"""

import time
from pathlib import Path

import pandas as pd
import requests

ROSTER_PATH = Path("data/processed/final_roster.csv")
REMOVED_PATH = Path("data/processed/scope_violations_removed.csv")

WINDOW_START = "2011-01-01"
SPINOFF_FORMS = {"10-12B", "10-12B/A", "10-12G", "10-12G/A"}
EXCLUDE_FROM_DATE_CHECK = {"D", "D/A", "REGDEX", "REGDEX/A"}

HEADERS = {
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json",
}


def get_full_filing_history(cik10: str):
    """All filings for a company, following SEC's own pagination into
    older filing files when the 'recent' section is capped, rather than
    trusting the recent section alone."""
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return [], []

    data = resp.json()
    recent = data.get("filings", {}).get("recent", {})
    forms = list(recent.get("form", []))
    dates = list(recent.get("filingDate", []))

    for file_info in data.get("filings", {}).get("files", []):
        file_name = file_info.get("name")
        if not file_name:
            continue
        older_url = f"https://data.sec.gov/submissions/{file_name}"
        older_resp = requests.get(older_url, headers=HEADERS, timeout=30)
        if older_resp.status_code == 200:
            older_data = older_resp.json()
            forms.extend(older_data.get("form", []))
            dates.extend(older_data.get("filingDate", []))
        time.sleep(0.15)

    return forms, dates


def check_company(cik10: str) -> dict:
    forms, dates = get_full_filing_history(cik10)
    has_spinoff_form = any(f in SPINOFF_FORMS for f in forms)

    substantive_dates = [d for f, d in zip(forms, dates) if f not in EXCLUDE_FROM_DATE_CHECK]
    true_earliest = min(substantive_dates) if substantive_dates else None
    predates_window = bool(true_earliest) and true_earliest < WINDOW_START

    return {
        "has_spinoff_form": has_spinoff_form,
        "true_earliest_filing_date": true_earliest,
        "predates_window": predates_window,
    }


if __name__ == "__main__":
    roster = pd.read_csv(ROSTER_PATH, dtype={"cik": str})
    roster["cik"] = roster["cik"].str.zfill(10)
    print(f"Re-checking full filing history for {len(roster)} companies, "
          "this follows SEC's own pagination, expect this to be slower "
          "than a single-page lookup, plausibly 15-20+ minutes.")

    violations = []
    for i, row in roster.iterrows():
        result = check_company(row["cik"])
        reason = None
        if result["has_spinoff_form"]:
            reason = "spinoff (Form 10-12B/G)"
        elif result["predates_window"]:
            reason = f"predates window (true earliest: {result['true_earliest_filing_date']})"

        if reason:
            violations.append({
                "company_name": row["company_name"], "cik": row["cik"], "reason": reason,
            })
            print(f"  VIOLATION: {row['company_name']!r}, {reason}")

        if (i + 1) % 25 == 0:
            print(f"{i + 1}/{len(roster)} checked, {len(violations)} violations found so far")

    violation_ciks = {v["cik"] for v in violations}
    clean = roster[~roster["cik"].isin(violation_ciks)].copy()

    clean.to_csv(ROSTER_PATH, index=False)
    pd.DataFrame(violations).to_csv(REMOVED_PATH, index=False)

    print(f"\n{len(violations)} scope violations removed, written to {REMOVED_PATH}.")
    print(f"{len(clean)} companies remain in {ROSTER_PATH}.")
    print("Rerun scripts 15 (pipeline) and 19 (patents) for the removed "
          "companies' rows to naturally disappear from those files too, "
          "or just filter them out by CIK before modeling.")
