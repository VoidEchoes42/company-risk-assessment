"""
Filter pipeline_features.csv and patent_features.csv down to whatever
CIKs currently exist in final_roster.csv. Both feature files were built
before the scope-violation cleanup (scripts 20-24), so they still carry
rows for every company removed across that whole process, not just the
last couple. This drops them rather than rerunning either large script.

Run with: python scripts/25_filter_feature_files.py

Input:  data/processed/final_roster.csv
        data/processed/pipeline_features.csv
        data/processed/patent_features.csv
Output: both feature files overwritten, filtered to the current roster
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

    print("\nBoth feature files now match the current roster exactly. "
          "Safe to join them on cik without any stale rows leaking in.")
