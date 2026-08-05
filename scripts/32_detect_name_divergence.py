"""
Step 4.3d: Before doing deep, cited individual research on all 136
'acquisition' companies (not realistic in one pass, would need 300+
searches), mechanically flag the ones that structurally match the
Conatus pattern: the company's current SEC-registered name shares
essentially nothing with the name it had during our study window.

Conatus Pharmaceuticals is now registered as "Histogen, Inc." Zero
shared words. That is not a coincidence of corporate rebranding, it is
the signature of a reverse merger where an unrelated private company
took over the public shell and the original drug program was
abandoned. This check applies the same name-matching logic already
used throughout this project (Jaccard token overlap) to find every
other company with the same signature.

This does NOT replace individual research, it replaces GUESSING at
which of 136 companies need it. Anything flagged here is a strong
candidate for real research with real citations. Anything not flagged
is not automatically confirmed as a genuine successful acquisition,
just deprioritized, since it doesn't show this specific red flag.

Run with: python scripts/32_detect_name_divergence.py

Input:  data/processed/exit_reasons.csv
Output: data/processed/name_divergence_check.csv
"""

import re
import time
from pathlib import Path

import pandas as pd
import requests

EXIT_PATH = Path("data/processed/exit_reasons.csv")
OUT_PATH = Path("data/processed/name_divergence_check.csv")

DIVERGENCE_THRESHOLD = 0.15  # below this, essentially no shared words

SUFFIXES = {
    "INC", "INCORPORATED", "CORP", "CORPORATION", "LTD", "LIMITED", "LLC",
    "PLC", "CO", "COMPANY", "HOLDING", "HOLDINGS", "GROUP", "BV", "NV", "SA",
    "AG", "SE", "THE",
}

HEADERS = {
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json",
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


def get_current_registered_name(cik10: str):
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return None
    return resp.json().get("name")


if __name__ == "__main__":
    df = pd.read_csv(EXIT_PATH, dtype={"cik": str})
    df["cik"] = df["cik"].str.zfill(10)
    acquisitions = df[df["exit_reason"] == "acquisition"]
    print(f"Checking {len(acquisitions)} 'acquisition' companies for name divergence.")

    rows = []
    for i, (idx, row) in enumerate(acquisitions.iterrows()):
        current_name = get_current_registered_name(row["cik"])
        score = name_match_score(row["company_name"], current_name) if current_name else None
        flagged = score is not None and score < DIVERGENCE_THRESHOLD

        rows.append({
            "company_name": row["company_name"], "cik": row["cik"],
            "current_registered_name": current_name,
            "name_match_score": score, "flagged_for_review": flagged,
        })
        if flagged:
            print(f"  FLAGGED: {row['company_name']!r} -> now {current_name!r} "
                  f"(match score {score:.2f})")

        if (i + 1) % 25 == 0:
            n_flagged = sum(r["flagged_for_review"] for r in rows)
            print(f"{i + 1}/{len(acquisitions)} checked, {n_flagged} flagged so far")
        time.sleep(0.15)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUT_PATH, index=False)

    n_flagged = out_df["flagged_for_review"].sum()
    print(f"\n{n_flagged} of {len(out_df)} flagged for individual research, "
          f"written to {OUT_PATH}.")
    print("These get real, cited research next. The rest stay labeled "
          "'acquisition' for now, not confirmed successful, just not "
          "showing this particular red flag.")
