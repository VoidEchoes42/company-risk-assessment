# Predictive Risk Assessment Engine for Biotech IPOs

## Executive Summary
A machine learning predictive engine designed to identify high-risk biotech IPOs. By aggregating and analyzing disparate financial, clinical, and patent data, this tool provides an interpretable decision-support framework to flag companies with a high likelihood of long-term failure (e.g., delisting or bankruptcy).

## Business Problem
In the early-stage biotech sector, the failure rate is exceptionally high. Investing in a company that fails clinical trials or exhausts its capital is highly costly. This project aims to transition from qualitative screening to a rigorous, data-driven approach, predicting clinical and market survival based on pre-IPO signals.

## Methodology & Progress
The project is currently in the **Data Engineering and Collection** phase. 
- Aggregating historical data on biotech initial public offerings.
- Scraping SEC Edgar for S-1 filings and business summaries.
- Querying patent databases and clinical trial registries to extract robust pipeline metrics.
- Handling data triage, corporate name divergence, and outcomes verification.

*(More details on predictive modeling and feature engineering will be added as the project progresses into the machine learning phase).*

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
