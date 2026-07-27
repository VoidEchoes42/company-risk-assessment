"""
Step 4.1d: Catch ticker-collision errors in roster_life_science.csv.

Why this exists: tickers get reused after a company delists. Adeptus
Health (NYSE: ADPT, emergency rooms, bankrupt 2017) and Adaptive
Biotechnologies (Nasdaq: ADPT, real biotech, IPO 2019) both used the
ticker ADPT four years apart. 02_lookup_sic_edgar.py matches on TODAY's
ticker list, so any row like this silently gets the wrong company's CIK
and SIC attached, no error thrown.

What this does: for every company already in roster_life_science.csv,
re-fetch its CIK's registered name (and former names) from EDGAR, and
compare that against the company name Ritter's file gave us. If they
don't reasonably match, the ticker got reused by someone else and the
row is quarantined for manual review rather than silently trusted.

Run with: python scripts/04_verify_names.py

Input:  data/processed/roster_life_science.csv
Output: data/processed/roster_life_science_verified.csv (trust these)
        data/processed/roster_life_science_suspect.csv (ticker collisions,
        needs a manual CIK lookup by name instead)
"""

import re
import time
from pathlib import Path

import pandas as pd
import requests

IN_PATH = Path("data/processed/roster_life_science.csv")
VERIFIED_PATH = Path("data/processed/roster_life_science_verified.csv")
SUSPECT_PATH = Path("data/processed/roster_life_science_suspect.csv")

MATCH_THRESHOLD = 0.5

HEADERS = {
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json",
}

SUFFIXES = {
    "INC", "INCORPORATED", "CORP", "CORPORATION", "LTD", "LIMITED", "LLC",
    "PLC", "CO", "COMPANY", "HOLDING", "HOLDINGS", "GROUP", "BV", "NV", "SA",
    "AG", "SE", "THE",
}


def normalize_name(name: str) -> set:
    name = re.sub(r"[^A-Z0-9 ]", " ", str(name).upper())
    return {t for t in name.split() if t not in SUFFIXES}


def name_match_score(a: str, b: str) -> float:
    ta, tb = normalize_name(a), normalize_name(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / min(len(ta), len(tb))


def best_match_score(ritter_name: str, edgar_data: dict) -> float:
    candidates = [edgar_data.get("name", "")]
    for former in edgar_data.get("formerNames", []) or []:
        candidates.append(former.get("name", ""))
    return max((name_match_score(ritter_name, c) for c in candidates), default=0.0)


def fetch_edgar_entity(cik10: str) -> dict:
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return {}
    return resp.json()


if __name__ == "__main__":
    roster = pd.read_csv(IN_PATH, dtype={"cik": str})
    roster["cik"] = roster["cik"].str.zfill(10)
    print(f"Re-checking {len(roster)} companies against EDGAR's own name records.")

    scores = []
    for i, row in roster.iterrows():
        entity = fetch_edgar_entity(row["cik"])
        score = best_match_score(row["company_name"], entity)
        scores.append(score)
        if score < MATCH_THRESHOLD:
            print(f"  SUSPECT: '{row['company_name']}' vs EDGAR's "
                  f"'{entity.get('name', '?')}' (score {score:.2f})")
        if (i + 1) % 20 == 0:
            print(f"{i + 1}/{len(roster)} checked")
        time.sleep(0.15)

    roster["name_match_score"] = scores
    verified = roster[roster["name_match_score"] >= MATCH_THRESHOLD].copy()
    suspect = roster[roster["name_match_score"] < MATCH_THRESHOLD].copy()

    VERIFIED_PATH.parent.mkdir(parents=True, exist_ok=True)
    verified.to_csv(VERIFIED_PATH, index=False)
    suspect.to_csv(SUSPECT_PATH, index=False)

    print(f"\n{len(verified)} verified, {len(suspect)} suspect (ticker collisions).")
    print("Trust roster_life_science_verified.csv from here on. The suspect "
          "file needs each company looked up by name instead of ticker, "
          "that's next, don't discard it.")
