"""
Step 4.3h: Two things before diving into 45 new individual researches.

1. Catch self-evident failures mechanically. A company whose current
   registered name contains "Liquidation," "Wind-down," "Winddown," or
   "Unwind" is not ambiguous, that is the company's own official record
   stating what happened. No search needed, no judgment call.

2. Cross-reference every flagged company (from script 35's full-roster
   check) against its CURRENT exit_reason bucket. A name change matters
   very differently depending on where a company already sits: one
   already correctly labeled bankruptcy needs nothing, one sitting in
   "unclear" or "actively_filing" is exactly where a wrong label would
   actually hurt, and that is where real research effort should go.

This does not resolve every company, deliberately, it prioritizes.

Run with: python scripts/36_triage_new_divergence_finds.py

Input:  data/processed/full_name_divergence_check.csv
        data/processed/exit_reasons.csv
        data/processed/outcome_triage.csv
Output: data/processed/divergence_priority.csv
"""

from pathlib import Path

import pandas as pd

DIVERGENCE_PATH = Path("data/processed/full_name_divergence_check.csv")
EXIT_PATH = Path("data/processed/exit_reasons.csv")
TRIAGE_PATH = Path("data/processed/outcome_triage.csv")
OUT_PATH = Path("data/processed/divergence_priority.csv")

SELF_EVIDENT_KEYWORDS = ["LIQUIDATION", "WIND-DOWN", "WINDDOWN", "UNWIND", "DISSOLUTION"]

# Companies already resolved through individual research in the earlier
# acquisition-only pass, re-appearing here is expected, not new work.
ALREADY_RESOLVED = {
    "Conatus Pharmaceuticals Inc", "Regado Biosciences Inc", "Axovant Sciences Ltd.",
    "Ophthotech Corp.", "CATABASIS PHARMACEUTICALS INC", "Versartis, Inc.",
    "ProNAi Therapeutics Inc", "Spring Bank Pharmaceuticals, Inc.",
    "Eleven Biotherapeutics, Inc.", "Carbylan Therapeutics, Inc.",
    "Aduro Biotech, Inc.", "Recro Pharma, Inc.", "Acucela Inc",
}


def check_self_evident(current_name: str) -> str:
    if not current_name:
        return None
    upper = str(current_name).upper()
    for kw in SELF_EVIDENT_KEYWORDS:
        if kw in upper:
            return kw
    return None


if __name__ == "__main__":
    divergence = pd.read_csv(DIVERGENCE_PATH, dtype={"cik": str})
    exits = pd.read_csv(EXIT_PATH, dtype={"cik": str})
    triage = pd.read_csv(TRIAGE_PATH, dtype={"cik": str})

    flagged = divergence[divergence["flagged_for_review"] == True].copy()
    flagged["cik"] = flagged["cik"].str.zfill(10)
    exits["cik"] = exits["cik"].str.zfill(10)
    triage["cik"] = triage["cik"].str.zfill(10)

    print(f"{len(flagged)} companies flagged for review.")

    flagged["already_resolved"] = flagged["company_name"].isin(ALREADY_RESOLVED)
    flagged["self_evident_keyword"] = flagged["current_registered_name"].apply(check_self_evident)

    # Merge in current bucket status, from exit_reasons where available
    # (companies that stopped filing), else from outcome_triage (covers
    # actively_filing companies too).
    exit_lookup = exits.set_index("cik")["exit_reason"].to_dict()
    triage_lookup = triage.set_index("cik")["bucket"].to_dict()

    def get_current_status(cik10):
        if cik10 in exit_lookup:
            return exit_lookup[cik10]
        return triage_lookup.get(cik10, "not found")

    flagged["current_status"] = flagged["cik"].apply(get_current_status)

    new_and_unresolved = flagged[
        (~flagged["already_resolved"]) & (flagged["self_evident_keyword"].isna())
    ]

    print(f"\n{flagged['already_resolved'].sum()} already resolved from before.")
    print(f"{flagged['self_evident_keyword'].notna().sum()} self-evident from the "
          f"registered name alone (no research needed):")
    print(flagged[flagged["self_evident_keyword"].notna()][
        ["company_name", "current_registered_name", "current_status"]
    ].to_string(index=False))

    print(f"\n{len(new_and_unresolved)} genuinely new and unresolved, "
          "grouped by where they currently sit:")
    print(new_and_unresolved["current_status"].value_counts())

    print("\nFull breakdown by current_status (this is what determines priority):")
    for status, group in new_and_unresolved.groupby("current_status"):
        print(f"\n  {status} ({len(group)}):")
        for name in group["company_name"]:
            print(f"    {name}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    flagged.to_csv(OUT_PATH, index=False)
    print(f"\nFull detail written to {OUT_PATH}.")
    print("\nPriority recommendation: 'unclear' and 'actively_filing' first, "
          "those are where a wrong label actually costs something. "
          "'bankruptcy' and 'likely_failure_delisted' already have a "
          "reasonable label regardless of the name change.")
