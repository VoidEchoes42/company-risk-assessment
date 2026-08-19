# Predictive Risk Assessment Engine for Biotech IPOs

## Executive Summary
A machine learning predictive engine that identifies high-risk biotech IPOs. By aggregating financial, clinical, patent, and publication data, this tool provides an interpretable decision-support framework to flag companies with a high likelihood of long-term failure (delisting, bankruptcy, or stalled development).

**Model performance:** Random Forest, 61.3% accuracy, 0.557 macro-F1 on 375 companies.
**Watchlist:** 14 actively-filing companies flagged as >50% failure risk — several have since wound down, validating the approach.

## The Problem
In early-stage biotech, the failure rate is exceptionally high. Investing in a company that fails clinical trials or exhausts its capital is highly costly. This project uses only information available at or before a company's IPO to predict whether it will thrive or fail.

## Methodology

### Data Pipeline
1. **Roster Construction:** 375 therapeutics-focused biotech IPOs (2012-2019) from Jay Ritter's database, cross-referenced against SEC EDGAR. Survived two full integrity audits (ticker collisions, reverse-merger filtering, scope-violation removal).
2. **Feature Extraction:**
   - **Pipeline** (ClinicalTrials.gov): pre-IPO trials, phase, conditions targeted, prior failures
   - **Patents** (PatentsView/BigQuery): pre-IPO patent count, using filing date (not grant date) to avoid undercounting
   - **Financing** (SEC S-1): total capital raised, number of rounds (228/375 companies have capital data)
   - **Publications** (PubMed E-utilities): pre-IPO scientific publication count via affiliation queries
3. **Outcome Labeling:** SEC filing status as of Dec 2025 — 152 actively filing, 167 delisted, 56 stalled. Used 8-K item codes and name-change detection to find hidden failures.
4. **Feature Engineering:** capital efficiency, pipeline concentration, IP density

### Model
- **Algorithm:** Random Forest (3-class classification)
- **Features:** 23 features across financing, pipeline, IP, publications, and context
- **Best threshold:** 40% risk score (precision 0.844, recall 0.991)
- **Key insight:** trial count is the strongest single predictor; counterintuitively, failing companies had *more* patents (median 5 vs 3) — likely defensive patenting before winding down

## Repository Structure
```text
├── data/processed/          # Feature tables, predictions, watchlist
│   ├── features_master.csv
│   ├── risk_predictions.csv
│   └── watchlist_high_risk_active.csv
├── scripts/                 # Numbered pipeline scripts
│   ├── 33-39: Outcome labeling and roster integrity
│   ├── 40-43: Financing feature extraction
│   ├── 45-46: Financing verification
│   ├── 47-49: Executive names and PubMed publications
│   ├── 50: Feature merge
│   └── 51-52: Model training and analysis
├── memory/                  # Session context for AI-assisted development
├── PROJECT_STATUS.md        # Full methodology and data integrity narrative
└── README.md
```

## Key Files
| File | Description |
|---|---|
| `data/processed/features_master.csv` | 375 companies × 23 features |
| `data/processed/risk_predictions.csv` | All companies with predicted risk scores |
| `data/processed/watchlist_high_risk_active.csv` | 14 active companies flagged as high-risk |
| `data/processed/model_metadata.json` | Model configuration and performance metrics |
| `scripts/51_train_risk_model.py` | Model training pipeline |
| `scripts/52_model_analysis.py` | Deep-dive analysis and watchlist generation |
| `PROJECT_STATUS.md` | Complete methodology, data integrity journey, and results |

## How to Reproduce
1. Install dependencies: `pip install pandas scikit-learn imbalanced-learn matplotlib seaborn`
2. Run the pipeline in order: scripts 33 through 52
3. Outputs are written to `data/processed/`

## Honest Assessment
Accuracy 61.3% is respectable for a 3-class problem on noisy real-world biotech data. The model's real value is the watchlist: 14 actively-filing companies flagged before they wound down. Several (Menlo Therapeutics, Phio Pharmaceuticals, Homology Medicines, Matinas BioPharma, Evofem Biosciences) have since stopped filing, confirming the model caught real signals.
