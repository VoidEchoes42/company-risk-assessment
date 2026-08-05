"""
Step 4.2 (helper): Pull each company's opening business description
straight from their actual S-1, into one file, instead of opening 464
separate EDGAR pages by hand.

Read this before running, real limits:
  - S-1 HTML formatting varies across companies, law firms, and years,
    2012-2019 spans a lot of style drift. This uses a best-effort
    heuristic (first couple of substantial prose paragraphs after
    stripping tags, tables, scripts, styles), not a guaranteed-clean
    "Business Overview" section pull. Some entries will come out noisy
    or short. When that happens, that company needs the real s1_url,
    not a re-run of this script.
  - This fetches actual filing documents, not small JSON responses, so
    it's much slower than anything so far. Real time, likely 15+
    minutes for 464 companies depending on document sizes and your
    connection. Let it run.
  - I could not test this against a single live filing from this
    sandbox (no internet access here). URL construction and JSON field
    names are confirmed against SEC's documented API shape from
    multiple sources, but the extraction heuristic itself was only
    tested against realistic fake HTML, not a real S-1. Spot-check the
    first 10-15 rows before trusting the rest.

Run with: python scripts/12_fetch_business_summaries.py

Requires: pip install beautifulsoup4

Input:  data/processed/review_full_read.csv
Output: data/processed/business_summaries.csv
"""

import re
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

IN_PATH = Path("data/processed/review_full_read.csv")
OUT_PATH = Path("data/processed/business_summaries.csv")

HEADERS = {
    "User-Agent": "Aman <your_email@example.com>",
    "Accept": "application/json, text/html",
}

MIN_PARAGRAPH_LEN = 250
MAX_SNIPPET_LEN = 2500


def find_s1_document(cik10: str):
    """Return (doc_url, filing_date) for this company's earliest S-1."""
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
    candidates.sort(key=lambda c: c[2])  # earliest S-1, the original filing
    accession, doc, filing_date = candidates[0]
    cik_plain = str(int(cik10))
    accession_plain = accession.replace("-", "")
    doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik_plain}/{accession_plain}/{doc}"
    return doc_url, filing_date


def extract_summary(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "table"]):
        tag.decompose()

    # Text from individual <p> tags directly, this is what most S-1
    # markup uses for prose, and it correctly separates adjacent
    # paragraphs even when there's no blank line between them in the
    # raw source, which relying on whitespace patterns alone gets wrong.
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    long_paragraphs = [p for p in paragraphs if len(p) >= MIN_PARAGRAPH_LEN]

    if not long_paragraphs:
        # Fallback for the filings that don't use <p> tags at all.
        text = soup.get_text("\n")
        blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
        long_paragraphs = [b for b in blocks if len(b) >= MIN_PARAGRAPH_LEN]

    if not long_paragraphs:
        return ""
    return " ".join(long_paragraphs[:2])[:MAX_SNIPPET_LEN]


if __name__ == "__main__":
    df = pd.read_csv(IN_PATH, dtype={"cik": str})
    df["cik"] = df["cik"].str.zfill(10)
    print(f"Fetching S-1 business summaries for {len(df)} companies. "
          "This is slow, real documents, not small JSON, let it run.")

    rows = []
    failures = 0
    for i, row in df.iterrows():
        doc_url, filing_date, summary = None, None, ""
        try:
            doc_url, filing_date = find_s1_document(row["cik"])
            if doc_url:
                resp = requests.get(doc_url, headers=HEADERS, timeout=30)
                if resp.status_code == 200:
                    summary = extract_summary(resp.text)
        except requests.RequestException:
            pass

        if not summary:
            failures += 1
            summary = "EXTRACTION FAILED, open s1_url directly"

        rows.append(
            {
                "company_name": row["company_name"],
                "cik": row["cik"],
                "s1_url": doc_url,
                "s1_filing_date": filing_date,
                "summary_snippet": summary,
            }
        )
        if (i + 1) % 25 == 0:
            print(f"{i + 1}/{len(df)} processed, {failures} extraction failures so far")
        time.sleep(0.2)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT_PATH, index=False)
    print(f"\n{len(rows) - failures} extracted cleanly, {failures} failed "
          f"and need the real s1_url instead. Written to {OUT_PATH}.")
