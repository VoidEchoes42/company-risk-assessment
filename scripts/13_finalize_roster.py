"""
Step 4.1, closing out: merge your manual classification back into the
full roster (recovering ipo_date, ticker, founding_year, sic, etc, which
aren't in business_summaries_updated.csv), then produce the final
therapeutics-only roster.

Handles a real gotcha found in your actual uploaded file: opening a CSV
with ID-like columns (CIK) in Excel and saving it strips leading zeros,
0001526119 becomes 1526119. Invisible in Excel, but silently breaks a
merge against roster_clean.csv, which still has the zero-padded version.
Both sides get re-zero-padded before merging here specifically because
of that.

UNCLEAR (32 companies in your file) are NOT included in the final
therapeutics roster, and not silently discarded either, they get their
own output file. Dropping them without a decision risks a selection
bias if whatever made them hard to classify (thin S-1 language, unusual
business model) correlates with anything about outcome. Recommended:
spend 15-20 minutes resolving just those 32 using unclear_for_review.csv
before treating the roster as final, it's a much smaller task than the
464 you just finished.

Run with: python scripts/13_finalize_roster.py

Input:  data/processed/business_summaries_updated.csv
        data/processed/roster_clean.csv
Output: data/processed/final_roster.csv       (therapeutics only, trust this)
        data/processed/unclear_for_review.csv (the 32 needing a second look)
        data/processed/excluded_non_therapeutics.csv (everything else, for reference)
"""

from pathlib import Path

import pandas as pd

SUMMARIES_PATH = Path("data/processed/business_summaries_updated.csv")
ROSTER_PATH = Path("data/processed/roster_clean.csv")
FINAL_PATH = Path("data/processed/final_roster.csv")
UNCLEAR_PATH = Path("data/processed/unclear_for_review.csv")
EXCLUDED_PATH = Path("data/processed/excluded_non_therapeutics.csv")

VALID_CATEGORIES = {
    "THERAPEUTICS", "DIAGNOSTICS", "CRO", "TOOLS",
    "DEVICES", "SERVICES", "UNCLEAR",
}

# Columns from roster_clean.csv worth keeping in the final working file.
# The matching-diagnostic columns (name_match_score, source,
# earliest_filing_date, likely_pre_existing) did their job getting the
# roster right, they're not needed going forward, so they're left out
# here to keep final_roster.csv focused on what Step 4.2 actually uses.
KEEP_ROSTER_COLS = [
    "cik", "ipo_date", "ticker", "founding_year", "ipo_year",
    "sic", "sic_description",
]


if __name__ == "__main__":
    summaries = pd.read_csv(SUMMARIES_PATH, dtype={"cik": str})
    roster = pd.read_csv(ROSTER_PATH, dtype={"cik": str})

    # The fix for the Excel leading-zero problem: force both sides back
    # to the same 10-digit zero-padded format before merging.
    summaries["cik"] = summaries["cik"].str.zfill(10)
    roster["cik"] = roster["cik"].str.zfill(10)

    print(f"{len(summaries)} classified companies, {len(roster)} rows in "
          "the full roster.")

    # Validate classification values before trusting them.
    normalized = summaries["classification"].astype(str).str.strip().str.upper()
    invalid = summaries[~normalized.isin(VALID_CATEGORIES)]
    if len(invalid):
        print(f"\n{len(invalid)} rows have an unrecognized classification "
              f"value, fix these by hand before continuing:")
        print(invalid[["company_name", "classification"]].to_string(index=False))
        raise SystemExit(1)
    summaries["classification"] = normalized
    print("All classification values are valid.")

    merged = summaries.merge(
        roster[KEEP_ROSTER_COLS], on="cik", how="left", indicator=True
    )
    unmatched = merged[merged["_merge"] == "left_only"]
    if len(unmatched):
        print(f"\n{len(unmatched)} companies didn't find a match in "
              f"roster_clean.csv, this shouldn't happen since both files "
              f"trace back to the same roster, investigate before trusting "
              f"the output:")
        print(unmatched[["company_name", "cik"]].to_string(index=False))
    merged = merged.drop(columns=["_merge"])

    print("\nClassification breakdown:")
    print(summaries["classification"].value_counts())

    final = merged[merged["classification"] == "THERAPEUTICS"].copy()
    unclear = merged[merged["classification"] == "UNCLEAR"].copy()
    excluded = merged[
        ~merged["classification"].isin(["THERAPEUTICS", "UNCLEAR"])
    ].copy()

    FINAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    final.to_csv(FINAL_PATH, index=False)
    unclear.to_csv(UNCLEAR_PATH, index=False)
    excluded.to_csv(EXCLUDED_PATH, index=False)

    print(f"\n{len(final)} companies in the final therapeutics roster, "
          f"written to {FINAL_PATH}. This is your actual study population "
          "going forward.")
    print(f"{len(unclear)} set aside as unresolved, written to "
          f"{UNCLEAR_PATH}. Worth a second look before calling the roster "
          "final, s1_url is right there for each one.")
    print(f"{len(excluded)} confirmed non-therapeutics, written to "
          f"{EXCLUDED_PATH} for reference, not part of the study.")
