"""
Step 4.2d (fixed v2): Convert financing candidate sentences into structured
per-company financing features.

v2 improvements over v1:
  - Proceeds phrasing: unchanged, still gold standard
  - Round+dollar: now requires a financing-action keyword near the amount
    (proceeds, raised, sold, financing, private placement, etc.)
  - No double-counting when both signals fire
  - Hard cap at $5B per amount
  - Round-only sentences (no dollar nearby) are now ignored entirely
"""
import json
import re
from pathlib import Path

import pandas as pd

BASE = Path("data/processed")

# --- Regex patterns ---
DOLLAR_AMOUNT_RE = re.compile(
    r"\$\s?([\d,]+(?:\.\d+)?)\s*(million|thousand|billion)",
    re.IGNORECASE,
)
ROUND_RE = re.compile(
    r"Series\s+([A-F])(?:[-–]\d+)?\s+(?:convertible\s+)?preferred\s+stock",
    re.IGNORECASE,
)
PROCEEDS_RE = re.compile(
    r"(?:aggregate\s+)?(?:net|gross)\s+proceeds\s+of\s+approximately\s+"
    r"\$\s?([\d,]+(?:\.\d+)?)\s*(million|thousand)",
    re.IGNORECASE,
)

# Financing-action keywords: the sentence must contain one of these near the
# round mention for us to trust the dollar amount as a real raise.
FINANCING_ACTION_RE = re.compile(
    r"(?:proceeds|raised|financing|private\s+placement|sold\s+.*?shares|"
    r"issued\s+.*?shares|aggregate\s+.*?sold|sold\s+.*?aggregate|"
    r"purchase\s+agreement|closings?\s+.*?\$|closing\s+.*?\$|"
    r"gross\s+proceeds|net\s+proceeds|total\s+proceeds)",
    re.IGNORECASE,
)

MAX_AMOUNT_M = 5000  # $5B cap
PROXIMITY_WINDOW = 300  # chars around round mention


def parse_dollar(raw: str, unit: str) -> float:
    """Convert '$10.5 million' -> 10.5 (in millions)."""
    amount = float(raw.replace(",", ""))
    if unit.lower().startswith("billion"):
        return round(amount * 1000, 2)
    elif unit.lower().startswith("thousand"):
        return round(amount / 1000, 6)
    return round(amount, 2)


def extract_from_sentence(sentence: str) -> dict:
    """
    Returns dict with:
      proceeds_amount_m: float or None
      round_amounts: list of (round_name, amount_m)
      source: "proceeds" | "round_dollar" | "both" | None
    """
    result = {
        "proceeds_amount_m": None,
        "round_amounts": [],
        "source": None,
    }

    # 1. Proceeds phrasing (highest confidence)
    pm = PROCEEDS_RE.search(sentence)
    if pm:
        amt = parse_dollar(pm.group(1), pm.group(2))
        if amt <= MAX_AMOUNT_M:
            result["proceeds_amount_m"] = amt

    # 2. Round mentions with proximate financing-action + dollar
    for rm in ROUND_RE.finditer(sentence):
        round_name = f"Series {rm.group(1)}"
        start = max(0, rm.start() - PROXIMITY_WINDOW)
        end = min(len(sentence), rm.end() + PROXIMITY_WINDOW)
        window = sentence[start:end]

        # Must have a financing-action keyword in the window
        if not FINANCING_ACTION_RE.search(window):
            continue

        # Find dollar amounts in the window
        found_amt = None
        for dm in DOLLAR_AMOUNT_RE.finditer(window):
            amt = parse_dollar(dm.group(1), dm.group(2))
            if 0.01 <= amt <= MAX_AMOUNT_M:  # skip $0 noise
                found_amt = amt
                break

        if found_amt is not None:
            result["round_amounts"].append((round_name, found_amt))

    # 3. Determine source
    has_proceeds = result["proceeds_amount_m"] is not None
    has_rounds = len(result["round_amounts"]) > 0
    if has_proceeds and has_rounds:
        result["source"] = "both"
    elif has_proceeds:
        result["source"] = "proceeds"
    elif has_rounds:
        result["source"] = "round_dollar"
    else:
        result["source"] = None

    return result


def aggregate_company(rows: pd.DataFrame) -> dict:
    """Aggregate all candidate sentences for one company."""
    rows = rows.drop_duplicates(subset=["sentence"])

    total_proceeds = 0.0
    round_totals: dict[str, float] = {}
    all_details = []
    methods = set()

    for _, row in rows.iterrows():
        sent = row["sentence"]
        info = extract_from_sentence(sent)

        if info["source"] is None:
            continue

        if info["proceeds_amount_m"] is not None:
            total_proceeds += info["proceeds_amount_m"]
            methods.add("proceeds_phrasing")
            all_details.append({
                "type": "aggregate_proceeds",
                "amount_m": info["proceeds_amount_m"],
                "sentence": sent[:200],
            })
            continue  # don't also count round amounts from same sentence

        if info["source"] == "round_dollar":
            methods.add("round_dollar")
            for rnd, amt in info["round_amounts"]:
                round_totals[rnd] = round_totals.get(rnd, 0.0) + amt
                all_details.append({
                    "type": "round_financing",
                    "round": rnd,
                    "amount_m": amt,
                    "sentence": sent[:200],
                })

    # Deduplicate details
    seen = set()
    unique_details = []
    for d in all_details:
        key = (d.get("type"), d.get("round"), d.get("amount_m"), d.get("sentence"))
        if key not in seen:
            seen.add(key)
            unique_details.append(d)

    num_rounds = len(round_totals)
    if total_proceeds > 0 and num_rounds == 0:
        num_rounds = 1

    if not methods:
        return {
            "total_pre_ipo_capital_m": None,
            "total_pre_ipo_capital_raw": None,
            "num_rounds_detected": 0,
            "round_details": json.dumps([]),
            "extraction_method": "none",
            "confidence": "none",
        }

    if total_proceeds > 0:
        final_total = round(total_proceeds, 2)
        raw = f"${final_total:,.1f}M (from proceeds phrasing)"
    elif round_totals:
        all_amts = [d["amount_m"] for d in unique_details
                    if d.get("amount_m") and d.get("type") == "round_financing"]
        best = max(all_amts) if all_amts else max(round_totals.values())
        final_total = round(best, 2)
        raw = f"${final_total:,.1f}M (max single round, {len(round_totals)} rounds detected)"
    else:
        final_total = None
        raw = None

    method_str = "+".join(sorted(methods))
    confidence = "high" if "proceeds_phrasing" in methods else "medium"

    return {
        "total_pre_ipo_capital_m": final_total,
        "total_pre_ipo_capital_raw": raw,
        "num_rounds_detected": num_rounds,
        "round_details": json.dumps(unique_details[:10]),
        "extraction_method": method_str,
        "confidence": confidence,
    }


if __name__ == "__main__":
    high = pd.read_csv(BASE / "financing_high_confidence.csv", dtype={"cik": str})
    med = pd.read_csv(BASE / "financing_medium_confidence.csv", dtype={"cik": str})

    combined = pd.concat([high, med], ignore_index=True)
    combined = combined.drop_duplicates(subset=["cik", "sentence"])
    print(f"Combined candidates after dedup: {len(combined)} rows, {combined['cik'].nunique()} companies")

    roster = pd.read_csv(BASE / "final_roster.csv", dtype={"cik": str})
    roster["cik"] = roster["cik"].str.zfill(10)
    combined["cik"] = combined["cik"].str.zfill(10)

    results = []
    for cik, group in combined.groupby("cik"):
        agg = aggregate_company(group)
        agg["cik"] = cik
        agg["company_name"] = group["company_name"].iloc[0]
        results.append(agg)

    feat_df = pd.DataFrame(results)

    covered_ciks = set(feat_df["cik"])
    missing_rows = []
    for _, row in roster.iterrows():
        cik = row["cik"]
        if cik not in covered_ciks:
            missing_rows.append({
                "cik": cik,
                "company_name": row["company_name"],
                "total_pre_ipo_capital_m": None,
                "total_pre_ipo_capital_raw": None,
                "num_rounds_detected": 0,
                "round_details": "[]",
                "extraction_method": "none",
                "confidence": "none",
            })
    if missing_rows:
        feat_df = pd.concat(
            [feat_df, pd.DataFrame(missing_rows)], ignore_index=True
        )

    feat_df = feat_df.sort_values("company_name").reset_index(drop=True)

    out_path = BASE / "financing_features.csv"
    feat_df.to_csv(out_path, index=False)

    total = len(feat_df)
    has_data = feat_df[feat_df["extraction_method"] != "none"]
    high_conf = feat_df[feat_df["confidence"] == "high"]
    med_conf = feat_df[feat_df["confidence"] == "medium"]

    print(f"\n=== Financing Features Summary ===")
    print(f"Total companies: {total}")
    print(f"Companies with extractable data: {len(has_data)} ({len(has_data)*100//total}%)")
    print(f"  High confidence (proceeds phrasing): {len(high_conf)}")
    print(f"  Medium confidence (round+dollar): {len(med_conf)}")
    print(f"Companies with no data: {total - len(has_data)}")

    if len(has_data) > 0:
        print(f"\nCapital raised stats (companies with data):")
        print(f"  Mean: ${has_data['total_pre_ipo_capital_m'].mean():.1f}M")
        print(f"  Median: ${has_data['total_pre_ipo_capital_m'].median():.1f}M")
        print(f"  Min: ${has_data['total_pre_ipo_capital_m'].min():.1f}M")
        print(f"  Max: ${has_data['total_pre_ipo_capital_m'].max():.1f}M")
    print(f"\nRounds detected stats:")
    print(f"  Mean rounds: {has_data['num_rounds_detected'].mean():.1f}")
    print(f"  Max rounds: {has_data['num_rounds_detected'].max()}")
    print(f"\nWritten to {out_path}")
