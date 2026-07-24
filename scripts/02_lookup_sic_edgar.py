"""
Step 4.1b: Attach each company's real SIC code from SEC EDGAR, then keep
only life-science companies (SIC 2830, 2834, 2835, 2836).

This is the fix for the missing SIC column. It also does double duty:
every later step (pulling S-1s, 8-Ks, 10-Ks) needs each company's CIK
anyway, so getting it now isn't wasted work.

How it works:
  1. Download SEC's bulk ticker-to-CIK mapping file once (small, cached
     locally after the first run).
  2. For each company in roster_by_date.csv, look up its CIK by ticker.
  3. Call EDGAR's submissions API for that CIK, which returns the
     company's own official SIC code.
  4. Keep only SIC in {2830, 2834, 2835, 2836}.

Same honesty note as before: I verified this endpoint and its field names
against current documentation, but could not execute a live call from
this sandbox, no internet access here. Field names below (sic,
sicDescription) are well confirmed, but if anything comes back oddly,
the script prints the raw response for the first company so you can see
exactly what SEC is sending back.

Run with: python scripts/02_lookup_sic_edgar.py

Input:  data/processed/roster_by_date.csv
Output: data/processed/roster_life_science.csv
"""

import time
from pathlib import Path

import pandas as pd
import requests

IN_PATH = Path("data/processed/roster_by_date.csv")
OUT_PATH = Path("data/processed/roster_life_science.csv")
TICKERS_CACHE = Path("data/raw/company_tickers.json")

LIFE_SCIENCE_SIC = {"2830", "2834", "2835", "2836"}

HEADERS = {
    # SEC blocks or rate-limits requests without a real identifying value.
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json",
}


def get_ticker_to_cik_map() -> dict:
    if TICKERS_CACHE.exists():
        import json

        return {
            v["ticker"].upper(): str(v["cik_str"]).zfill(10)
            for v in json.loads(TICKERS_CACHE.read_text()).values()
        }

    resp = requests.get(
        "https://www.sec.gov/files/company_tickers.json", headers=HEADERS, timeout=30
    )
    resp.raise_for_status()
    TICKERS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    TICKERS_CACHE.write_text(resp.text)

    data = resp.json()
    return {
        v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in data.values()
    }


def get_sic(cik10: str, show_raw: bool = False) -> tuple:
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return None, None
    data = resp.json()
    if show_raw:
        print("Raw fields on the first successful lookup, sanity-check "
              "'sic' and 'sicDescription' appear as expected:")
        print({k: data[k] for k in list(data)[:8]})
    return data.get("sic"), data.get("sicDescription")


if __name__ == "__main__":
    roster = pd.read_csv(IN_PATH)
    ticker_to_cik = get_ticker_to_cik_map()
    print(f"Loaded {len(ticker_to_cik)} ticker-to-CIK mappings.")

    sics, sic_descs, ciks = [], [], []
    shown_raw = False
    for i, row in roster.iterrows():
        ticker = str(row["ticker"]).upper().strip()
        cik10 = ticker_to_cik.get(ticker)
        if cik10 is None:
            sics.append(None)
            sic_descs.append(None)
            ciks.append(None)
            continue
        sic, sic_desc = get_sic(cik10, show_raw=not shown_raw)
        shown_raw = True
        sics.append(sic)
        sic_descs.append(sic_desc)
        ciks.append(cik10)
        if i % 20 == 0:
            print(f"{i + 1}/{len(roster)} looked up")
        time.sleep(0.15)  # stay comfortably under SEC's rate limit

    roster["cik"] = ciks
    roster["sic"] = sics
    roster["sic_description"] = sic_descs

    unmatched = roster["cik"].isna().sum()
    if unmatched:
        print(f"\n{unmatched} companies had no ticker match in EDGAR, "
              "likely delisted tickers Ritter's file still shows, or "
              "ticker changes. These need a manual name-based lookup, "
              "expect this, don't expect zero.")

    life_science = roster[roster["sic"].isin(LIFE_SCIENCE_SIC)].copy()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    life_science.to_csv(OUT_PATH, index=False)
    print(f"\n{len(life_science)} life-science companies written to {OUT_PATH}")
    print("Next: hand-skim each one's S-1 business summary to keep "
          "therapeutics only, dropping diagnostics/CRO/tools/devices/service.")
