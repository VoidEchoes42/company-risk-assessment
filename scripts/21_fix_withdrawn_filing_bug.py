"""
Fix for a real bug in script 20: it treated ANY substantive-looking
filing as proof a company was already public before 2011, including a
bare S-1. But an S-1 alone doesn't prove anything, it can be filed and
then withdrawn without ever leading to a real offering, exactly what
happened to PTC Therapeutics (filed an S-1 in 2006, was not declared
effective, their real IPO wasn't until 2013 through a completely normal
underwritten offering).

This is the same distinction identified much earlier in this project,
during the original reverse-merger screen: only filing types that
REQUIRE an already-public, already-reporting company are real proof.
10-K, 10-Q, 8-K, DEF 14A, S-8, and Schedule 13D/G all fall in that
category, no private company can file any of them. An S-1 does not,
it is just an attempt. Script 20 lost that distinction by checking
against a denylist (exclude only Form D/REGDEX) instead of an allowlist
(only count these specific proof-of-public forms), which is the more
robust design and what this uses instead.

Run with: python scripts/21_fix_withdrawn_filing_bug.py

Input:  data/processed/scope_violations_removed.csv
        data/processed/final_roster.csv
Output: data/processed/final_roster.csv (overwritten, false positives restored)
        data/processed/scope_violations_removed.csv (overwritten, corrected)
"""

import time
from pathlib import Path

import pandas as pd
import requests

REMOVED_PATH = Path("data/processed/scope_violations_removed.csv")
ROSTER_PATH = Path("data/processed/final_roster.csv")

WINDOW_START = "2011-01-01"

# Only these REQUIRE an already-public, already-reporting company. An
# S-1, by contrast, only proves an attempt, which may have been
# withdrawn, exactly PTC Therapeutics's situation.
PROOF_OF_PUBLIC_FORMS = {
    "10-K", "10-K/A", "10-K405", "10-K405/A", "10-KSB", "10-KSB/A",
    "10-Q", "10-Q/A", "10QSB", "10QSB/A",
    "8-K", "8-K/A",
    "DEF 14A", "DEF 14C",
    "S-8", "S-8 POS",
    "SC 13D", "SC 13D/A", "SC 13G", "SC 13G/A",
}

HEADERS = {
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json",
}


def get_full_filing_history(cik10: str):
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return [], []
    data = resp.json()
    recent = data.get("filings", {}).get("recent", {})
    forms = list(recent.get("form", []))
    dates = list(recent.get("filingDate", []))
    for file_info in data.get("filings", {}).get("files", []):
        file_name = file_info.get("name")
        if not file_name:
            continue
        older_url = f"https://data.sec.gov/submissions/{file_name}"
        older_resp = requests.get(older_url, headers=HEADERS, timeout=30)
        if older_resp.status_code == 200:
            older_data = older_resp.json()
            forms.extend(older_data.get("form", []))
            dates.extend(older_data.get("filingDate", []))
        time.sleep(0.15)
    return forms, dates


def true_predates_window(cik10: str) -> tuple:
    forms, dates = get_full_filing_history(cik10)
    proof_dates = [d for f, d in zip(forms, dates) if f in PROOF_OF_PUBLIC_FORMS]
    earliest = min(proof_dates) if proof_dates else None
    return bool(earliest) and earliest < WINDOW_START, earliest


if __name__ == "__main__":
    removed = pd.read_csv(REMOVED_PATH, dtype={"cik": str})
    roster = pd.read_csv(ROSTER_PATH, dtype={"cik": str})
    removed["cik"] = removed["cik"].str.zfill(10)

    # Spinoff-form removals aren't touched by this fix, that check was
    # never about filing dates. Only "predates window" removals get
    # rechecked under the corrected, stricter proof standard.
    to_recheck = removed[removed["reason"].str.startswith("predates window")]
    print(f"Rechecking {len(to_recheck)} 'predates window' removals under "
          "the corrected proof standard. Spinoff-form removals are untouched.")

    still_excluded, restored = [], []
    for i, row in to_recheck.iterrows():
        really_predates, earliest = true_predates_window(row["cik"])
        if really_predates:
            still_excluded.append({
                "company_name": row["company_name"], "cik": row["cik"],
                "reason": f"predates window, confirmed (earliest proof-of-public filing: {earliest})",
            })
        else:
            restored.append(row.to_dict())
            print(f"  RESTORED: {row['company_name']!r}, no filing proves it "
                  f"was public before {WINDOW_START}, earlier flag was a "
                  "false positive (likely a withdrawn S-1).")
        if (i + 1) % 10 == 0:
            print(f"{i + 1}/{len(to_recheck)} rechecked")

    spinoff_removed = removed[removed["reason"].str.startswith("spinoff")]
    final_removed = pd.concat(
        [spinoff_removed, pd.DataFrame(still_excluded)], ignore_index=True
    )
    restored_df = pd.DataFrame(restored)

    updated_roster = pd.concat([roster, restored_df], ignore_index=True) if len(restored_df) else roster

    updated_roster.to_csv(ROSTER_PATH, index=False)
    final_removed.to_csv(REMOVED_PATH, index=False)

    print(f"\n{len(restored)} companies restored to {ROSTER_PATH}, now "
          f"{len(updated_roster)} total.")
    print(f"{len(final_removed)} remain correctly excluded, written to {REMOVED_PATH}.")
