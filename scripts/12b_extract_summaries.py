"""
Step 4.2b: Extract business summaries from the locally cached S-1 HTML.

Fixed extraction logic, two changes from the first version:
  1. Looks for the "Prospectus Summary" heading and starts reading after
     it, that's structurally where every S-1's actual business
     description lives, rather than just taking the first long-enough
     paragraph from the top of the document.
  2. Explicitly rejects paragraphs matching known cover-page boilerplate
     (Rule 462(b)/462(c) checkbox language), which is what the first
     version was actually extracting most of the time. It's long enough
     to pass a length filter but has nothing to do with the company.

Pure local file reads, no network, safe to re-run as many times as the
heuristic needs tuning.

Run with: python scripts/12b_extract_summaries.py

Input:  data/processed/s1_manifest.csv
        data/raw/s1_html/{cik}.html
Output: data/processed/business_summaries.csv
"""

import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

MANIFEST_PATH = Path("data/processed/s1_manifest.csv")
OUT_PATH = Path("data/processed/business_summaries.csv")

MIN_PARAGRAPH_LEN = 250
MAX_SNIPPET_LEN = 2500

# A broader, more principled category than a growing list of one-off
# phrases: paragraphs that talk about the DOCUMENT itself (the summary,
# the prospectus, the registration statement) rather than about the
# company. Virtually every disclaimer/legal paragraph in an S-1 is
# self-referential this way, and virtually no genuine company overview
# is.
BOILERPLATE_MARKERS = [
    "this summary", "this prospectus", "elsewhere in this prospectus",
    "before investing", "should carefully read", "does not contain all",
    "registration statement", "securities act", "check the following box",
    "hereby amends this registration statement", "section 8(a)",
    "large accelerated filer", "smaller reporting company",
    "emerging growth company", "exchange act",
    "i.r.s. employer", "jurisdiction of incorporation",
]


def is_boilerplate(paragraph: str) -> bool:
    p = paragraph.lower()
    return any(marker in p for marker in BOILERPLATE_MARKERS)


def extract_summary(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "table"]):
        tag.decompose()

    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]

    # LAST short "prospectus summary" mention, not first. A table of
    # contents lists that phrase (with a page number) before the real
    # section heading appears later in the document, taking the first
    # match was landing us back at the table of contents.
    start_idx = 0
    for i, p in enumerate(paragraphs):
        if "prospectus summary" in p.lower() and len(p) < 100:
            start_idx = i + 1

    candidates = paragraphs[start_idx:] if start_idx else paragraphs
    long_paragraphs = [
        p for p in candidates
        if len(p) >= MIN_PARAGRAPH_LEN and not is_boilerplate(p)
    ]

    if not long_paragraphs:
        # Fallback for filings that don't use <p> tags consistently.
        text = soup.get_text("\n")
        blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
        long_paragraphs = [
            b for b in blocks
            if len(b) >= MIN_PARAGRAPH_LEN and not is_boilerplate(b)
        ]

    if not long_paragraphs:
        return ""
    return " ".join(long_paragraphs[:2])[:MAX_SNIPPET_LEN]


if __name__ == "__main__":
    manifest = pd.read_csv(MANIFEST_PATH, dtype={"cik": str})
    print(f"Extracting summaries for {len(manifest)} companies from cached HTML.")

    rows = []
    failures = 0
    for i, row in manifest.iterrows():
        summary = ""
        html_path = row.get("html_path")
        if isinstance(html_path, str) and Path(html_path).exists():
            html = Path(html_path).read_text(encoding="utf-8", errors="ignore")
            summary = extract_summary(html)

        if not summary:
            failures += 1
            summary = "EXTRACTION FAILED, open s1_url directly"

        rows.append(
            {
                "company_name": row["company_name"],
                "cik": row["cik"],
                "s1_url": row.get("s1_url"),
                "s1_filing_date": row.get("s1_filing_date"),
                "summary_snippet": summary,
            }
        )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT_PATH, index=False)
    print(f"{len(rows) - failures} extracted, {failures} failed. "
          f"Written to {OUT_PATH}.")