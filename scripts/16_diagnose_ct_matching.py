"""
Diagnostic, not part of the pipeline: fetch ClinicalTrials.gov results
for a small list of KNOWN companies (real pre-IPO trial history, verified
outside this script) and print exactly what's coming back, sponsor name,
collaborator names, name-match score, and start date, so we can see
precisely where the main script is losing real matches instead of
guessing again.

Run with: python scripts/16_diagnose_ct_matching.py
"""

import re

import requests

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
HEADERS = {"User-Agent": "Aman <your_email@example.com>"}

SUFFIXES = {
    "INC", "INCORPORATED", "CORP", "CORPORATION", "LTD", "LIMITED", "LLC",
    "PLC", "CO", "COMPANY", "HOLDING", "HOLDINGS", "GROUP", "BV", "NV", "SA",
    "AG", "SE", "THE",
}


def normalize_name(name):
    name = str(name).upper().replace(".", "")
    name = re.sub(r"[^A-Z0-9 ]", " ", name)
    return {t for t in name.split() if t not in SUFFIXES}


def name_match_score(a, b):
    ta, tb = normalize_name(a), normalize_name(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


# Companies with real, externally-verifiable pre-IPO trial history.
KNOWN_COMPANIES = ["Cempra, Inc.", "Kythera Biopharmaceuticals Inc", "Contrafect Corp"]


def diagnose(company_name):
    search_term = company_name.replace(",", "").replace(".", "")
    for suffix in ["Inc", "Corp", "Corporation"]:
        search_term = search_term.replace(suffix, "").strip()

    print(f"\n{'='*70}\nSearching for: {company_name!r} (query: {search_term!r})")
    resp = requests.get(
        BASE_URL,
        params={"query.spons": search_term, "pageSize": 20},
        headers=HEADERS,
        timeout=30,
    )
    print(f"HTTP status: {resp.status_code}")
    if resp.status_code != 200:
        print("Request itself failed, nothing to diagnose past this point.")
        return

    data = resp.json()
    studies = data.get("studies", [])
    print(f"Raw studies returned: {len(studies)} (totalCount: {data.get('totalCount')})")

    if not studies:
        print("Zero studies returned by the API itself, this means the "
              "SEARCH is the problem, not the filtering logic downstream.")
        return

    for study in studies[:10]:
        protocol = study.get("protocolSection", {})
        nct_id = protocol.get("identificationModule", {}).get("nctId")
        sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
        lead_sponsor = sponsor_module.get("leadSponsor", {}).get("name", "")
        collaborators = [c.get("name", "") for c in sponsor_module.get("collaborators", []) or []]
        status_module = protocol.get("statusModule", {})
        start_date = status_module.get("startDateStruct", {}).get("date")
        lead_score = name_match_score(company_name, lead_sponsor)

        print(f"\n  {nct_id}")
        print(f"    Lead sponsor: {lead_sponsor!r} (match score vs company: {lead_score:.2f})")
        print(f"    Collaborators: {collaborators}")
        print(f"    Start date: {start_date}")
        print(f"    Status: {status_module.get('overallStatus')}")
        if lead_score < 0.5:
            collab_scores = [name_match_score(company_name, c) for c in collaborators]
            best_collab = max(collab_scores) if collab_scores else 0.0
            print(f"    -> This is why it was excluded: lead sponsor score "
                  f"{lead_score:.2f} is below 0.5. Best collaborator score: "
                  f"{best_collab:.2f}.")


if __name__ == "__main__":
    for name in KNOWN_COMPANIES:
        diagnose(name)
