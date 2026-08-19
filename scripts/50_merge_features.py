"""
Step 4.2f: Merge all features into a single master feature table.

Combines:
  - Pipeline features (ClinicalTrials.gov)
  - Patent features (BigQuery/PatentsView)
  - Financing features (S-1 extraction)
  - Publication features (PubMed)
  - Roster metadata (IPO date, year, founding year, etc.)
  - Outcome labels (exit_reasons + outcome_triage)

Output: data/processed/features_master.csv
"""
import pandas as pd
from pathlib import Path

BASE = Path("data/processed")

# Load all feature sources
roster = pd.read_csv(BASE / "final_roster.csv", dtype={"cik": str})
roster["cik"] = roster["cik"].str.zfill(10)

pipeline = pd.read_csv(BASE / "pipeline_features.csv", dtype={"cik": str})
pipeline["cik"] = pipeline["cik"].str.zfill(10)

patents = pd.read_csv(BASE / "patent_features.csv", dtype={"cik": str})
patents["cik"] = patents["cik"].str.zfill(10)

financing = pd.read_csv(BASE / "financing_features.csv", dtype={"cik": str})
financing["cik"] = financing["cik"].str.zfill(10)

publications = pd.read_csv(BASE / "publication_features.csv", dtype={"cik": str})
publications["cik"] = publications["cik"].str.zfill(10)

outcomes_triage = pd.read_csv(BASE / "outcome_triage.csv", dtype={"cik": str})
outcomes_triage["cik"] = outcomes_triage["cik"].str.zfill(10)

outcomes_exit = pd.read_csv(BASE / "exit_reasons.csv", dtype={"cik": str})
outcomes_exit["cik"] = outcomes_exit["cik"].str.zfill(10)

# Merge outcome tables
outcomes = outcomes_triage.merge(outcomes_exit, on="cik", how="outer", suffixes=("", "_exit"))

# Merge sequentially
features = roster[["cik", "company_name", "ticker", "ipo_date", "ipo_year",
                    "founding_year", "sic", "sic_description"]].copy()

features = features.merge(pipeline, on="cik", how="left", suffixes=("", "_pipe"))
features = features.merge(patents, on="cik", how="left", suffixes=("", "_pat"))
features = features.merge(
    financing[["cik", "total_pre_ipo_capital_m", "num_rounds_detected",
               "extraction_method", "confidence"]],
    on="cik", how="left", suffixes=("", "_fin")
)
features = features.merge(
    publications[["cik", "pubmed_pre_ipo_count"]],
    on="cik", how="left", suffixes=("", "_pub")
)
features = features.merge(
    outcomes[["cik", "bucket", "exit_reason", "exit_subtype"]],
    on="cik", how="left", suffixes=("", "_out")
)

# Engineer derived features
# Capital efficiency: capital / years from founding to IPO
features["founding_year"] = pd.to_numeric(features["founding_year"], errors="coerce")
features["ipo_year"] = pd.to_numeric(features["ipo_year"], errors="coerce")
features["years_to_ipo"] = features["ipo_year"] - features["founding_year"]
features.loc[features["years_to_ipo"] <= 0, "years_to_ipo"] = None

features["capital_efficiency_m"] = features["total_pre_ipo_capital_m"] / features["years_to_ipo"]
features["capital_efficiency_m"] = features["capital_efficiency_m"].round(2)

# Pipeline concentration: programs / indications targeted
features["pipeline_concentration"] = (
    features["pre_ipo_trial_count"] / features["pre_ipo_conditions_targeted"]
)
features["pipeline_concentration"] = features["pipeline_concentration"].round(2)

# IP density: patents / active programs
features["ip_density"] = (
    features["pre_ipo_patent_count"] / features["pre_ipo_trial_count"]
)
features["ip_density"] = features["ip_density"].round(3)

# Reorder columns for readability
col_order = [
    "cik", "company_name", "ticker", "ipo_date", "ipo_year", "founding_year",
    "years_to_ipo",
    # Financing
    "total_pre_ipo_capital_m", "num_rounds_detected", "capital_efficiency_m",
    # Pipeline
    "pre_ipo_trial_count", "pre_ipo_max_phase_rank", "pre_ipo_conditions_targeted",
    "pipeline_concentration", "pre_ipo_had_terminated_or_withdrawn",
    # IP
    "pre_ipo_patent_count", "ip_density",
    # Publications
    "pubmed_pre_ipo_count",
    # Outcomes
    "bucket", "exit_reason", "exit_subtype",
    # Metadata
    "sic", "sic_description",
]
# Only include columns that exist
col_order = [c for c in col_order if c in features.columns]
features = features[col_order]

# Save
out_path = BASE / "features_master.csv"
features.to_csv(out_path, index=False)

# Summary
print(f"=== Feature Merge Summary ===")
print(f"Total companies: {len(features)}")
print(f"\nFeature coverage:")
for col in ["total_pre_ipo_capital_m", "pre_ipo_trial_count", "pre_ipo_patent_count",
             "pubmed_pre_ipo_count", "bucket"]:
    if col in features.columns:
        non_null = features[col].notna().sum()
        nonzero = (features[col] > 0).sum() if features[col].dtype in ["float64", "int64"] else "N/A"
        print(f"  {col:35s}: {non_null:3d} non-null  ({nonzero} nonzero)")

print(f"\nOutcome label distribution:")
if "bucket" in features.columns:
    print(features["bucket"].value_counts().to_string())

print(f"\nWritten to {out_path}")
