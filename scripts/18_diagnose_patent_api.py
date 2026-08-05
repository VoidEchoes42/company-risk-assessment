"""
Diagnostic, not the real extraction script yet: test USPTO's post-migration
patent search API against a few known biotech companies before committing
to a full 416-company build. Two things documentation alone couldn't
confirm: the exact auth header format, and whether assignee_organization
does partial or exact matching. This settles both on real evidence.

BEFORE RUNNING: paste your free API key (from data.uspto.gov/apis/getting-started)
into API_KEY below.

Run with: python scripts/18_diagnose_patent_api.py
"""

import requests

API_KEY = "PASTE_YOUR_KEY_HERE"
BASE_URL = "https://api.uspto.gov/api/v1/patentsview/patents"

# Trying the most commonly used USPTO ODP header name first. If this
# comes back 401/403, that alone tells us the header name is wrong
# rather than the key itself, an easy thing to fix once we see it.
HEADERS = {"X-Api-Key": API_KEY}

# Companies I have independent confidence should have real patents, one
# already fully verified elsewhere in this project (Kythera developed
# Kybella, an approved drug, definitely patented).
KNOWN_COMPANIES = ["Kythera Biopharmaceuticals", "Verastem", "Agios Pharmaceuticals"]


def query_patents(company_name: str):
    query = f'{{"assignees.assignee_organization":"{company_name}"}}'
    fields = '["patent_id","patent_title","patent_date","assignees.assignee_organization"]'
    params = {"q": query, "f": fields}

    print(f"\n{'='*70}\nQuerying: {company_name!r}")
    resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
    print(f"HTTP status: {resp.status_code}")
    print(f"Full URL requested: {resp.url}")

    if resp.status_code == 401 or resp.status_code == 403:
        print("Auth failure. This means the header name or key format is "
              "wrong, not necessarily that the key itself is bad. Response "
              f"body: {resp.text[:300]}")
        return

    if resp.status_code != 200:
        print(f"Non-200, non-auth error. Response body: {resp.text[:300]}")
        return

    data = resp.json()
    print(f"Raw top-level keys in response: {list(data.keys())}")
    print(f"Full raw response (first 1000 chars): {str(data)[:1000]}")


if __name__ == "__main__":
    if API_KEY == "PASTE_YOUR_KEY_HERE":
        print("Set API_KEY at the top of this script before running.")
        raise SystemExit(1)

    for name in KNOWN_COMPANIES:
        query_patents(name)

    print(f"\n{'='*70}")
    print("What to look for in the output above:")
    print("1. Did any query return HTTP 200 with real patent data? If so, "
          "auth and query syntax both work, note the field names shown.")
    print("2. Did 'Kythera Biopharmaceuticals' return an exact-looking "
          "match, or did it also pull in unrelated companies? That tells "
          "us if assignee_organization needs an exact string or tolerates "
          "partial matches.")
    print("3. If everything came back 401/403, the header name is likely "
          "wrong, paste this full output and we'll try the alternatives.")
