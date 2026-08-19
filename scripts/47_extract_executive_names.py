"""
Step 4.2e (part 1, fast version): Extract founder/executive names from
cached S-1s using regex on raw text (no BeautifulSoup — much faster).

S-1s have an executive officers section with names and titles.
We extract names near scientific/medical titles and save them for
PubMed lookup.
"""
import json
import re
from pathlib import Path

import pandas as pd

S1_DIR = Path("data/raw/s1_html")
ROSTER_PATH = Path("data/processed/final_roster.csv")
OUT_PATH = Path("data/processed/executive_names_raw.csv")

# Strip HTML tags quickly
TAG_RE = re.compile(r"<[^>]+>")
MULTI_SPACE = re.compile(r"[ \t]+")
MULTI_NEWLINE = re.compile(r"\n{3,}")

# Scientific/medical leadership titles
SCIENTIFIC_TITLES = re.compile(
    r"(?:Chief\s+Scientific\s+Officer|Chief\s+Medical\s+Officer|"
    r"Chief\s+Development\s+Officer|"
    r"(?:President|VP|Vice\s+President).*?(?:Research|Science|Development|Scientific)|"
    r"(?:Head\s+of|Director).*?(?:Research|Development|Science)|"
    r"Scientific\s+Founder|Co-Founder|Founder[^s]|"
    r"Chief\s+Executive\s+Officer)",
    re.IGNORECASE,
)

# Name extraction: "FirstName LastName" patterns, excluding company names
NAME_RE = re.compile(
    r"\b([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)\b"
)

# Words that are NOT names (false positives)
NOT_NAMES = {
    "Table Contents", "United States", "Securities Act", "Exchange Act",
    "Clinical Trials", "Food Drug", "Food and Drug", "Code Federal",
    "Public Company", "Sarbanes Oxley", "Jumpstart Our", "Emerging Growth",
    "Large Accelerated", "Accelerated Filer", "Non Accelerated",
    "Smaller Reporting", "Risk Factors", "Forward Looking",
    "Selected Financial", "Summary Financial", "Prospectus Summary",
    "Prospectus Supplement", "Registration Statement", "Business Strategy",
    "Market Opportunity", "Product Pipeline", "Intellectual Property",
    "Management Discussion", "Financial Statements", "Notes to Financial",
    "Significant Estimates", "Revenue Recognition", "Stock Based",
    "Defined Benefit", "Retirement Plan", "Income Taxes", "Leases",
    "Commitments Contingencies", "Subsequent Events", "Stock Options",
    "Warrants Outstanding", "Preferred Stock", "Common Stock",
    "Convertible Preferred", "Rights Agreement", "Equity Incentive",
    "Employee Stock", "Directors Executive", "Board Directors",
    "Compensation Discussion", "Compensation Tables", "Summary Compensation",
    "Grants Plan", "Outstanding Equity", "Option Exercises",
    "Pension Benefits", "Nonqualified Deferred", "Director Compensation",
    "Audit Committee", "Nominating Committee", "Compensation Committee",
    "Corporate Governance", "Code Conduct", "Related Party",
    "Principal Accountant", "Independent Registered", "Legal Matters",
    "Experts Reports", "Index Financial", "Where You Can Find",
    "Information Registrant", "Incorporated Delaware", "Delaware Corporation",
    "File Number", "Commission File", "Irs Identification",
    "State Irs", "Zip Code", "Telephone Number", "Facsimile Number",
    "Email Address", "Web Site", "Internet Address", "Official Statement",
    "Accuracy Not", "Information Not", "Forward Looking Statements",
    "Safe Harbor", "Cautionary Statement", "Risk Factors You",
    "Should Carefully", "Investment Risk", "Losses May", "Operating Results",
    "Fluctuate Significantly", "Quarterly Results", "Seasonal Variations",
    "Rely Single", "Single Product", "Product Candidates", "Clinical Development",
    "Regulatory Approval", "Marketing Approval", "Investigational New",
    "New Drug", "Biologics License", "Breakthrough Therapy", "Fast Track",
    "Priority Review", "Orphan Drug", "Accelerated Approval",
    "Special Protocol", "Pediatric Exclusivity", "Qualified Infectious",
    "Regenerative Medicine", "Compassionate Use", "Expanded Access",
    "Manufacturing Commercialization", "Supply Chain", "Commercial Scale",
    "Competition Competition", "Competitive Landscape", "Market Share",
    "Large Competitors", "Pharmaceutical Companies", "Biotechnology Companies",
    "Research Organizations", "Academic Institutions", "Government Agencies",
    "Intellectual Property Rights", "Patent Protection", "Patent Term",
    "Patent Applications", "Issued Patents", "Patent Litigation",
    "Patent Office", "United States Patent", "Trademark Matters",
    "Proprietary Rights", "Trade Secrets", "Confidential Information",
    "Employee Relations", "Labor Matters", "Union Representation",
    "Workforce Size", "Contractors Consultants", "Third Parties",
    "Collaboration Agreements", "Licensing Arrangements", "In License",
    "Out License", "Strategic Alliance", "Joint Venture",
    "Material Agreements", "Significant Customers", "Vendor Relationships",
    "Government Contracts", "Grant Funding", "Non Government",
    "Properties Facilities", "Leased Property", "Owned Property",
    "Research Facilities", "Manufacturing Facilities", "Corporate Office",
    "Legal Proceedings", "Pending Litigation", "Settled Claims",
    "Governmental Investigations", "Stockholder Proposals",
    "Shareholder Rights", "Anti Takeover", "Poison Pill",
    "Change Control", "Control Change", "Change Ownership",
    "Beneficial Owners", "Five Percent", "Ten Percent",
    "Stock Ownership", "Equity Securities", "Debt Securities",
    "Convertible Notes", "Senior Notes", "Credit Facility",
    "Revolving Credit", "Term Loan", "Bridge Loan",
    "Off Balance Sheet", "Contractual Obligations", "Contractual Commitments",
    "Material Contracts", "Exhibit List", "Form K", "Form Q",
    "Form D", "Form S", "Form F", "Current Report",
    "Periodic Report", "Annual Report", "Proxy Statement",
    "Information Statement", "Consent Solicitation",
}


def strip_html(html: str) -> str:
    """Fast HTML to text conversion."""
    text = TAG_RE.sub(" ", html)
    text = MULTI_SPACE.sub(" ", text)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    text = "\n".join(lines)
    text = MULTI_NEWLINE.sub("\n\n", text)
    return text


def extract_exec_names(html: str) -> list[dict]:
    """Extract executive names with scientific titles from S-1 HTML."""
    text = strip_html(html)
    lines = text.split("\n")

    results = []
    seen_names = set()

    for line in lines:
        if not SCIENTIFIC_TITLES.search(line):
            continue

        # Extract names from this line
        candidates = NAME_RE.findall(line)

        for name in candidates:
            name = name.strip()
            # Skip obvious non-names
            if name in NOT_NAMES:
                continue
            if any(fp in name for fp in NOT_NAMES):
                continue
            if len(name.split()) < 2:
                continue
            if all(len(w) <= 2 for w in name.split()):
                continue
            # Skip if contains company-like words
            if re.search(r"(?:Inc|Corp|LLC|Ltd|Bio|Thera|Gene|Cell|Pharma|Medic|Health|Science|Vax|Immun)", name, re.IGNORECASE):
                continue

            if name not in seen_names:
                seen_names.add(name)
                results.append({
                    "executive_name": name,
                    "title_context": line[:200],
                })

    return results


if __name__ == "__main__":
    import time
    start = time.time()

    roster = pd.read_csv(ROSTER_PATH, dtype={"cik": str})
    roster["cik"] = roster["cik"].str.zfill(10)

    rows = []
    no_s1 = 0
    empty_section = 0
    total = len(roster)

    for i, (_, row) in enumerate(roster.iterrows()):
        html_path = S1_DIR / f"{row['cik']}.html"
        if not html_path.exists():
            no_s1 += 1
            continue

        html = html_path.read_text(encoding="utf-8", errors="ignore")
        execs = extract_exec_names(html)

        if not execs:
            empty_section += 1
            continue

        for e in execs:
            rows.append({
                "cik": row["cik"],
                "company_name": row["company_name"],
                "executive_name": e["executive_name"],
                "title_context": e["title_context"],
            })

        if (i + 1) % 50 == 0:
            elapsed = time.time() - start
            print(f"{i + 1}/{total} ({elapsed:.0f}s) — {len(rows)} names so far, {empty_section} empty sections")

    out_df = pd.DataFrame(rows)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(OUT_PATH, index=False)

    elapsed = time.time() - start
    print(f"\n=== Executive Names Extraction ===")
    print(f"Elapsed: {elapsed:.0f}s")
    print(f"Roster companies: {total}")
    print(f"Companies with cached S-1: {total - no_s1}")
    print(f"Companies with executive names: {out_df['cik'].nunique()}")
    print(f"Total name records: {len(out_df)}")
    print(f"No S-1 cache: {no_s1}")
    print(f"S-1 found but no exec section matched: {empty_section}")
    print(f"\nWritten to {OUT_PATH}")

    # Show samples
    print(f"\n=== Sample ===")
    for _, r in out_df.head(25).iterrows():
        print(f"  {r['company_name'][:40]:40s}  {r['executive_name']:30s}  {r['title_context'][:80]}")
