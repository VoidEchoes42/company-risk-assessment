"""
Step 5: Train risk prediction model for biotech IPO survival.

Predicts the 'bucket' outcome:
  - actively_filing (low risk)
  - stalled_filing (medium risk)
  - deregistered_or_delisted (high risk)

Uses all available features from features_master.csv with proper imputation
and model comparison (Logistic Regression, Random Forest, XGBoost).
"""
import json
import warnings
from pathlib import Path

import pandas as pd
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    make_scorer,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

BASE = Path("data/processed")
FEATURES_PATH = BASE / "features_master.csv"
OUT_DIR = BASE

# ── Load data ──────────────────────────────────────────────────────────────
df = pd.read_csv(FEATURES_PATH, dtype={"cik": str})

# ── Feature selection ────────────────────────────────────────────────────
FEATURES_NUMERIC = [
    "total_pre_ipo_capital_m",
    "num_rounds_detected",
    "years_to_ipo",
    "pre_ipo_trial_count",
    "pre_ipo_max_phase_rank",
    "pre_ipo_conditions_targeted",
    "pipeline_concentration",
    "pre_ipo_had_terminated_or_withdrawn",
    "pre_ipo_patent_count",
    "ip_density",
    "pubmed_pre_ipo_count",
    "capital_efficiency_m",
]

FEATURES_CATEGORICAL = ["sic"]

TARGET = "bucket"

# ── Prepare X, y ─────────────────────────────────────────────────
X = df[FEATURES_NUMERIC + FEATURES_CATEGORICAL].copy()
y = df[TARGET].copy()

# Replace infinities with NaN (e.g. ip_density when trial_count=0)
X = X.replace([np.inf, -np.inf], np.nan)

print(f"Dataset: {len(X)} companies")
print(f"Features: {len(FEATURES_NUMERIC)} numeric + {len(FEATURES_CATEGORICAL)} categorical")
print(f"\nClass distribution:")
print(y.value_counts().to_string())
print(f"\nMissing values per feature:")
for col in FEATURES_NUMERIC:
    nn = X[col].notna().sum()
    print(f"  {col:40s}: {nn:3d}/{len(X)} ({nn/len(X)*100:.0f}%)")

# ── Preprocessing ─────────────────────────────────────────────────
numeric_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])

categorical_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
])

preprocessor = ColumnTransformer([
    ("num", numeric_transformer, FEATURES_NUMERIC),
    ("cat", categorical_transformer, FEATURES_CATEGORICAL),
])

# ── Model comparison ─────────────────────────────────────────────
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=10, class_weight="balanced", random_state=42, n_jobs=-1),
    "Gradient Boosting": GradientBoostingClassifier(n_estimators=200, max_depth=4, random_state=42),
}

# Macro-F1 is our scoring metric (treats all classes equally)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

print(f"\n{'='*60}")
print(f"Model Comparison (5-fold CV, macro-F1)")
print(f"{'='*60}")
print(f"{'Model':<25} {'Macro F1':>10} {'Accuracy':>10}")
print(f"{'-'*50}")

results = {}
for name, model in models.items():
    pipe = Pipeline([("prep", preprocessor), ("clf", model)])
    scores_f1 = cross_val_score(pipe, X, y, cv=cv, scoring="f1_macro")
    scores_acc = cross_val_score(pipe, X, y, cv=cv, scoring="accuracy")
    f1_mean, f1_std = scores_f1.mean(), scores_f1.std()
    acc_mean = scores_acc.mean()
    print(f"{name:<25} {f1_mean:>10.3f} ±{f1_std:.3f}  {acc_mean:>10.3f}")
    results[name] = {"f1": f1_mean, "f1_std": f1_std, "acc": acc_mean, "model": pipe}

best_name = max(results, key=lambda k: results[k]["f1"])
best_pipe = results[best_name]["model"]

print(f"\nBest model: {best_name} (F1={results[best_name]['f1']:.3f})")

# ── Train final model on all data ─────────────────────────────────
best_pipe.fit(X, y)
y_pred = best_pipe.predict(X)

print(f"\n{'='*60}")
print(f"Final Model Performance (trained on all data)")
print(f"{'='*60}")
print(classification_report(y, y_pred, digits=3))

# ── Confusion matrix ─────────────────────────────────────────────
cm = confusion_matrix(y, y_pred, labels=best_pipe.classes_)
print("Confusion Matrix (rows=true, cols=pred):")
print(f"  Classes: {best_pipe.classes_}")
for i, true_cls in enumerate(best_pipe.classes_):
    print(f"  {true_cls:<30s}: {cm[i]}")

# ── Feature importance ───────────────────────────────────────────
clf = best_pipe.named_steps["clf"]
if hasattr(clf, "feature_importances_"):
    importances = clf.feature_importances_
    feat_names = FEATURES_NUMERIC + FEATURES_CATEGORICAL
    imp_df = pd.DataFrame({"feature": feat_names, "importance": importances})
    imp_df = imp_df.sort_values("importance", ascending=False)
    print(f"\n{'='*60}")
    print("Feature Importance:")
    print(f"{'='*60}")
    for _, r in imp_df.iterrows():
        print(f"  {r['feature']:40s} {r['importance']:>8.4f}")

# ── Predictions with confidence ──────────────────────────────────
proba = best_pipe.predict_proba(X)
prob_df = pd.DataFrame(proba, columns=[f"prob_{c}" for c in best_pipe.classes_])

output = df[["cik", "company_name", "bucket"]].copy().reset_index(drop=True)
for c in best_pipe.classes_:
    output[f"prob_{c}"] = prob_df[f"prob_{c}"].values
output["predicted"] = y_pred
output["confidence"] = proba.max(axis=1)
output["correct"] = (output["predicted"] == output["bucket"]).astype(int)

# Risk score: higher = more likely to fail
fail_prob = np.zeros(len(output))
for i, c in enumerate(best_pipe.classes_):
    if "delisted" in c.lower() or "deregistered" in c.lower():
        fail_prob += proba[:, i]
    if "stalled" in c.lower():
        fail_prob += proba[:, i] * 0.5
output["risk_score"] = (fail_prob * 100).round(1)
output = output.sort_values("risk_score", ascending=False).reset_index(drop=True)

print(f"\n{'='*60}")
print("Highest Risk Companies (predicted failure probability):")
print(f"{'='*60}")
for _, r in output.head(20).iterrows():
    pred_icon = "OK" if r["correct"] else "✗"
    print(f"  {r['risk_score']:5.1f}%  [{r['predicted'][:20]:20s}]  [{r['bucket'][:20]:20s}]  {pred_icon}  {r['company_name'][:40]}")

# Save predictions
out_path = OUT_DIR / "risk_predictions.csv"
output.to_csv(out_path, index=False)
print(f"\nPredictions saved to {out_path}")

# Save model metadata
meta = {
    "best_model": best_name,
    "macro_f1": round(float(results[best_name]["f1"]), 4),
    "accuracy": round(float(results[best_name]["acc"]), 4),
    "n_companies": len(df),
    "features_used": FEATURES_NUMERIC + FEATURES_CATEGORICAL,
    "classes": list(best_pipe.classes_),
}
meta_path = OUT_DIR / "model_metadata.json"
with open(meta_path, "w") as f:
    json.dump(meta, f, indent=2)
print(f"Metadata saved to {meta_path}")
