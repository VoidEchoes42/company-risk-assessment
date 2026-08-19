"""
Step 4.2c: Extract candidate financing information (pre-IPO funding
rounds, dollar amounts) from S-1 filings already cached locally from
earlier in this project (data/raw/s1_html/{cik}.html, from scripts
12a/12b).

Honest framing, same as every other genuinely hard extraction in this
project: this pulls CANDIDATE sentences mentioning funding rounds and
dollar amounts, it does not claim to produce a perfect structured
total. Real S-1 language varies too much for pure regex to get this
100% right (a "Series B" might be mentioned in one sentence and its
dollar amount two sentences later, or the same round gets referenced
multiple times across the document). This narrows 50+ pages down to a
handful of relevant lines per company, cutting review time from
reading a full filing to reading a few sentences.

What it looks for:
  - Funding round mentions: "Series A/B/C/D/E/F ... preferred stock"
  - Dollar amounts: "$X million/thousand/billion"
  - Proceeds-specific phrasing: "aggregate net/gross proceeds of
    approximately $X"

Run with: python scripts/41_extract_financing_candidates.py

Input:  data/processed/final_roster.csv
        data/raw/s1_html/{cik}.html (already cached)
Output: data/processed/financing_candidates.csv
"""

import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

ROSTER_PATH = Path("data/processed/final_roster.csv")
S1_HTML_DIR = Path("data/raw/s1_html")
OUT_PATH = Path("data/processed/financing_candidates.csv")

SERIES_ROUND_RE = re.compile(
    r"Series\s+[A-F](?:-1|-2)?\s+(?:convertible\s+)?preferred\s+stock",
    re.IGNORECASE,
)
DOLLAR_RE = re.compile(
    r"\$\s?[\d,]+(?:\.\d+)?\s*(?:million|thousand|billion)",
    re.IGNORECASE,
)
PROCEEDS_RE = re.compile(
    r"(?:aggregate\s+)?(?:net|gross)\s+proceeds\s+of\s+approximately\s+"
    r"\$\s?[\d,]+(?:\.\d+)?\s*(?:million|thousand)",
    re.IGNORECASE,
)


def extract_paragraphs(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "table"]):
        tag.decompose()
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    if not paragraphs:
        text = soup.get_text("\n")
        paragraphs = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    return paragraphs


def find_financing_sentences(paragraphs: list) -> list:
    candidates = []
    for para in paragraphs:
        sentences = re.split(r"(?<=[.!?])\s+", para)
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            has_series = bool(SERIES_ROUND_RE.search(sent))
            has_dollar = bool(DOLLAR_RE.search(sent))
            if has_series or has_dollar:
                candidates.append({
                    "sentence": sent[:500],
                    "mentions_round": has_series,
                    "mentions_dollar_amount": has_dollar,
                    "has_proceeds_phrasing": bool(PROCEEDS_RE.search(sent)),
                })
    return candidates


if __name__ == "__main__":
    roster = pd.read_csv(ROSTER_PATH, dtype={"cik": str})
    roster["cik"] = roster["cik"].str.zfill(10)
    print(f"Extracting financing candidates for {len(roster)} companies.")

    rows = []
    no_cache = 0
    for i, row in roster.iterrows():
        html_path = S1_HTML_DIR / f"{row['cik']}.html"
        if not html_path.exists():
            no_cache += 1
            continue

        html = html_path.read_text(encoding="utf-8", errors="ignore")
        paragraphs = extract_paragraphs(html)
        candidates = find_financing_sentences(paragraphs)

        for rank, cand in enumerate(candidates):
            rows.append({
                "company_name": row["company_name"], "cik": row["cik"],
                "sentence_rank": rank, **cand,
            })

        if (i + 1) % 50 == 0:
            print(f"{i + 1}/{len(roster)} processed")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUT_PATH, index=False)

    companies_with_hits = out_df["cik"].nunique() if len(out_df) else 0
    print(f"\n{no_cache} companies had no cached S-1, skipped, not the same "
          "as zero financing, just no local file to search.")
    print(f"{companies_with_hits} of {len(roster) - no_cache} companies "
          f"with a cached S-1 produced at least one candidate sentence.")
    print(f"{len(out_df)} total candidate sentences written to {OUT_PATH}.")
    print("\nThis is a candidate list, not a finished feature. Next step "
          "is turning the highest-value candidates (proceeds phrasing "
          "especially) into actual per-company totals, that needs a "
          "review pass, not another blind regex layer.")
