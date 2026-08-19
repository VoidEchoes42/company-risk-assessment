"""
Deep-dive analysis of the risk model:
1. Misclassification analysis
2. Actively-filing companies flagged as high risk (early warnings)
3. Stalled companies that looked safe (missed signals)
4. Threshold calibration
"""
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

BASE = Path("data/processed")
PRED_PATH = BASE / "risk_predictions.csv"
FEATURES_PATH = BASE / "features_master.csv"
META_PATH = BASE / "model_metadata.json"

preds = pd.read_csv(PRED_PATH, dtype={"cik": str})
features = pd.read_csv(FEATURES_PATH, dtype={"cik": str})
with open(META_PATH) as f:
    meta = json.load(f)

classes = meta["classes"]

print(f"Model: {meta['best_model']}, Accuracy: {meta['accuracy']:.3f}, Macro-F1: {meta['macro_f1']:.3f}")
print(f"{'='*70}")

# ── 1. Misclassifications ───────────────────────────────────────
wrong = preds[preds["correct"] == 0]
print(f"\n{'='*70}")
print(f"MISCLASSIFICATIONS: {len(wrong)} / {len(preds)} ({len(wrong)/len(preds)*100:.1f}%)")
print(f"{'='*70}")

for _, r in wrong.iterrows():
    pred_col = f"prob_{r['predicted']}"
    true_col = f"prob_{r['bucket']}"
    pred_conf = r.get(pred_col, "?")
    true_conf = r.get(true_col, "?")
    print(f"  Predicted {r['predicted'][:22]:22s} (conf {pred_conf:.2f})"
          f"  | True {r['bucket'][:22]:22s}  {r['company_name'][:45]}")

# ── 2. Actively-filing companies flagged high-risk ─────────────
print(f"\n{'='*70}")
print("ACTIVELY-FILING COMPANIES WITH HIGH RISK SCORE (potential early warnings)")
print(f"{'='*70}")

active = preds[preds["bucket"] == "actively_filing"].copy()
active = active.sort_values("risk_score", ascending=False)
warn_threshold = 50  # risk_score > 50 is concerning
high_risk_active = active[active["risk_score"] > warn_threshold]

print(f"\nCompanies still actively filing but scored >{warn_threshold}% failure risk:")
print(f"Count: {len(high_risk_active)} / {len(active)} actively-filing companies\n")

for _, r in high_risk_active.head(20).iterrows():
    # Pull feature data
    feat_row = features[features["cik"] == r["cik"]]
    if len(feat_row) > 0:
        fr = feat_row.iloc[0]
        capital = fr.get("total_pre_ipo_capital_m", "?")
        trials = fr.get("pre_ipo_trial_count", "?")
        patents = fr.get("pre_ipo_patent_count", "?")
        pubs = fr.get("pubmed_pre_ipo_count", "?")
        years = fr.get("years_to_ipo", "?")
        detail = f"$ {capital:.1f}M | {trials} trials | {patents} patents | {pubs} pubs | {years}yr"
    else:
        detail = ""
    print(f"  Risk {r['risk_score']:5.1f}%  {r['company_name'][:45]:45s}  {detail}")

# ── 3. Stalled companies the model missed ──────────────────────
print(f"\n{'='*70}")
print("STALLED COMPANIES MODEL THOUGHT WERE SAFE (false negatives)")
print(f"{'='*70}")

stalled = preds[preds["bucket"] == "stalled_filing"].copy()
missed = stalled[stalled["risk_score"] < 30]

print(f"\nStalled companies with risk_score < 30%: {len(missed)}")
for _, r in missed.iterrows():
    print(f"  Risk {r['risk_score']:5.1f}%  {r['company_name'][:50]}")

# ── 4. Threshold analysis ──────────────────────────────────────
print(f"\n{'='*70}")
print("THRESHOLD CALIBRATION")
print(f"{'='*70}")

# Combine stalled + delisted as "failure"
preds["is_failure"] = preds["bucket"].isin(["deregistered_or_delisted", "stalled_filing"])
preds["pred_failure"] = preds["risk_score"] > 30

from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

for thresh in [20, 30, 40, 50, 60]:
    pred_fail = (preds["risk_score"] > thresh).astype(int)
    is_fail = preds["is_failure"].astype(int)
    prec = precision_score(is_fail, pred_fail, zero_division=0)
    rec = recall_score(is_fail, pred_fail, zero_division=0)
    f1 = f1_score(is_fail, pred_fail, zero_division=0)
    flagged = pred_fail.sum()
    print(f"  Threshold {thresh:2d}%: precision={prec:.3f}  recall={rec:.3f}  F1={f1:.3f}  flagged={flagged}/{len(preds)}")

# ── 5. Feature-driven insights ─────────────────────────────────
print(f"\n{'='*70}")
print("FEATURE-DRIVEN INSIGHTS")
print(f"{'='*70}")

# Merge predictions with features for analysis
merged = preds.merge(features, on="cik", how="left", suffixes=("", "_feat"))
bucket_col = "bucket_feat" if "bucket_feat" in merged.columns else "bucket"

# Capital efficiency analysis
print("\n--- Capital efficiency by outcome ---")
for bucket in meta["classes"]:
    subset = merged[merged[bucket_col] == bucket]
    eff = subset["capital_efficiency_m"].dropna()
    if len(eff) > 0:
        print(f"  {bucket:<30s}: mean ${eff.mean():.1f}M/yr (n={len(eff)})")

# Publication analysis
print("\n--- Pre-IPO publications by outcome ---")
for bucket in meta["classes"]:
    subset = merged[merged[bucket_col] == bucket]
    pubs = subset["pubmed_pre_ipo_count"].dropna()
    nonzero = pubs[pubs > 0]
    if len(pubs) > 0:
        print(f"  {bucket:<30s}: median {pubs.median():.0f} (nonzero median {nonzero.median():.0f}, n={len(pubs)})")

# Patent analysis
print("\n--- Patents by outcome ---")
for bucket in meta["classes"]:
    subset = merged[merged[bucket_col] == bucket]
    pats = subset["pre_ipo_patent_count"].dropna()
    if len(pats) > 0:
        print(f"  {bucket:<30s}: median {pats.median():.0f} (n={len(pats)})")

# Trial analysis
print("\n--- Clinical trials by outcome ---")
for bucket in meta["classes"]:
    subset = merged[merged[bucket_col] == bucket]
    trials = subset["pre_ipo_trial_count"].dropna()
    if len(trials) > 0:
        print(f"  {bucket:<30s}: median {trials.median():.0f} (n={len(trials)})")

# ── 6. Save the high-risk actively-filing watchlist ────────────
watchlist = high_risk_active[["cik", "company_name", "risk_score", "predicted",
                               "prob_actively_filing", "prob_deregistered_or_delisted",
                               "prob_stalled_filing"]].copy()
watchlist_path = BASE / "watchlist_high_risk_active.csv"
watchlist.to_csv(watchlist_path, index=False)
print(f"\nWatchlist saved to {watchlist_path} ({len(watchlist)} companies)")
