"""
Step 4.2e (hybrid): PubMed publication counts via affiliation queries,
with author-disambiguation fallback for noisy results.

Strategy:
  1. Query affiliation for each company (pre-IPO year only)
  2. Flag implausibly high counts (>3000) as noisy — likely generic name
     matching unrelated organizations
  3. For noisy companies, query individual authors from S-1 executive names
  4. Use the lower, more precise author count for noisy companies
"""
import re
import time
from pathlib import Path

import pandas as pd
from urllib.request import Request, urlopen

BASE = Path("data/processed")
ROSTER_PATH = BASE / "final_roster.csv"
NAMES_PATH = BASE / "executive_names_clean.csv"
OUT_PATH = BASE / "publication_features.csv"

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
REQUEST_DELAY = 0.32
NCBI_EMAIL = "research@example.com"
NCBI_TOOL = "biotech_ipo_v3"
NOISY_THRESHOLD = 3000  # counts above this are likely generic name matches


def pubmed_search(query: str, max_year: int = None) -> int:
    params = [
        ("db", "pubmed"),
        ("term", query),
        ("retmax", "0"),
        ("tool", NCBI_TOOL),
        ("email", NCBI_EMAIL),
    ]
    if max_year:
        params += [
            ("datetype", "pdat"),
            ("mindate", "1900/01/01"),
            ("maxdate", f"{max_year}/12/31"),
        ]
    url = EUTILS + "/esearch.fcgi?" + "&".join(f"{k}={v}" for k, v in params)
    try:
        req = Request(url, headers={"User-Agent": NCBI_TOOL})
        with urlopen(req, timeout=15) as resp:
            data = resp.read().decode("utf-8")
    except Exception:
        return 0
    m = re.search(r"<Count>(\d+)</Count>", data)
    return int(m.group(1)) if m else 0


def clean_company_for_pubmed(name: str) -> str:
    name = re.sub(
        r"\b(?:Inc\.?|Corp\.?|Corporation|LLC|Ltd\.?|Limited|PLC|"
        r"Holdings?|Group|International|Enterprises?|Ventures?|"
        r"Technologies?|Solutions?|Therapeutics?|Pharmaceuticals?|Pharma|"
        r"Biotherapeutics?|Biosciences?|Diagnostics?|Laboratories?|"
        r"Institutes?|Foundations?|Partners?|Associates?|Capital)\b",
        "", name, flags=re.IGNORECASE,
    )
    name = re.sub(r"\s+", " ", name).strip(" ,.")
    return name.strip(" .,")


def is_valid_name(name: str) -> bool:
    parts = name.split()
    if len(parts) < 2 or len(parts) > 4:
        return False
    if not all(p[0].isupper() for p in parts):
        return False
    bad = {"Inc","Corp","LLC","Ltd","Bio","Thera","Pharma","Health","Science",
           "Research","Institute","University","Hospital","Center","Foundation",
           "Trust","Fund","Ventures","Capital","Partners","Associates","Group"}
    if parts[-1] in bad:
        return False
    return True


if __name__ == "__main__":
    start_time = time.time()

    roster = pd.read_csv(ROSTER_PATH, dtype={"cik": str})
    roster["cik"] = roster["cik"].str.zfill(10)
    roster["ipo_year"] = pd.to_datetime(roster["ipo_date"], errors="coerce").dt.year

    # Load executive names for fallback
    names_df = pd.read_csv(NAMES_PATH, dtype={"cik": str})
    names_df["cik"] = names_df["cik"].str.zfill(10)

    rows = []
    total = len(roster)

    for i, row_tuple in enumerate(roster.iterrows()):
        _, row = row_tuple
        cik = row["cik"]
        company = row["company_name"]
        ipo_year = row["ipo_year"]
        query = clean_company_for_pubmed(company)

        pubmed_pre_ipo = 0
        method = "none"
        authors_used = 0

        if query and len(query) >= 3 and pd.notna(ipo_year):
            affil_q = f'"{query}"[Affiliation]'
            affil_count = pubmed_search(affil_q, max_year=int(ipo_year))
            time.sleep(REQUEST_DELAY)

            if affil_count > NOISY_THRESHOLD:
                # Fallback: use individual author queries
                co_names = names_df[names_df["cik"] == cik]
                valid = [n for n in co_names["executive_name"].unique() if is_valid_name(n)][:5]
                author_total = 0
                for name in valid:
                    aq = f'"{name}"[Author]'
                    cnt = pubmed_search(aq, max_year=int(ipo_year))
                    time.sleep(REQUEST_DELAY)
                    author_total += cnt
                pubmed_pre_ipo = author_total
                method = "author_disambiguated"
                authors_used = len(valid)
            else:
                pubmed_pre_ipo = affil_count
                method = "affiliation"
        else:
            method = "no_query"

        rows.append({
            "cik": cik,
            "company_name": company,
            "pubmed_pre_ipo_count": pubmed_pre_ipo,
            "pubmed_query_method": method,
            "pubmed_authors_queried": authors_used,
        })

        if (i + 1) % 25 == 0:
            elapsed = time.time() - start_time
            print(f"  {i + 1}/{total} ({elapsed:.0f}s)")

    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUT_PATH, index=False)

    elapsed = time.time() - start_time
    has_pubs = out_df[out_df["pubmed_pre_ipo_count"] > 0]
    nonzero = has_pubs[has_pubs["pubmed_pre_ipo_count"] > 0]
    noisy = out_df[out_df["pubmed_query_method"] == "author_disambiguated"]

    print(f"\n=== PubMed Publication Features ===")
    print(f"Elapsed: {elapsed:.0f}s")
    print(f"Total companies: {len(out_df)}")
    print(f"With pre-IPO publications: {len(has_pubs)}")
    print(f"Zero pre-IPO publications: {len(out_df) - len(has_pubs)}")
    print(f"Used affiliation query: {(out_df['pubmed_query_method'] == 'affiliation').sum()}")
    print(f"Used author disambiguation: {len(noisy)}")
    if len(nonzero) > 0:
        print(f"  Mean (nonzero): {nonzero['pubmed_pre_ipo_count'].mean():.1f}")
        print(f"  Median (nonzero): {nonzero['pubmed_pre_ipo_count'].median():.1f}")
        print(f"  Max: {nonzero['pubmed_pre_ipo_count'].max()}")

    print(f"\nTop 15 by pre-IPO publications:")
    for _, r in out_df.nlargest(15, "pubmed_pre_ipo_count").iterrows():
        print(f"  {r['company_name'][:45]:45s}  {r['pubmed_pre_ipo_count']:>5}  [{r['pubmed_query_method'][:15]}]")

    print(f"\nWritten to {OUT_PATH}")
