"""
Refresh pipeline_features.csv and patent_features.csv against the
current 375-company roster. Both files still carry rows for Dynamic
Nutra Enterprises and GridIron BioNutrients (removed as scope
violations since these were last built), same pattern as script 25.

Run with: python scripts/40_refresh_feature_files.py
"""

from pathlib import Path

import pandas as pd

ROSTER_PATH = Path("data/processed/final_roster.csv")
PIPELINE_PATH = Path("data/processed/pipeline_features.csv")
PATENT_PATH = Path("data/processed/patent_features.csv")


def filter_to_roster(path: Path, valid_ciks: set):
    if not path.exists():
        print(f"{path} not found, skipping.")
        return
    df = pd.read_csv(path, dtype={"cik": str})
    df["cik"] = df["cik"].str.zfill(10)
    before = len(df)
    filtered = df[df["cik"].isin(valid_ciks)]
    dropped = before - len(filtered)
    filtered.to_csv(path, index=False)
    print(f"{path.name}: {before} -> {len(filtered)} rows ({dropped} stale rows dropped).")


if __name__ == "__main__":
    roster = pd.read_csv(ROSTER_PATH, dtype={"cik": str})
    roster["cik"] = roster["cik"].str.zfill(10)
    valid_ciks = set(roster["cik"])
    print(f"Current roster: {len(valid_ciks)} companies.\n")
    filter_to_roster(PIPELINE_PATH, valid_ciks)
    filter_to_roster(PATENT_PATH, valid_ciks)
