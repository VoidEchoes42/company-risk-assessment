"""
Step 4.1i: Pre-sort roster_clean.csv before the manual therapeutics skim,
no network calls, pure local filtering.

Two cuts:
  1. SIC 2835 = "In Vitro and In Vivo Diagnostic Substances" by SEC's own
     classification. Not a judgment call, these are diagnostics companies,
     auto-excluded per Step 1's scope.
  2. Company names containing an obvious giveaway word (Diagnostics,
     Imaging, Laboratories, Devices, CRO, Contract Research) get pulled
     into a "likely non-therapeutics" pile for a quick confirm rather than
     a full read, and everyone else lands in the pile that actually needs
     the real business-description skim.

This doesn't touch the network or make any final exclusion decision on
its own for the name-flagged group, it just shrinks what you have to
read carefully.

Run with: python scripts/11_presort_for_manual_skim.py

Input:  data/processed/roster_clean.csv
Output: data/processed/excluded_sic_diagnostics.csv   (auto-excluded, SIC 2835)
        data/processed/review_name_flagged.csv        (quick confirm only)
        data/processed/review_full_read.csv            (the real skim work)
"""

import re
from pathlib import Path

import pandas as pd

IN_PATH = Path("data/processed/roster_clean.csv")
SIC_OUT = Path("data/processed/excluded_sic_diagnostics.csv")
NAME_FLAGGED_OUT = Path("data/processed/review_name_flagged.csv")
FULL_READ_OUT = Path("data/processed/review_full_read.csv")

NAME_GIVEAWAYS = [
    "diagnostic", "imaging", "laborator", "device", " cro", "contract research",
]


def name_is_flagged(name: str) -> bool:
    n = f" {str(name).lower()} "
    return any(kw in n for kw in NAME_GIVEAWAYS)


if __name__ == "__main__":
    df = pd.read_csv(IN_PATH, dtype={"cik": str, "sic": str})
    print(f"Starting from {len(df)} companies.")

    sic_diagnostics = df[df["sic"] == "2835"]
    remaining = df[df["sic"] != "2835"]
    print(f"{len(sic_diagnostics)} excluded by SIC 2835 (diagnostics, no "
          "reading needed).")

    name_flagged_mask = remaining["company_name"].apply(name_is_flagged)
    name_flagged = remaining[name_flagged_mask]
    full_read = remaining[~name_flagged_mask]

    SIC_OUT.parent.mkdir(parents=True, exist_ok=True)
    sic_diagnostics.to_csv(SIC_OUT, index=False)
    name_flagged.to_csv(NAME_FLAGGED_OUT, index=False)
    full_read.to_csv(FULL_READ_OUT, index=False)

    print(f"{len(name_flagged)} flagged by name for a quick confirm "
          f"(written to {NAME_FLAGGED_OUT}).")
    print(f"{len(full_read)} left needing the real business-description "
          f"skim (written to {FULL_READ_OUT}).")
