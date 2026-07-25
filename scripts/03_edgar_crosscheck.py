"""
Step 4.1c: Cross-check the roster directly against SEC EDGAR.

Catches any life-science IPO from 2012-2019 that Ritter's dataset might
have missed or classified differently. Uses EDGAR's full text search API,
free, no key required, but SEC does require a real, descriptive User-Agent
header identifying you, generic or missing ones get rate-limited or blocked.
Set YOUR real name and email in HEADERS below before running.

Run with: python scripts/03_edgar_crosscheck.py

Output: data/processed/roster_edgar_crosscheck.csv

Note: I built this against EDGAR's documented full text search parameters,
but could not execute a live call to confirm the exact response shape from
this sandbox (no network access here). The script prints the raw field
names on the first result before parsing anything, check that printout
against the company_name/cik/form_type/filed_at lines below and adjust if
they don't line up. If the whole thing returns 0 results, sanity-check the
same filters by hand at https://www.sec.gov/edgar/search/ first.
"""

import time
from pathlib import Path

import pandas as pd
import requests

SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
LIFE_SCIENCE_SIC = "2830,2834,2835,2836"
OUT_PATH = Path("data/processed/roster_edgar_crosscheck.csv")

HEADERS = {
    # SEC's fair-access policy: identify yourself or risk being blocked.
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json",
}


def fetch_page(start: int) -> dict:
    params = {
        "q": "initial public offering",
        "forms": "S-1",
        "sics": LIFE_SCIENCE_SIC,
        "dateRange": "custom",
        "startdt": "2012-01-01",
        "enddt": "2019-12-31",
        "from": start,
    }
    resp = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_all() -> list:
    all_hits = []
    start = 0
    while True:
        data = fetch_page(start)
        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            break
        all_hits.extend(hits)
        total = data["hits"]["total"]["value"]
        start += len(hits)
        print(f"Fetched {start} of {total}")
        if start >= total:
            break
        time.sleep(0.3)  # stay comfortably under SEC's rate limit
    return all_hits


def to_dataframe(hits: list) -> pd.DataFrame:
    if hits:
        print("Fields available on the first result (check these against "
              "the lines below):")
        print(list(hits[0].get("_source", {}).keys()))

    rows = []
    for h in hits:
        src = h.get("_source", {})
        rows.append(
            {
                "company_name": (src.get("display_names") or [""])[0],
                "cik": (src.get("ciks") or [""])[0],
                "form_type": src.get("form_type") or src.get("root_form"),
                "filed_at": src.get("file_date"),
                "filing_url": h.get("_id"),
            }
        )
    return pd.DataFrame(rows).drop_duplicates(subset="company_name")


if __name__ == "__main__":
    hits = fetch_all()
    df = to_dataframe(hits)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"{len(df)} unique companies written to {OUT_PATH}")
    print("Next: merge this with roster_life_science.csv by company name, dedup, "
          "then hand-skim each S-1's business summary to keep therapeutics "
          "only and drop diagnostics/CRO/tools/devices/service companies.")
