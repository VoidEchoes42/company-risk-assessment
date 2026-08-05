"""
Fix for a real bug in script 26: it treated any deregistration or Form
25 signal as an automatic, unconditional "this company stopped being
public," when Form 25 specifically means "removed from listing on this
exchange," which can happen for partial or technical reasons (a move
between exchanges, deregistering a specific security class like
warrants) while the company keeps trading and filing completely
normally elsewhere. 18 of 189 companies showed this contradiction, a
periodic filing dated well after the supposed stop signal, several of
them (Viking Therapeutics, Zymeworks, Amneal Pharmaceuticals) are real,
currently-trading companies, not failures.

Corrected rule: compare the stop signal against the latest periodic
filing directly. If the periodic filing comes meaningfully later, that
is stronger evidence than the stop signal, and the company gets
reclassified based on filing recency instead, same as any other
company. No new network calls, this reprocesses data already collected.

Run with: python scripts/27_fix_triage_priority.py

Input:  data/processed/outcome_triage.csv
Output: data/processed/outcome_triage.csv (overwritten, bucket column corrected)
"""

from pathlib import Path

import pandas as pd

TRIAGE_PATH = Path("data/processed/outcome_triage.csv")

CUTOFF_DATE = "2025-12-31"
RECENT_WINDOW_DAYS = 455
CONTRADICTION_THRESHOLD_DAYS = 180


def reclassify(row) -> str:
    latest_periodic = pd.to_datetime(row["latest_periodic_filing"], errors="coerce")

    stop_dates = [
        pd.to_datetime(row["deregistration_date"], errors="coerce"),
        pd.to_datetime(row["form25_date"], errors="coerce"),
    ]
    stop_dates = [d for d in stop_dates if pd.notna(d)]
    stop_date = min(stop_dates) if stop_dates else None

    cutoff_ts = pd.to_datetime(CUTOFF_DATE)
    is_recent = pd.notna(latest_periodic) and (cutoff_ts - latest_periodic).days <= RECENT_WINDOW_DAYS

    if stop_date is not None:
        contradicted = (
            pd.notna(latest_periodic)
            and (latest_periodic - stop_date).days > CONTRADICTION_THRESHOLD_DAYS
        )
        if not contradicted:
            return "deregistered_or_delisted"
        # else: fall through, treat purely on filing recency instead

    return "actively_filing" if is_recent else "stalled_filing"


if __name__ == "__main__":
    df = pd.read_csv(TRIAGE_PATH)
    before = df["bucket"].value_counts().to_dict()

    df["old_bucket"] = df["bucket"]
    df["bucket"] = df.apply(reclassify, axis=1)

    changed = df[df["old_bucket"] != df["bucket"]]
    print(f"{len(changed)} companies reclassified:")
    print(changed[["company_name", "old_bucket", "bucket"]].to_string(index=False))

    df = df.drop(columns=["old_bucket"])
    df.to_csv(TRIAGE_PATH, index=False)

    print(f"\nBefore: {before}")
    print(f"After:  {df['bucket'].value_counts().to_dict()}")
