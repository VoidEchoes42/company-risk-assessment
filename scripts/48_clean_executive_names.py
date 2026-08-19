"""
Step 4.2e (part 2, strict): Second-pass cleaning of executive names.

Adds aggressive filters:
  - Geographic locations (Los Angeles, San Francisco, etc.)
  - Stock/security terms (Ordinary Shares, Common Stock, etc.)
  - Legal/audit firm names (Friedberg, Wolf, etc.)
  - Company names that look like person names (Menlo, Celsus, etc.)
  - Section headers and document structure terms
  - Titles and roles (Interim Head, Development Services, etc.)
  - Academic departments (Anderson School, etc.)
  - Single-word or obviously non-person entries
"""
import re
import pandas as pd

from pathlib import Path

RAW_PATH = Path("data/processed/executive_names_raw.csv")
OUT_PATH = Path("data/processed/executive_names_clean.csv")

# Known US cities that appear in S-1s
CITIES = {
    "los angeles", "san francisco", "new york", "boston", "san diego",
    "south san", "san mateo", "palo alto", "mountain view", "sunnyvale",
    "santa clara", "oakland", "seattle", "portland", "chicago",
    "philadelphia", "washington dc", "bethesda", "rockville", "gaithersburg",
    "austin", "houston", "dallas", "denver", "phoenix", "salt lake city",
    "minneapolis", "baltimore", "durham", "raleigh", "chapel hill",
    "research triangle", "princeton", "newark", "camden",
    "cambridge", "boston", "waltham", "watertown", "lexington",
    "westborough", "hopkinton", "framingham", "natick",
    "london", "oxford", "cambridge uk", "basel", "zurich", "geneva",
    "paris", "berlin", "munich", "amsterdam", "copenhagen", "stockholm",
    "toronto", "vancouver", "montreal", "sydney", "melbourne",
    "tokyo", "osaka", "singapore", "hong kong", "shanghai", "beijing",
    "boulder", "longmont", "fort collins", "colorado springs",
    "irvine", "newport beach", "santa monica", "beverly hills",
    "redwood city", "menlo park", "burlingame", "mill valley",
    "laguna niguel", "lake forest", "aliso viejo",
    "king of prussia", "malvern", "wayne", "horsham",
    "south san francisco", "emeryville", "richmond", "berkeley",
    "dublin", "pleasanton", "livermore", "fremont", "hayward",
    "miami", "fort lauderdale", "boca raton", "palm beach",
    "atlanta", "charlotte", "nashville", "orlando", "tampa",
    "kansas city", "st louis", "indianapolis", "columbus", "cincinnati",
    "pittsburgh", "detroit", "cleveland", "milwaukee", "madison",
}

# Stock/security terms
STOCK_TERMS = {
    "ordinary shares", "common stock", "preferred stock", "convertible preferred",
    "voting stock", "non voting", "class a", "class b", "class c",
    "restricted stock", "performance shares", "phantom stock",
    "stock options", "stock appreciation", "restricted stock units",
    "equity awards", "equity incentive", "employee stock",
    "shareholder rights", "poison pill", "rights agreement",
    "warrants outstanding", "warrant agreement",
}

# Known non-person words/phrases that slip through
KNOWN_NOISE = {
    "los angeles", "san francisco", "new york", "south san", "san diego",
    "boston", "seattle", "chicago", "philadelphia", "washington dc",
    "bethesda", "austin", "boulder", "irvine", "santa monica",
    "ordinary shares", "common stock", "preferred stock",
    "development services", "interim head", "business development",
    "executive chairman", "executive director", "executive officers",
    "street reform", "friedberg mercantile", "quantum dot",
    "anderson school", "harvard medical", "johns hopkins", "stanford university",
    "uc san", "ucla", "ucsf", "uc berkeley", "uc davis",
    "massachusetts general", "brigham women", "memorial sloan",
    "city hope", "city of hope", "dana farber", "broad institute",
    "whitehead institute", "salk institute", "scripps research",
    "children hospital", "children's hospital", "national institutes",
    "nih", "fda", "ema", "who", "cdc", "cms",
    "pfizer inc", "roche holding", "novartis ag", "merck co",
    "sanofi sa", "glaxosmithkline", "astrazeneca plc", "johnson johnson",
    "bristol myers", "eli lilly", "abbvie inc", "amgen inc",
    "gilead sciences", "regeneron pharmaceuticals", "biogen inc",
    "vertex pharmaceuticals", "seagen inc", "exelixis inc",
    "exxon mobil", "chevron corporation", "conocophillips",
    "halliburton company", "schlumberger nv",
    "united states", "united kingdom", "european union",
    "from april", "from inception", "from date", "from time",
    "our chief", "the company", "each director", "all directors",
    "certain officers", "key employees", "named executive",
    "compensation discussion", "summary compensation",
    "grants plan", "outstanding equity", "option exercises",
    "pension benefits", "nonqualified deferred", "director compensation",
    "audit committee", "nominating committee", "compensation committee",
    "corporate governance", "code conduct", "related party",
    "principal accountant", "independent registered", "legal matters",
    "experts reports", "index financial", "where you can find",
    "information registrant", "incorporated delaware", "delaware corporation",
    "commission file", "irs identification", "telephone number",
    "facsimile number", "email address", "web site", "internet address",
    "official statement", "safe harbor", "cautionary statement",
    "investor relations", "shareholder rights", "anti takeover",
    "beneficial owners", "stock ownership", "equity securities",
    "debt securities", "credit facility", "revolving credit",
    "term loan", "bridge loan", "off balance sheet",
    "contractual obligations", "contractual commitments",
    "material contracts", "exhibit list", "form k", "form q",
    "form d", "form s", "form f", "current report",
    "periodic report", "annual report", "proxy statement",
    "information statement", "consent solicitation",
    "change control", "change ownership",
    "material adverse", "significant adverse", "adverse effect",
    "forward looking", "risk factors you", "should carefully",
    "investment risk", "losses may", "operating results",
    "fluctuate significantly", "quarterly results", "seasonal variations",
    "rely single", "single product", "product candidates",
    "clinical development", "regulatory approval", "marketing approval",
    "investigational new", "new drug", "biologics license",
    "breakthrough therapy", "fast track", "priority review",
    "orphan drug", "accelerated approval", "special protocol",
    "pediatric exclusivity", "qualified infectious",
    "regenerative medicine", "compassionate use", "expanded access",
    "manufacturing commercialization", "supply chain", "commercial scale",
    "competitive landscape", "market share", "large competitors",
    "pharmaceutical companies", "biotechnology companies",
    "research organizations", "academic institutions", "government agencies",
    "intellectual property rights", "patent protection", "patent term",
    "patent applications", "issued patents", "patent litigation",
    "patent office", "united states patent", "trademark matters",
    "proprietary rights", "trade secrets", "confidential information",
    "employee relations", "labor matters", "union representation",
    "workforce size", "contractors consultants", "third parties",
    "collaboration agreements", "licensing arrangements", "in license",
    "out license", "strategic alliance", "joint venture",
    "material agreements", "significant customers", "vendor relationships",
    "government contracts", "grant funding", "non government",
    "properties facilities", "leased property", "owned property",
    "research facilities", "manufacturing facilities", "corporate office",
    "legal proceedings", "pending litigation", "settled claims",
    "governmental investigations", "stockholder proposals",
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
    "monday", "tuesday", "wednesday", "thursday", "friday",
    "saturday", "sunday",
}

# Patterns that indicate a non-person even if it looks name-like
NOISE_PATTERNS = [
    r"(?:Street|Avenue|Boulevard|Drive|Lane|Way|Place|Court|Circle|Road|Highway|Parkway|Expressway)",
    r"(?:LLP|LLC|LP|PC|PA|DO|DDS|MD|PhD|JD|Esq|CPA|CFA)",
    r"(?:School|College|University|Institute|Hospital|Center|Centre|Foundation|Trust|Fund|Academy)",
    r"(?:Ventures|Capital|Partners|Associates|Holdings|Enterprises|Solutions|Technologies|Laboratories|Group|International|Global|Worldwide)",
    r"(?:Department|Division|Section|Unit|Branch|Office|Agency|Bureau|Authority|Commission|Board|Committee)",
    r"(?:Agreement|Contract|Arrangement|Understanding|Commitment|Obligation|Transaction|Deal|Proposal|Offer)",
    r"(?:Shareholder|Shareholder|Stockholder|Investor|Lender|Creditor|Debtor|Borrower)",
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)",
    r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)",
    r"(?:City|Town|Village|Borough|Township|County|Parish|Province|State|Country|Nation|Territory|Region|District|Zone|Area|Sector|Precinct)",
    r"(?:Street Reform|Securities Regulation|Market Regulation)",
]

# US state abbreviations (not names)
STATE_ABBREVS = {
    "al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga",
    "hi", "id", "il", "in", "ia", "ks", "ky", "la", "me", "md",
    "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", "nh", "nj",
    "nm", "ny", "nc", "nd", "oh", "ok", "or", "pa", "ri", "sc",
    "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv", "wi", "wy",
    "dc", "pr", "vi", "gu", "as", "mp",
}


def is_person_name(name: str) -> bool:
    """Strict check: does this look like an actual person's name?"""
    parts = name.split()
    if len(parts) < 2 or len(parts) > 4:
        return False

    # Check against known noise
    lower = name.lower()
    if lower in KNOWN_NOISE:
        return False
    if any(noise in lower for noise in KNOWN_NOISE):
        return False
    for pat in NOISE_PATTERNS:
        if re.search(pat, name, re.IGNORECASE):
            return False

    # Check for title patterns
    for pat in TITLE_PATTERNS:
        if re.search(pat, name, re.IGNORECASE):
            return False

    # Check for org words
    for word in ORG_WORDS:
        if word in lower:
            return False

    # All words should start with uppercase (proper names)
    for part in parts:
        if not part[0].isupper():
            return False

    # The last word should not be a state abbreviation
    if parts[-1].lower() in STATE_ABBREVS:
        return False

    return True


# Import ORG_WORDS from the broader module context — redefine here
ORG_WORDS = {
    "securities", "exchange", "commission", "act", "federal",
    "registration", "statement", "prospectus", "underwriter", "underwriters",
    "investor", "investors", "shareholder", "shareholders", "stockholder",
    "stockholders", "director", "directors", "officer", "officers",
    "board", "committee", "management", "administrative", "general",
    "total", "average", "median", "maximum", "minimum", "aggregate",
    "individual", "individuals", "persons", "person", "people",
    "employees", "consultants", "contractors", "advisors",
    "proceeds", "revenue", "income", "expenses", "assets", "liabilities",
    "capital", "financing", "funding", "investment", "investments",
    "clinical", "trial", "trials", "patient", "patients", "study", "studies",
    "product", "products", "therapy", "therapies", "treatment", "treatments",
    "drug", "drugs", "candidate", "candidates", "pipeline", "program",
    "programs", "indication", "indications", "disease", "diseases",
    "patent", "patents", "license", "licenses", "approval", "approvals",
    "reimbursement", "commercial", "commercialization", "marketing",
    "sales", "distribution", "partner", "partners", "collaboration",
    "licensee", "licensor", "acquisition", "divestiture",
    "amendment", "amendments", "modification", "modifications",
    "agreement", "agreements", "contract", "contracts",
    "material", "adverse", "significant", "substantial", "considerable",
    "comparable", "similar", "competitive", "competition",
    "regulatory", "legislative", "statutory", "administrative",
    "international", "national", "regional", "local", "global",
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "first", "second", "third", "fourth", "fifth",
}

TITLE_PATTERNS = [
    r"^(?:Chief|President|Vice|Executive|Director|Head|Senior|General|Managing|Founder|Co.Founder|Chairman|Chair)",
    r"(?:Officer|Director|Officers|Directors|Committee|Board|Members|Management|Team|Group|Department)$",
    r"(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)$",
    r"^(?:Mr|Mrs|Ms|Dr|Prof)$",
]

MULTI_SPACE = re.compile(r"\s+")


def clean_name(name: str) -> str:
    """Strip HTML entities and normalize whitespace."""
    name = name.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    name = MULTI_SPACE.sub(" ", name).strip()
    return name


if __name__ == "__main__":
    raw = pd.read_csv(RAW_PATH, dtype={"cik": str})
    raw["cik"] = raw["cik"].str.zfill(10)
    print(f"Raw records: {len(raw)}")

    kept = []
    seen = set()

    for _, row in raw.iterrows():
        name = clean_name(row["executive_name"])
        if not is_person_name(name):
            continue
        key = (row["cik"], name)
        if key in seen:
            continue
        seen.add(key)
        kept.append({
            "cik": row["cik"],
            "company_name": row["company_name"],
            "executive_name": name,
            "title_context": row["title_context"],
        })

    out_df = pd.DataFrame(kept)
    out_df.to_csv(OUT_PATH, index=False)

    print(f"Cleaned records: {len(out_df)}")
    print(f"Companies with cleaned names: {out_df['cik'].nunique()}")
    print(f"Removed {len(raw) - len(out_df)} non-person entries")

    print(f"\n=== Sample cleaned names ===")
    for _, r in out_df.head(30).iterrows():
        print(f"  {r['company_name'][:40]:40s}  {r['executive_name']}")

    print(f"\n=== Companies with most execs (should be reasonable now) ===")
    counts = out_df.groupby("company_name").size().sort_values(ascending=False)
    print(counts.head(15).to_string())

    print(f"\n=== Bottom of distribution ===")
    print(counts.tail(10).to_string())
