"""
Verification pass, not a reclassification: for every company script 30
just moved into 'acquisition' via Item 2.01, check whether that date
actually lines up with when the company stopped filing normally. If
the Item 2.01 happened years before the company's last periodic filing,
that's a sign it was a routine mid-life asset transaction, not the
company itself being acquired, and the reclassification is probably
wrong, worth an individual look rather than trusting it by default.

Flags anything where the gap exceeds 18 months as suspicious. Doesn't
change any labels itself, deliberately, this is a check, not a fix.

Run with: python scripts/31_verify_acquisition_timing.py

Input:  data/processed/exit_reasons.csv
        data/processed/outcome_triage.csv
Output: prints flagged companies directly, writes no files
"""

from pathlib import Path

import pandas as pd

EXIT_PATH = Path("data/processed/exit_reasons.csv")
TRIAGE_PATH = Path("data/processed/outcome_triage.csv")

SUSPICIOUS_GAP_DAYS = 545  # about 18 months

if __name__ == "__main__":
    exits = pd.read_csv(EXIT_PATH, dtype={"cik": str})
    triage = pd.read_csv(TRIAGE_PATH, dtype={"cik": str})
    exits["cik"] = exits["cik"].str.zfill(10)
    triage["cik"] = triage["cik"].str.zfill(10)

    merged = exits.merge(
        triage[["cik", "latest_periodic_filing"]], on="cik", how="left"
    )

    via_2_01 = merged[merged["acquisition_completion_date"].notna()]
    print(f"Checking {len(via_2_01)} companies reclassified via Item 2.01.")

    completion = pd.to_datetime(via_2_01["acquisition_completion_date"])
    last_periodic = pd.to_datetime(via_2_01["latest_periodic_filing"])
    gap_days = (last_periodic - completion).dt.days

    suspicious = via_2_01[gap_days.abs() > SUSPICIOUS_GAP_DAYS].copy()
    suspicious["gap_days"] = gap_days[gap_days.abs() > SUSPICIOUS_GAP_DAYS]

    print(f"\n{len(suspicious)} look suspicious (Item 2.01 date and last "
          f"periodic filing more than {SUSPICIOUS_GAP_DAYS} days apart):")
    if len(suspicious):
        print(suspicious[["company_name", "acquisition_completion_date",
                           "latest_periodic_filing", "gap_days"]].to_string(index=False))
    else:
        print("None found, all reclassifications look timing-consistent.")

    clean = via_2_01[gap_days.abs() <= SUSPICIOUS_GAP_DAYS]
    print(f"\n{len(clean)} look timing-consistent, reasonable to trust as-is.")
