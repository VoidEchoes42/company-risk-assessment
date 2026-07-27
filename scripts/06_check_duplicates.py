"""
Diagnostic, not part of the main pipeline: check roster_final.csv for
actual duplicate companies two ways.

1. Duplicate CIK values. This is the definitive check, two rows with the
   same CIK are mathematically the same SEC filer, no judgment call
   needed. Any hit here is a real bug that needs merging.

2. Similar-but-not-identical names (the old check), shown WITH each
   company's CIK this time. Most of these are just different companies
   sharing a common industry word ("Therapeutics", "Pharmaceuticals"),
   which is expected and fine. The CIK column tells you immediately
   which ones, if any, are actually the same filer under two names
   rather than two unrelated companies that happen to sound similar.

Run with: python scripts/06_check_duplicates.py

Input: data/processed/roster_final.csv
"""

import re
from itertools import combinations
from pathlib import Path

import pandas as pd

FINAL_PATH = Path("data/processed/roster_final.csv")

SUFFIXES = {
    "INC", "INCORPORATED", "CORP", "CORPORATION", "LTD", "LIMITED", "LLC",
    "PLC", "CO", "COMPANY", "HOLDING", "HOLDINGS", "GROUP", "BV", "NV", "SA",
    "AG", "SE", "THE",
}


def normalize_name(name: str) -> set:
    name = str(name).upper().replace(".", "")
    name = re.sub(r"[^A-Z0-9 ]", " ", name)
    return {t for t in name.split() if t not in SUFFIXES}


def name_match_score(a: str, b: str) -> float:
    ta, tb = normalize_name(a), normalize_name(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


if __name__ == "__main__":
    df = pd.read_csv(FINAL_PATH, dtype={"cik": str})
    df["cik"] = df["cik"].str.zfill(10)

    print("=== CHECK 1: duplicate CIKs (definitive) ===")
    dupe_ciks = df[df.duplicated(subset="cik", keep=False)].sort_values("cik")
    if dupe_ciks.empty:
        print("None found. Every row is a distinct SEC filer.")
    else:
        print(f"{dupe_ciks['cik'].nunique()} CIK(s) appear more than once, "
              "these ARE the same company and need merging:")
        print(dupe_ciks[["company_name", "cik", "sic"]].to_string(index=False))

    print("\n=== CHECK 2: similar names, shown with CIK ===")
    names_ciks = list(zip(df["company_name"], df["cik"]))
    suspicious = []
    for (a, cik_a), (b, cik_b) in combinations(names_ciks, 2):
        score = name_match_score(a, b)
        if 0.3 <= score < 1.0:
            suspicious.append((score, a, cik_a, b, cik_b, cik_a == cik_b))
    suspicious.sort(key=lambda x: (-x[5], -x[0]))  # same-CIK hits float to top

    same_cik_hits = [s for s in suspicious if s[5]]
    print(f"{len(suspicious)} total pairs with partial name overlap, "
          f"{len(same_cik_hits)} of them share a CIK (those are the real ones).")
    for score, a, cik_a, b, cik_b, same in suspicious[:40]:
        flag = "  <-- SAME CIK, real duplicate" if same else ""
        print(f"  {score:.2f}  {a!r} (CIK {cik_a})  <->  {b!r} (CIK {cik_b}){flag}")
