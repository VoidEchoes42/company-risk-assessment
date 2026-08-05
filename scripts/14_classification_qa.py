"""
Step 4.1, quality check: scan the classification you did by hand for
likely errors, using strong keyword signals as a heuristic, not a
verdict. Manual classification across 464 rows will always have some
error rate, this just makes the likely errors fast to find instead of
re-reading everything.

Two directions checked:
  1. In excluded_non_therapeutics.csv and unclear_for_review.csv: flag
     rows containing strong "this is a drug developer" language
     (clinical-stage, product candidate, lead candidate, therapeutic
     candidate, drug candidate). These may have been wrongly excluded.
  2. In final_roster.csv: flag rows labeled THERAPEUTICS that contain
     strong "this is NOT a drug developer" language (diagnostic test,
     contract research, on behalf of, medical device, research
     reagents). These may have been wrongly included.

IMPORTANT: a flag here is a candidate for a 10-second human look, not an
automatic correction. Company names matter too, "Spero Therapeutics"
being labeled non-therapeutics is a strong enough tell on its own that
you can probably fix it without even opening the snippet.

Run with: python scripts/14_classification_qa.py

Input (checks whichever of these exist):
  data/processed/excluded_non_therapeutics.csv
  data/processed/unclear_for_review.csv
  data/processed/final_roster.csv
Output: prints flagged rows directly, does not write or change any file
"""

from pathlib import Path

import pandas as pd

FILES_TO_CHECK = {
    "excluded_non_therapeutics.csv": "excluded",
    "unclear_for_review.csv": "unclear",
    "final_roster.csv": "included",
}

# Strong signals a company develops ITS OWN drug. Kept short and
# specific on purpose, a longer list starts catching incidental
# mentions rather than genuine self-description.
THERAPEUTICS_SIGNALS = [
    "clinical-stage", "clinical stage", "product candidate",
    "lead candidate", "therapeutic candidate", "drug candidate",
]

# Strong signals a company is NOT a drug developer, used only against
# rows already labeled THERAPEUTICS, to catch the opposite mistake.
NON_THERAPEUTICS_SIGNALS = [
    "diagnostic test", "diagnostic assay", "contract research",
    "on behalf of", "medical device", "510(k)", "research reagents",
    "sequencing platform",
]


def find_signals(text: str, signal_list: list) -> list:
    t = str(text).lower()
    return [s for s in signal_list if s in t]


def check_file(path: Path, mode: str):
    if not path.exists():
        print(f"(skipping {path.name}, not found)")
        return

    df = pd.read_csv(path)
    if mode in ("excluded", "unclear"):
        df["signals"] = df["summary_snippet"].apply(
            lambda t: find_signals(t, THERAPEUTICS_SIGNALS)
        )
        flagged = df[df["signals"].apply(len) > 0]
        direction = "possibly wrongly excluded (contains drug-developer language)"
    else:
        therapeutics_only = df[df["classification"] == "THERAPEUTICS"]
        therapeutics_only = therapeutics_only.copy()
        therapeutics_only["signals"] = therapeutics_only["summary_snippet"].apply(
            lambda t: find_signals(t, NON_THERAPEUTICS_SIGNALS)
        )
        flagged = therapeutics_only[therapeutics_only["signals"].apply(len) > 0]
        direction = "possibly wrongly included (contains non-therapeutics language)"

    print(f"\n=== {path.name}: {len(flagged)} of {len(df)} flagged, {direction} ===")
    for _, row in flagged.iterrows():
        label = row.get("classification", "?")
        print(f"  {row['company_name']} (labeled {label}), signals: {row['signals']}")


if __name__ == "__main__":
    for filename, mode in FILES_TO_CHECK.items():
        check_file(Path("data/processed") / filename, mode)
    print("\nA flag is a candidate for a quick look, not an automatic "
          "correction. Fix any real errors directly in "
          "business_summaries_updated.csv's classification column, then "
          "rerun scripts/13_finalize_roster.py to regenerate all three "
          "files with the corrections applied.")
