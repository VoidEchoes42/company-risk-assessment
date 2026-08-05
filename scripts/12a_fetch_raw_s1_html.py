"""
Step 4.2a: Fetch and cache each company's raw S-1 HTML to disk.

Split out from extraction on purpose. This is the slow, network-bound
half. Once these files are on disk, the extraction logic (12b) can be
re-run, re-tuned, and re-run again as many times as needed, for free,
in seconds, no more 20-minute waits if the heuristic needs another pass.
Given today already needed two passes on the extraction logic, there
will likely be a third.

Safe to re-run: already-cached files are skipped, so if this gets
interrupted partway through, just run it again.

Run with: python scripts/12a_fetch_raw_s1_html.py

Input:  data/processed/review_full_read.csv
Output: data/raw/s1_html/{cik}.html   (one file per company)
        data/processed/s1_manifest.csv (company_name, cik, s1_url, filing date)
"""

import time
from pathlib import Path

import pandas as pd
import requests

IN_PATH = Path("data/processed/review_full_read.csv")
HTML_DIR = Path("data/raw/s1_html")
MANIFEST_PATH = Path("data/processed/s1_manifest.csv")

HEADERS = {
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json, text/html",
}


def find_s1_document(cik10: str):
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return None, None
    data = resp.json()
    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accessions = recent.get("accessionNumber", [])
    docs = recent.get("primaryDocument", [])
    dates = recent.get("filingDate", [])

    candidates = [
        (a, doc, dt) for f, a, doc, dt in zip(forms, accessions, docs, dates)
        if f == "S-1"
    ]
    if not candidates:
        return None, None
    candidates.sort(key=lambda c: c[2])
    accession, doc, filing_date = candidates[0]
    cik_plain = str(int(cik10))
    accession_plain = accession.replace("-", "")
    doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik_plain}/{accession_plain}/{doc}"
    return doc_url, filing_date


if __name__ == "__main__":
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(IN_PATH, dtype={"cik": str})
    df["cik"] = df["cik"].str.zfill(10)
    print(f"Fetching and caching S-1 HTML for {len(df)} companies.")

    manifest_rows = []
    fetched, skipped, missing = 0, 0, 0
    for i, row in df.iterrows():
        cik10 = row["cik"]
        html_path = HTML_DIR / f"{cik10}.html"

        if html_path.exists():
            skipped += 1
            manifest_rows.append(
                {"company_name": row["company_name"], "cik": cik10,
                 "html_path": str(html_path)}
            )
            continue

        doc_url, filing_date = find_s1_document(cik10)
        if not doc_url:
            missing += 1
            manifest_rows.append(
                {"company_name": row["company_name"], "cik": cik10,
                 "html_path": None}
            )
            continue

        try:
            resp = requests.get(doc_url, headers=HEADERS, timeout=30)
            if resp.status_code == 200:
                html_path.write_text(resp.text, encoding="utf-8", errors="ignore")
                fetched += 1
                manifest_rows.append(
                    {"company_name": row["company_name"], "cik": cik10,
                     "html_path": str(html_path), "s1_url": doc_url,
                     "s1_filing_date": filing_date}
                )
        except requests.RequestException:
            missing += 1
            manifest_rows.append(
                {"company_name": row["company_name"], "cik": cik10,
                 "html_path": None}
            )

        if (i + 1) % 25 == 0:
            print(f"{i + 1}/{len(df)} done ({fetched} fetched, "
                  f"{skipped} already cached, {missing} missing)")
        time.sleep(0.2)

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(manifest_rows).to_csv(MANIFEST_PATH, index=False)
    print(f"\nDone. {fetched} newly fetched, {skipped} already cached, "
          f"{missing} had no findable S-1. Manifest at {MANIFEST_PATH}.")
    print("Next: 12b_extract_summaries.py reads these files locally, no "
          "network needed, safe to re-run any time.")
