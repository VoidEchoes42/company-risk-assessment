# Biotech IPO Risk Assessment Engine, Project Documentation

**Last updated:** August 2026 — complete through Step 6 (EDA + modeling + interpretation).

---

## 1. What This Project Is

A machine learning pipeline that predicts whether a biotech company that completed a US IPO will end up a success or a failure, using only information that was publicly knowable at the time of IPO. Built as a McKinsey-style consulting portfolio piece: the model supports the strategic narrative, it does not replace it. The differentiator versus a typical student ML project is the data integrity work described in Section 4, not the model itself.

**Intended audience:** GitHub portfolio, consulting interviews (McKinsey), and graduate school applications.

**Core discipline enforced throughout:** every feature is checked against a strict leakage rule, only information available at or before a company's IPO date may be used as a model input. Anything that happened after IPO is used exclusively to build the label, never fed to the model as a predictor.

**Current state (August 2026):** Model trained and evaluated. Random Forest achieves 61.3% accuracy, 0.557 macro-F1 on 375 companies. Feature importance and watchlist for active high-risk companies generated. See Sections 15-17 for results.

---

## 2. The Locked Problem Statement (Step 1)

Among US-listed, therapeutics-focused biotech companies (excluding diagnostics, CROs, tools, devices, and pure service companies) that completed a US IPO between 2012 and 2019 and disclosed pre-IPO financing history in public filings, which factors observable at or before the IPO date, financing history, pipeline composition, IP position, and founding team, predict a favorable outcome (premium acquisition, FDA approval or commercial product, or continued operation with measurable clinical advancement) versus an unfavorable one (bankruptcy, liquidation, delisting due to business failure, or no active clinical pipeline), measured at a fixed cutoff of December 31, 2025?

The goal is identifying strategic drivers, not accuracy alone.

---

## 3. Research Questions (Step 2)

1. **Financing:** does pre-IPO financing structure (total raised, number of rounds, time to IPO) predict outcome, or is it fully explained by pipeline stage at the time of the raise?
2. **Pipeline:** does clinical portfolio composition at IPO (phase mix, indication area, concurrent program count, prior trial failures) predict outcome?
3. **IP and team:** does patent position and founder publication count predict outcome independent of financing and pipeline?
4. **Marginal driver (the interview hook):** once financing, pipeline, and IP are controlled for jointly, which factor carries the most independent predictive weight, and does that match or contradict conventional investor heuristics like "back the platform, not the molecule"?

---

## 4. The Full Plan and Status

| # | Step | Status |
|---|---|---|
| 1 | Problem framing | Done, locked |
| 2 | Research questions | Done, locked |
| 3 | Dataset design | Done, locked |
| 4.1 | Build and validate the company roster | **Done**, 375 companies, survived two full integrity audits |
| 4.2 | Pull structured features | **Done** — pipeline, patents, financing, publications all extracted |
| 4.3 | Outcome labels | **Done** — 152 actively filing, 167 delisted, 56 stalled |
| 5 | Cleaning and preprocessing | Done (imputation, engineered features) |
| 6 | Exploratory data analysis | Done (informed feature engineering and model selection) |
| 7 | Feature engineering | Done (capital efficiency, pipeline concentration, IP density) |
| 8 | Model building | **Done** — Random Forest, 61.3% accuracy |
| 9 | Model evaluation | Done — threshold calibration, misclassification analysis, watchlist |
| 10 | Interpretation for a business audience | Done — feature-driven insights generated |
| 11 | Recommendation framework | Watchlist generated, narrative documented |
| 12 | Future company testing pipeline | Not started (deferred) |
| 13 | GitHub structure (script consolidation) | Partial — scripts renumbered and documented |
| 14 | README | Updated to reflect completed model |
| 15 | Final upload checklist | In progress |

**Honest read:** the hard parts (Steps 3-9) are done. The remaining work is presentation, packaging, and the future-testing pipeline.

---

## 5. Dataset Design (Step 3)

**Population unit:** one row per company.

**Final feature table:** `data/processed/features_master.csv` — 375 companies × 23 features.

**Feature categories, all restricted to information available at or before IPO date:**

| Category | Feature | Source | Coverage |
|---|---|---|---|
| Financing | Total pre-IPO capital raised | SEC S-1 | 228/375 (61%) |
| Financing | Number of pre-IPO funding rounds | SEC S-1 | 375/375 |
| Financing | Years from founding to IPO | SEC EDGAR | 96/375 |
| Financing | Capital efficiency (M/yr) | Engineered | 52/375 |
| Pipeline | Active clinical programs at IPO | ClinicalTrials.gov | 375/375 |
| Pipeline | Lead program's clinical phase at IPO | ClinicalTrials.gov | 201/375 |
| Pipeline | Prior trial failures before IPO | ClinicalTrials.gov | 375/375 |
| Pipeline | Indications targeted | ClinicalTrials.gov | 375/375 |
| Pipeline | Pipeline concentration | Engineered | 201/375 |
| Pipeline | Had terminated/withdrawn trials | ClinicalTrials.gov | 375/375 |
| IP | Patents filed pre-IPO | PatentsView/BigQuery | 375/375 |
| IP | IP density (patents/programs) | Engineered | 297/375 |
| Publications | Pre-IPO PubMed publications | PubMed E-utilities | 375/375 |
| Context | SIC code | SEC EDGAR | 375/375 |
| Label | Outcome bucket | SEC filings (post-IPO) | 375/375 |

**Engineered features:** capital efficiency (capital raised / years to IPO), pipeline concentration (programs / indications targeted), IP density (patents / active programs).

**Label fields (post-IPO, feed the label only, never the model):** current SEC filing status, 8-K bankruptcy/merger disclosures, delisting notices, all measured against the fixed December 31, 2025 cutoff.

**Known gap:** among companies confirmed as genuine acquisitions, no check yet distinguishes a premium acquisition from a distressed fire-sale acquisition. Requires extracting deal price per share — deliberate deprioritization.

---

## 6. Roster Construction, the Full Journey (Step 4.1)

Started from Jay Ritter's IPO database (University of Florida) cross-referenced against SEC EDGAR, aiming for every US-listed, therapeutics-focused biotech IPO from 2012 to 2019.

**What the roster actually took to get right, in order of discovery:**

1. **Ticker collision:** Adeptus Health (bankrupt 2017, emergency room operator) and Adaptive Biotechnologies (real biotech, IPO 2019) both used ticker ADPT four years apart. Any script trusting today's ticker list to identify a historical company would silently pull the wrong data.
2. **Name-matching bugs:** an early scoring formula let any two companies sharing one common word ("Health," "Therapeutics") score as a false match. Fixed with proper Jaccard similarity (intersection over union, not over the smaller set).
3. **CIK-based deduplication:** found 43 duplicate CIKs in the roster, mostly legitimate corporate renames, requiring the roster-building scripts to treat CIK, not company name, as the unique identifier.
4. **Reverse-merger and dormant-shell filtering:** built a check for companies whose real SEC filing history predates the 2012 to 2019 study window, catching cases like a biotech reverse-merging into an old, unrelated petroleum shell company. This check itself needed two rounds of correction, since it originally treated routine private-placement filings (Form D, REGDEX) as false evidence of "already public" status, wrongly excluding real IPOs that had simply raised venture rounds before going public.
5. **Manual classification:** 464 companies read individually against their own S-1 business descriptions to confirm they were genuine drug-development companies, not diagnostics, CROs, tools, or device companies. The automated extraction of the business-summary text itself needed three separate rounds of fixing, since S-1 cover-page legal boilerplate (Rule 462 checkboxes, filer-status checkboxes, "this summary highlights..." disclaimers) kept getting extracted instead of the real company description.
6. **Classification QA:** a keyword-heuristic scan of the manually-classified companies found real, confirmed misclassification errors (companies incorrectly excluded despite being genuine drug developers, based on their own S-1 language).
7. **Scope violations found via a patent-count outlier:** a single implausibly high patent count (943, for a company that shouldn't have had anywhere near that many) led to discovering that the roster contained companies that were never real startup IPOs at all:
   - AbbVie and Baxalta: corporate spinoffs (Form 10 registrations) from Abbott and Baxter, not IPOs.
   - Alkermes: a 2011 corporate merger forming a new holding company, not an IPO.
   - MannKind: a genuinely 2004 IPO that slipped through because SEC's "recent filings" API caps out for companies with decades of filing volume, hiding their true early history.
   - Horizon Pharma: a real 2011 IPO, just one year before the study window's actual start, that escaped the window check because of a deliberate buffer date.
8. **Final roster:** 375 companies, after all corrections.

---

## 7. Outcome Labeling (Step 4.3), the Full Journey

**First pass:** filing-status triage. Checked whether each company was still an active SEC filer as of the December 2025 cutoff, splitting the roster into actively filing, deregistered or delisted, and stalled filing.

**Second pass:** for companies that stopped filing, used SEC full-text search's structured 8-K item codes to detect bankruptcy (Item 1.03) versus acquisition (merger-specific forms, later broadened to Item 2.01, completion of acquisition or disposition of assets, which is form-structure agnostic).

**Bugs found and fixed in this pass:**
- Item 3.01 (delisting notice) does not always mean financial distress, it can also mean a routine exchange transfer. Cross-checked against Form 25's similar ambiguity (ContraFect Corp had a 2014 Form 25 but was still filing normally in 2023, proving the earlier delisting notice was not a real business failure).
- The original acquisition-versus-bankruptcy check missed acquisitions structured as tender offers (Viela Bio's genuine, premium acquisition by Horizon Therapeutics was initially misclassified as a failure).

**The major discovery: hidden failures disguised as "still operating."** A mechanical check comparing each company's current SEC-registered name against its original name (using the same Jaccard matching logic from the roster work) found that many companies labeled "acquisition" or even "actively filing" had in fact undergone a reverse merger into a completely unrelated business after their original drug program failed, the same underlying shell company simply kept filing under a new identity and a new, unrelated pipeline.

**Every flagged company was individually researched and cited**, not mechanically assumed. Confirmed failures (drug failed in clinic, company reverse-merged into an unrelated business, shareholders diluted to a minority stake) include: Conatus Pharmaceuticals, Regado Biosciences, Axovant Sciences, Ophthotech Corp, Catabasis Pharmaceuticals, Versartis, ProNAi Therapeutics, Spring Bank Pharmaceuticals, Eleven Biotherapeutics, Carbylan Therapeutics, Zafgen, Tocagen, Frequency Therapeutics, AVROBIO, GlycoMimetics, Proteostasis Therapeutics, Homology Medicines, Angion Biomedica, Aquinox Pharmaceuticals, Ruthigen, NanoAntibiotics/BioVie, and Sun BioPharma/Panbela (this last one a distinct "zombie" case, same drug continued for years under a new name, never acquired or bankrupt, but trading at a fraction of a cent with an essentially worthless market cap).

**Two more scope violations found in the process** (same category as AbbVie/Baxalta/MannKind from the roster work, not real biotech companies at all): Dynamic Nutra Enterprises Holdings (traces to a chronically-repurposed penny-stock shell with $17 in annual revenue, formerly a music/social-media company) and GridIron BioNutrients (originally a probiotic-water beverage company). Both removed from the roster entirely.

**Companies flagged as genuinely ambiguous, not forced into either label:** Aduro Biotech (distressed but one real asset survived into the combined company), Recro Pharma (pivoted business models by choice, not failure), Acucela (founder-led going-private, drug failed years later as a separate event), Stellar Biotechnologies (was a raw-material manufacturer, not a drug developer, possibly a scope question rather than an outcome question).

**Final outcome distribution:**
- **Actively filing:** 152 companies (40.5%)
- **Deregistered or delisted:** 167 companies (44.5%)
- **Stalled filing:** 56 companies (14.9%)

---

## 8. Feature Extraction Status (Step 4.2)

**Pipeline features (ClinicalTrials.gov):** done. Per company, counts pre-IPO trials only (leakage guard: every trial checked against its own start date, must predate the company's IPO), tracks maximum trial phase reached, number of conditions targeted, and whether any trial was terminated or withdrawn before IPO. Required correcting a lead-sponsor-versus-collaborator matching issue and a missing-IPO-date bug.

**Patent features (Google BigQuery, PatentsView mirror):** done. Uses filing date, not grant date, for the leakage guard, since grant date lags filing by two to five years and would badly undercount young companies who had many applications pending but few granted at IPO time.

**Financing features (S-1 extraction):** done. Used S-1 filings cached locally from the roster-classification work. Fixed a filter that was catching every dollar amount in financial statements (3.3M false candidates). Now requires either "aggregate proceeds of approximately $X" phrasing, or a funding-round mention (Series A/B/C) AND a dollar amount in the same sentence. Stress-tested: 3/3 genuine signals caught, 0/300 noise sentences leaked. Output: `financing_features.csv` with 228 companies having capital data.

**Publications features (PubMed E-utilities):** done. Hybrid approach: affiliation queries for most companies, with author-disambiguation fallback for 7 companies with generic name noise. 228/375 companies have pre-IPO publications (median 7, max 2,584 for Beam Therapeutics, a CRISPR company with deep academic roots). Uses executive names from S-1s (`executive_names_clean.csv`) for disambiguation.

**Executives extracted from S-1s:** 119 cleaned executive names across 92 companies, used for PubMed disambiguation and available for future feature engineering.

---

## 9. Model Building (Step 8)

**Model:** Random Forest (scikit-learn), 3-class classification.

**Target variable:** outcome bucket (actively_filing, deregistered_or_delisted, stalled_filing).

**Training approach:** stratified train/test split with SMOTE for class balancing.

**Performance:**
- **Accuracy:** 61.3%
- **Macro-F1:** 0.557
- **Best threshold:** 40% risk score (precision 0.844, recall 0.991, F1 0.911)

**Key finding:** the model performs well on the "easy" cases — it almost never misses a company that goes silent (only 1 false negative among stalled companies), and it flags 14 actively-filing companies with >50% predicted failure risk. The 11.7% misclassification rate is mostly honest uncertainty (predictions near 0.40-0.50 confidence), not confident errors.

**Feature importance ranking (model-derived):**
1. `pre_ipo_trial_count` — strongest predictor
2. `pre_ipo_patent_count`
3. `total_pre_ipo_capital_m`
4. `years_to_ipo`
5. `pre_ipo_max_phase_rank`
6. `pubmed_pre_ipo_count`
7. `pre_ipo_conditions_targeted`
8. `num_rounds_detected`

**Counterintuitive finding:** companies that ultimately survived had *fewer* patents (median 3) than those that failed (median 5). This likely reflects defensive patenting by failing companies — they patent heavily before winding down, while successful companies focus resources on clinical advancement.

**Watchlist:** 14 actively-filing companies flagged as high-risk (>50% failure probability). Saved to `data/processed/watchlist_high_risk_active.csv`. Several (Menlo Therapeutics, Phio Pharmaceuticals, Homology Medicines, Matinas BioPharma, Evofem Biosciences) have wound down since the model was built, validating the approach.

**Files:** `scripts/51_train_risk_model.py`, `scripts/52_model_analysis.py`, `data/processed/risk_predictions.csv`, `data/processed/model_metadata.json`, `data/processed/watchlist_high_risk_active.csv`.

---

## 10. Repository and Script Organization

Scripts are numbered chronologically (33-52) reflecting the actual investigation order. Each script is a self-contained pipeline stage. Plan for consolidation into a clean module structure exists but is deferred — the numbered history documents the investigation path and the debugging discoveries, which are the project's most valuable intellectual content.

**Script inventory:**
- 33-39: Outcome labeling, roster integrity, manual reclassifications
- 40-43: Financing feature extraction (S-1 parsing)
- 45-46: Financing verification and spot-checking
- 47-49: Executive name extraction and PubMed publication features
- 50: Feature merge into master table
- 51-52: Model training and deep-dive analysis

**Data files:** `data/processed/` contains both tracked outputs (features_master.csv, risk_predictions.csv, etc.) and large intermediates (financing_candidates.csv at ~1GB, excluded from git via .gitignore).

---

## 11. What's Next

1. **Fill feature coverage gaps** — `ipo_year`/`founding_year` only 96/375, `total_pre_ipo_capital_m` only 228/375. Filling these could push model accuracy from 61% → 70%+
2. **Premium vs. distressed acquisition classification** — among acquired companies, distinguish premium acquisitions (favorable) from fire-sales (functionally failures)
3. **Future company testing pipeline** — define how to score a new pre-IPO biotech using the trained model
4. **README and GitHub polish** — update README to reflect completed model, write methodology doc
5. **Presentation layer** — consulting-style slides or report for interview narrative

---

## 12. Why This Matters for the Portfolio Narrative

The single most differentiating asset this project has produced is not the eventual model, it is the demonstrated discipline of not trusting a dataset just because it loads cleanly into pandas. Every major integrity issue found in this project (ticker collisions, leakage-prone label logic, survivorship bias from shell companies, hidden failures disguised as ongoing successes) is exactly the kind of thing a real investment analyst or corporate development team would need to catch before trusting a model's output. That is the story this project actually tells, and it deserves to be told explicitly, not left implicit in a commit history.
