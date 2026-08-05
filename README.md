# Predictive Risk Assessment Engine for Biotech IPOs

## Executive Summary
A machine learning predictive engine designed to identify high-risk biotech IPOs. By aggregating and analyzing disparate financial, clinical, and patent data, this tool provides an interpretable decision-support framework to flag companies with a high likelihood of long-term failure (e.g., delisting or bankruptcy).

## Business Problem
In the early-stage biotech sector, the failure rate is exceptionally high. Investing in a company that fails clinical trials or exhausts its capital is highly costly. This project aims to transition from qualitative screening to a rigorous, data-driven approach, predicting clinical and market survival based on pre-IPO signals.

## Methodology & Progress
The project is currently finalizing the **Data Engineering and Collection** phase. The pipeline has been fully executed through the following stages:

1. **Roster Construction & Validation:** Aggregating historical Ritter IPO data, matching with SEC EDGAR SIC codes, resolving ticker collisions, and filtering out reverse-mergers and dormant shells.
2. **Manual Classification Pipeline:** Scraping SEC Edgar for S-1 filings to extract business summaries and manually validating biotech classifications.
3. **Clinical Pipeline Features:** Integrating with ClinicalTrials.gov to extract robust trial metrics and pipeline stage data.
4. **Patent & IP Features:** Querying the PatentsView API / BigQuery to quantify intellectual property strength and patent family sizes.
5. **Roster Integrity Audit:** Handling edge cases such as corporate spinoffs, mergers, and API blind spots to ensure a clean universe of companies.
6. **Outcome Labeling:** Triaging filing statuses and classifying exit reasons (e.g., delisting, bankruptcy, successful acquisition) as the target variable for predictive modeling.

*(The project is now prepared to transition into the feature engineering and predictive machine learning phase).*

## Repository Structure (Current)
```text
├── data/                    # Excluded from version control
│   ├── raw/                 # Raw datasets (Ritter IPO, etc.)
│   └── processed/           # Cleaned and engineered features
├── scripts/                 # Core data pipeline
│   ├── 01_load_ritter_ipos.py
│   ├── 02_lookup_sic_edgar.py
│   └── ...                  # (Additional processing scripts)
└── README.md                # Project documentation
```

## How to Run
*(Instructions for running the end-to-end inference pipeline will be provided upon the completion of the modeling phase).*
