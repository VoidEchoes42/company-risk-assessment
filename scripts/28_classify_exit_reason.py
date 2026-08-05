"""
Step 4.3b: For every company that stopped filing (deregistered_or_delisted
plus stalled_filing), determine whether the exit was a bankruptcy or an
acquisition, the actual distinction Step 1's label needs.

Uses SEC's full-text search endpoint (efts.sec.gov), not the plain
submissions API, specifically because it returns the numbered "items"
disclosed on each 8-K as structured data. An 8-K disclosing bankruptcy
files under Item 1.03, directly detectable without opening the document.
Confirmed against the same endpoint already used successfully in script
03 (the field showed up as 'items' in that earlier real response).

Two signals checked per company:
  bankruptcy: any 8-K with item 1.03 anywhere in its history
  acquisition: any DEFM14A (merger proxy), SC 14D9 (tender offer
               response), SC TO-T, or SC TO-I (tender offer statements)

If both appear (rare, e.g. failed merger talks followed by bankruptcy),
whichever happened LATER is treated as the real outcome, not just the
first one found.

I could not test a live response from this sandbox (no network access
here), the items field's exact shape (list vs string) is inferred from
the field's presence in an earlier confirmed response, not directly
verified. The script prints the raw item value on the first real
bankruptcy-flagged hit specifically so this can be checked immediately.

Run with: python scripts/28_classify_exit_reason.py

Input:  data/processed/outcome_triage.csv
Output: data/processed/exit_reasons.csv
"""

import time
from pathlib import Path

import pandas as pd
import requests

TRIAGE_PATH = Path("data/processed/outcome_triage.csv")
OUT_PATH = Path("data/processed/exit_reasons.csv")

FTS_URL = "https://efts.sec.gov/LATEST/search-index"
BANKRUPTCY_ITEM = "1.03"
MERGER_FORMS = ["DEFM14A", "SC 14D9", "SC TO-T", "SC TO-I"]

HEADERS = {
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json",
}


def search_filings(cik10: str, forms: str) -> list:
    params = {"forms": forms, "ciks": cik10}
    resp = requests.get(FTS_URL, params=params, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return []
    data = resp.json()
    return data.get("hits", {}).get("hits", [])


def check_exit_reason(cik10: str, show_raw: bool = False) -> dict:
    bankruptcy_date = None
    eightk_hits = search_filings(cik10, "8-K")
    for hit in eightk_hits:
        src = hit.get("_source", {})
        items = src.get("items", [])
        if show_raw and items:
            print(f"  Raw items field on an 8-K hit (checking shape): {items!r}")
        items_list = items if isinstance(items, list) else [items]
        if BANKRUPTCY_ITEM in items_list:
            file_date = src.get("file_date")
            if file_date and (bankruptcy_date is None or file_date < bankruptcy_date):
                bankruptcy_date = file_date

    merger_date = None
    merger_hits = search_filings(cik10, ",".join(MERGER_FORMS))
    for hit in merger_hits:
        src = hit.get("_source", {})
        file_date = src.get("file_date")
        if file_date and (merger_date is None or file_date < merger_date):
            merger_date = file_date

    if bankruptcy_date and merger_date:
        reason = "bankruptcy" if bankruptcy_date > merger_date else "acquisition"
    elif bankruptcy_date:
        reason = "bankruptcy"
    elif merger_date:
        reason = "acquisition"
    else:
        reason = "unclear"

    return {"exit_reason": reason, "bankruptcy_date": bankruptcy_date, "merger_date": merger_date}


if __name__ == "__main__":
    triage = pd.read_csv(TRIAGE_PATH, dtype={"cik": str})
    triage["cik"] = triage["cik"].str.zfill(10)
    to_check = triage[triage["bucket"].isin(["deregistered_or_delisted", "stalled_filing"])]
    print(f"Checking exit reason for {len(to_check)} companies that stopped filing.")

    rows = []
    shown_raw = False
    for i, row in to_check.iterrows():
        result = check_exit_reason(row["cik"], show_raw=not shown_raw)
        if result["bankruptcy_date"]:
            shown_raw = True
        rows.append({"company_name": row["company_name"], "cik": row["cik"], **result})

        if (len(rows)) % 25 == 0:
            counts = pd.Series([r["exit_reason"] for r in rows]).value_counts().to_dict()
            print(f"{len(rows)}/{len(to_check)} checked, {counts}")
        time.sleep(0.15)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUT_PATH, index=False)

    print(f"\nWritten to {OUT_PATH}.")
    print(out_df["exit_reason"].value_counts())
    print("\n'unclear' companies had no Item 1.03 8-K and no merger-specific "
          "form found, could be a quiet wind-down, an asset sale, a going-"
          "private transaction structured differently, or a genuine gap in "
          "this detection. Worth a manual glance, not an automatic label.")
