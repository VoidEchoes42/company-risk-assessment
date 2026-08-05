"""
Step 4.2b: Pull patent features per company from Google's public BigQuery
mirror of PatentsView data. Alternative to USPTO's own API, chosen
specifically to avoid that registration's personal-information request.

Schema confirmed directly against live query results, not guessed:
  assignee(id, organization)
  patent_assignee(patent_id, assignee_id, location_id)
  application(id, patent_id, series_code, number, country, date)
  patent(id, type, number, country, date, ...)

Deliberately uses application.date (filing date), not patent.date (grant
date). Patents typically take 2 to 5 years to grant, so grant date would
badly undercount young companies: a biotech that filed patents the year
before its IPO would show zero patents under a grant-date filter, even
though "N patents pending" is a real, S-1-visible signal an investor
would have seen. Filing date is what actually existed at decision time,
consistent with the leakage rule used for every other feature so far.

SETUP (no personal-info registration required, unlike the USPTO path):
  pip install google-cloud-bigquery
  Install the Google Cloud CLI if you don't already have it:
    https://cloud.google.com/sdk/docs/install
  gcloud auth application-default login
    (opens a browser, sign in with the same Google account used for the
    BigQuery console, that is the only login step this needs)
  Set PROJECT_ID below to your own project ID (top-left of the BigQuery
  console, or under IAM & Admin > Settings).

Run with: python scripts/19_fetch_patent_features.py

Input:  data/processed/final_roster.csv
Output: data/processed/patent_features.csv
"""

import re
from pathlib import Path

import pandas as pd
from google.cloud import bigquery

ROSTER_PATH = Path("data/processed/final_roster.csv")
OUT_PATH = Path("data/processed/patent_features.csv")

PROJECT_ID = "bio-patent-project"

SUFFIXES = {
    "INC", "INCORPORATED", "CORP", "CORPORATION", "LTD", "LIMITED", "LLC",
    "PLC", "CO", "COMPANY", "HOLDING", "HOLDINGS", "GROUP", "BV", "NV", "SA",
    "AG", "SE", "THE",
}

QUERY = """
    SELECT a.organization, pa.patent_id, app.date AS filing_date
    FROM `patents-public-data.patentsview.assignee` a
    JOIN `patents-public-data.patentsview.patent_assignee` pa
      ON a.id = pa.assignee_id
    JOIN `patents-public-data.patentsview.application` app
      ON pa.patent_id = app.patent_id
    WHERE UPPER(a.organization) LIKE UPPER(@search_pattern)
"""


def normalize_name(name: str) -> set:
    name = str(name).upper().replace(".", "")
    name = re.sub(r"[^A-Z0-9 ]", " ", name)
    return {t for t in name.split() if t not in SUFFIXES}


def name_match_score(a: str, b: str) -> float:
    ta, tb = normalize_name(a), normalize_name(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def clean_name_for_search(company_name: str) -> str:
    tokens = [t for t in re.split(r"[,\.\s]+", str(company_name))
              if t.upper() not in SUFFIXES and t]
    return " ".join(tokens)


def fetch_patent_rows(client, company_name: str) -> list:
    search_term = clean_name_for_search(company_name)
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("search_pattern", "STRING", f"%{search_term}%")
        ]
    )
    result = client.query(QUERY, job_config=job_config).result()
    return [dict(row) for row in result]


def extract_features(company_name: str, ipo_date, rows: list) -> dict:
    ipo_ts = pd.to_datetime(ipo_date, errors="coerce")
    pre_ipo_patent_ids = set()

    for row in rows:
        org = row.get("organization", "")
        if name_match_score(company_name, org) < 0.5:
            continue  # not actually this company, a substring coincidence

        filing_ts = pd.to_datetime(row.get("filing_date"), errors="coerce")
        if pd.isna(filing_ts) or pd.isna(ipo_ts) or filing_ts >= ipo_ts:
            continue  # leakage guard: filed after IPO, or date unusable

        pre_ipo_patent_ids.add(row.get("patent_id"))

    return {"pre_ipo_patent_count": len(pre_ipo_patent_ids)}


if __name__ == "__main__":
    if PROJECT_ID == "PASTE_YOUR_GCP_PROJECT_ID_HERE":
        print("Set PROJECT_ID at the top of this script before running.")
        raise SystemExit(1)

    client = bigquery.Client(project=PROJECT_ID)
    roster = pd.read_csv(ROSTER_PATH)
    print(f"Fetching patent features for {len(roster)} companies.")

    rows_out = []
    for i, row in roster.iterrows():
        try:
            patent_rows = fetch_patent_rows(client, row["company_name"])
        except Exception as e:
            print(f"  Query failed for {row['company_name']!r}: {e}")
            patent_rows = []

        features = extract_features(row["company_name"], row["ipo_date"], patent_rows)
        rows_out.append({"company_name": row["company_name"], "cik": row["cik"], **features})

        if (i + 1) % 25 == 0:
            with_patents = sum(1 for r in rows_out if r["pre_ipo_patent_count"] > 0)
            print(f"{i + 1}/{len(roster)} done, {with_patents} with at least one matched patent so far")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame(rows_out)
    out_df.to_csv(OUT_PATH, index=False)

    zero = (out_df["pre_ipo_patent_count"] == 0).sum()
    print(f"\nWritten to {OUT_PATH}.")
    print(f"{zero} of {len(out_df)} companies show zero pre-IPO patents, "
          "plausible for younger or platform-early companies, not "
          "necessarily a bug, unlike the ClinicalTrials.gov case.")
