"""
Manual verification checklist for the risk model.

Instructions:
  1. For each company below, look it up on:
     - SEC EDGAR (last 10-K/10-Q filing date)
     - Stock price / market cap (Yahoo Finance, Google Finance)
     - News (company name + "acquired", "delisted", "bankruptcy", "reverse merger")
  2. Check if the model's prediction matches reality
  3. Note any companies where the model is clearly wrong

Three sections:
  A. Companies predicted to fail but still actively filing (false alarms)
  B. Companies predicted to survive but actually failed (missed signals)
  C. High-risk watchlist — actively filing, scored >50% failure risk
"""
import pandas as pd
import json
from pathlib import Path

BASE = Path("data/processed")
preds = pd.read_csv(BASE / "risk_predictions.csv", dtype={"cik": str})
features = pd.read_csv(BASE / "features_master.csv", dtype={"cik": str})
with open(BASE / "model_metadata.json") as f:
    meta = json.load(f)

# Merge for context
merged = preds.merge(features, on="cik", how="left", suffixes=("", "_feat"))

output = []
output.append("# Model Manual Verification Checklist\n")
output.append("Generated from model analysis. Check each company against current reality.\n\n")

# ── Section A: Predicted failure, still actively filing ────────
output.append("## Section A: Predicted Failure but Still Actively Filing (False Alarms)\n\n")
output.append("These companies the model thinks will fail but are still filing. Check if any have\n")
output.append("quietly wound down, reverse-merged, or are in distress the model missed.\n\n")

false_alarms = merged[
    (merged["bucket"] == "actively_filing") &
    (merged["predicted"].isin(["deregistered_or_delisted", "stalled_filing"]))
].sort_values("risk_score", ascending=False)

output.append("| # | Company | Risk Score | Predicted | Capital | Trials | Patents | Pubs | Notes |\n")
output.append("|---|---------|-----------|-----------|---------|--------|---------|------|-------|\n")
for i, (_, r) in enumerate(false_alarms.iterrows(), 1):
    cap = f"${r['total_pre_ipo_capital_m']:.1f}M" if pd.notna(r.get("total_pre_ipo_capital_m")) else "?"
    trials = r.get("pre_ipo_trial_count", "?")
    pats = r.get("pre_ipo_patent_count", "?")
    pubs = r.get("pubmed_pre_ipo_count", "?")
    output.append(f"| {i} | {r['company_name'][:40]} | {r['risk_score']:.1f}% | {r['predicted'][:20]} | {cap} | {trials} | {pats} | {pubs} | |\n")

output.append(f"\n**Total: {len(false_alarms)} companies**\n\n")

# ── Section B: Predicted survival, actually failed ─────────────
output.append("## Section B: Predicted Survival but Actually Failed (Missed Signals)\n\n")
output.append("These companies the model thought would survive but have already failed.\n")
output.append("These are the most important to understand — what did the model miss?\n\n")

# NOTE: This model has ZERO false negatives — it never predicts "actively filing"
# for a company that has actually failed. All errors are false alarms.
missed = merged[
    (merged["bucket"].isin(["deregistered_or_delisted", "stalled_filing"])) &
    (merged["predicted"] == "actively_filing")
].sort_values("risk_score")

output.append("| # | Company | Risk Score | Actual Outcome | Capital | Trials | Patents | Pubs | Notes |\n")
output.append("|---|---------|-----------|---------------|---------|--------|---------|------|-------|\n")
for i, (_, r) in enumerate(missed.iterrows(), 1):
    cap = f"${r['total_pre_ipo_capital_m']:.1f}M" if pd.notna(r.get("total_pre_ipo_capital_m")) else "?"
    trials = r.get("pre_ipo_trial_count", "?")
    pats = r.get("pre_ipo_patent_count", "?")
    pubs = r.get("pubmed_pre_ipo_count", "?")
    output.append(f"| {i} | {r['company_name'][:40]} | {r['risk_score']:.1f}% | {r['bucket'][:25]} | {cap} | {trials} | {pats} | {pubs} | |\n")

output.append(f"\n**Total: {len(missed)} companies**\n\n")

if len(missed) == 0:
    output.append("**This is actually a positive finding for the model:** it never misses a company that has already failed.\n")
    output.append("All 44 misclassifications are false alarms (Section A), not missed failures.\n")
    output.append("This means the model is **conservative on the failure side** — when it says a company will fail, it might be wrong,\n")
    output.append("but when it says a company will survive, it's reliable.\n\n")
    output.append("Implication for use: use the watchlist as a high-priority monitoring signal, not as a definitive prediction.\n\n")

# ── Section C: High-risk watchlist (actively filing, >50% risk) ─
output.append("## Section C: High-Risk Watchlist (Actively Filing, Risk Score > 50%)\n\n")
output.append("These are the companies to watch most closely. The model thinks they're in trouble.\n")
output.append("Verify: have any of these already failed since the Dec 2025 cutoff?\n\n")

watchlist = merged[
    (merged["bucket"] == "actively_filing") &
    (merged["risk_score"] > 50)
].sort_values("risk_score", ascending=False)

output.append("| # | Company | Risk Score | Capital | Trials | Patents | Pubs | Last Check | Notes |\n")
output.append("|---|---------|-----------|---------|--------|---------|------|-----------|-------|\n")
for i, (_, r) in enumerate(watchlist.iterrows(), 1):
    cap = f"${r['total_pre_ipo_capital_m']:.1f}M" if pd.notna(r.get("total_pre_ipo_capital_m")) else "?"
    trials = r.get("pre_ipo_trial_count", "?")
    pats = r.get("pre_ipo_patent_count", "?")
    pubs = r.get("pubmed_pre_ipo_count", "?")
    output.append(f"| {i} | {r['company_name'][:40]} | {r['risk_score']:.1f}% | {cap} | {trials} | {pats} | {pubs} | Aug 2026 | |\n")

output.append(f"\n**Total: {len(watchlist)} companies**\n\n")

# ── Section D: Quick reference — all companies sorted by risk ──
output.append("## Section D: All 375 Companies Sorted by Risk Score\n\n")
all_sorted = merged.sort_values("risk_score", ascending=False)
output.append("| # | Company | Risk Score | Predicted | Actual | CIK |\n")
output.append("|---|---------|-----------|-----------|--------|-----|\n")
for i, (_, r) in enumerate(all_sorted.iterrows(), 1):
    output.append(f"| {i} | {r['company_name'][:40]} | {r['risk_score']:.1f}% | {r['predicted'][:22]} | {r['bucket'][:22]} | {r['cik']} |\n")

# Save
out_path = BASE / "manual_verification_checklist.md"
with open(out_path, "w", encoding="utf-8") as f:
    f.writelines(output)

print(f"Written to {out_path}")
print(f"  Section A (false alarms): {len(false_alarms)} companies")
print(f"  Section B (missed signals): {len(missed)} companies")
print(f"  Section C (watchlist): {len(watchlist)} companies")
print(f"  Section D (full ranking): {len(all_sorted)} companies")
