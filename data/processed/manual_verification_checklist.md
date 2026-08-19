# Model Manual Verification Checklist
Generated from model analysis. Check each company against current reality.

## Section A: Predicted Failure but Still Actively Filing (False Alarms)

These companies the model thinks will fail but are still filing. Check if any have
quietly wound down, reverse-merged, or are in distress the model missed.

| # | Company | Risk Score | Predicted | Capital | Trials | Patents | Pubs | Notes |
|---|---------|-----------|-----------|---------|--------|---------|------|-------|
| 1 | BiomX Inc. | 64.4% | deregistered_or_deli | ? | 0 | 0 | 0 | |
| 2 | Menlo Therapeutics, Inc. | 62.6% | deregistered_or_deli | $109.3M | 0 | 8 | 0 | |
| 3 | Phio Pharmaceuticals Corp. | 62.4% | deregistered_or_deli | $28.2M | 0 | 0 | 1 | |
| 4 | Matinas BioPharma Holdings, Inc. | 59.2% | deregistered_or_deli | $13.6M | 0 | 2 | 0 | |
| 5 | PROTEOSTASIS THERAPEUTICS, INC. | 57.2% | deregistered_or_deli | $25.2M | 0 | 9 | 16 | |
| 6 | Homology Medicines, Inc. | 56.9% | deregistered_or_deli | $20.5M | 0 | 0 | 0 | |
| 7 | AQUINOX PHARMACEUTICALS, INC | 54.5% | deregistered_or_deli | $19.6M | 2 | 8 | 2 | |
| 8 | Evofem Biosciences, Inc. | 53.2% | deregistered_or_deli | $13.6M | 0 | 0 | 0 | |
| 9 | Gemphire Therapeutics Inc. | 52.3% | deregistered_or_deli | $1.5M | 0 | 2 | 2 | |
| 10 | EYENOVIA, INC. | 51.0% | deregistered_or_deli | $6.8M | 1 | 8 | 1 | |
| 11 | Unum Therapeutics, Inc. | 50.8% | deregistered_or_deli | $64.8M | 0 | 1 | 33 | |
| 12 | resTORbio, Inc. | 50.6% | deregistered_or_deli | $40.0M | 1 | 0 | 1 | |
| 13 | RELMADA THERAPEUTICS, INC. | 50.4% | stalled_filing | ? | 0 | 4 | 0 | |
| 14 | Atossa Genetics Inc | 50.3% | stalled_filing | ? | 0 | 2 | 0 | |
| 15 | Celsus Therapeutics Plc. | 49.7% | stalled_filing | ? | 0 | 0 | 2 | |
| 16 | Regen BioPharma Inc | 49.3% | stalled_filing | ? | 0 | 1 | 0 | |
| 17 | AntriaBio, Inc. | 49.3% | stalled_filing | ? | 0 | 1 | 0 | |
| 18 | Nemus Bioscience, Inc. | 49.1% | stalled_filing | ? | 0 | 0 | 0 | |
| 19 | Stellar Biotechnologies, Inc. | 49.1% | stalled_filing | ? | 0 | 0 | 0 | |
| 20 | Zomedica Pharmaceuticals Corp. | 49.1% | stalled_filing | ? | 0 | 0 | 0 | |
| 21 | Cell Source, Inc. | 49.1% | stalled_filing | ? | 0 | 0 | 0 | |
| 22 | Ruthigen, Inc. | 49.1% | stalled_filing | ? | 0 | 0 | 0 | |
| 23 | Sun BioPharma, Inc. | 49.1% | stalled_filing | ? | 0 | 0 | 0 | |
| 24 | NANOANTIBIOTICS, INC. | 49.1% | stalled_filing | ? | 0 | 0 | 0 | |
| 25 | Propanc Biopharma, Inc. | 49.1% | stalled_filing | ? | 0 | 0 | 0 | |
| 26 | KEMPHARM, INC | 42.6% | stalled_filing | ? | 0 | 17 | 0 | |
| 27 | FIBROGEN INC | 37.4% | stalled_filing | ? | 0 | 0 | 41 | |
| 28 | Novus Therapeutics, Inc. | 37.4% | stalled_filing | ? | 0 | 0 | 38 | |

**Total: 28 companies**

## Section B: Predicted Survival but Actually Failed (Missed Signals)

These companies the model thought would survive but have already failed.
These are the most important to understand — what did the model miss?

| # | Company | Risk Score | Actual Outcome | Capital | Trials | Patents | Pubs | Notes |
|---|---------|-----------|---------------|---------|--------|---------|------|-------|

**Total: 0 companies**

**This is actually a positive finding for the model:** it never misses a company that has already failed.
All 44 misclassifications are false alarms (Section A), not missed failures.
This means the model is **conservative on the failure side** — when it says a company will fail, it might be wrong,
but when it says a company will survive, it's reliable.

Implication for use: use the watchlist as a high-priority monitoring signal, not as a definitive prediction.

## Section C: High-Risk Watchlist (Actively Filing, Risk Score > 50%)

These are the companies to watch most closely. The model thinks they're in trouble.
Verify: have any of these already failed since the Dec 2025 cutoff?

| # | Company | Risk Score | Capital | Trials | Patents | Pubs | Last Check | Notes |
|---|---------|-----------|---------|--------|---------|------|-----------|-------|
| 1 | BiomX Inc. | 64.4% | ? | 0 | 0 | 0 | Aug 2026 | |
| 2 | Menlo Therapeutics, Inc. | 62.6% | $109.3M | 0 | 8 | 0 | Aug 2026 | |
| 3 | Phio Pharmaceuticals Corp. | 62.4% | $28.2M | 0 | 0 | 1 | Aug 2026 | |
| 4 | Matinas BioPharma Holdings, Inc. | 59.2% | $13.6M | 0 | 2 | 0 | Aug 2026 | |
| 5 | PROTEOSTASIS THERAPEUTICS, INC. | 57.2% | $25.2M | 0 | 9 | 16 | Aug 2026 | |
| 6 | Homology Medicines, Inc. | 56.9% | $20.5M | 0 | 0 | 0 | Aug 2026 | |
| 7 | AQUINOX PHARMACEUTICALS, INC | 54.5% | $19.6M | 2 | 8 | 2 | Aug 2026 | |
| 8 | Evofem Biosciences, Inc. | 53.2% | $13.6M | 0 | 0 | 0 | Aug 2026 | |
| 9 | Gemphire Therapeutics Inc. | 52.3% | $1.5M | 0 | 2 | 2 | Aug 2026 | |
| 10 | EYENOVIA, INC. | 51.0% | $6.8M | 1 | 8 | 1 | Aug 2026 | |
| 11 | Unum Therapeutics, Inc. | 50.8% | $64.8M | 0 | 1 | 33 | Aug 2026 | |
| 12 | resTORbio, Inc. | 50.6% | $40.0M | 1 | 0 | 1 | Aug 2026 | |
| 13 | RELMADA THERAPEUTICS, INC. | 50.4% | ? | 0 | 4 | 0 | Aug 2026 | |
| 14 | Atossa Genetics Inc | 50.3% | ? | 0 | 2 | 0 | Aug 2026 | |

**Total: 14 companies**

## Section D: All 375 Companies Sorted by Risk Score

| # | Company | Risk Score | Predicted | Actual | CIK |
|---|---------|-----------|-----------|--------|-----|
| 1 | Relypsa Inc | 93.1% | deregistered_or_delist | deregistered_or_delist | 0001416792 |
| 2 | Poseida Therapeutics, Inc. | 92.7% | deregistered_or_delist | deregistered_or_delist | 0001661460 |
| 3 | Allakos Inc. | 92.3% | deregistered_or_delist | deregistered_or_delist | 0001564824 |
| 4 | ZS Pharma, Inc. | 92.0% | deregistered_or_delist | deregistered_or_delist | 0001459266 |
| 5 | TESARO, Inc. | 91.8% | deregistered_or_delist | deregistered_or_delist | 0001491576 |
| 6 | Dermira, Inc. | 91.4% | deregistered_or_delist | deregistered_or_delist | 0001557883 |
| 7 | Principia Biopharma Inc. | 91.3% | deregistered_or_delist | deregistered_or_delist | 0001510487 |
| 8 | Allena Pharmaceuticals, Inc. | 91.3% | deregistered_or_delist | deregistered_or_delist | 0001624658 |
| 9 | G1 Therapeutics, Inc. | 90.9% | deregistered_or_delist | deregistered_or_delist | 0001560241 |
| 10 | Inhibrx, Inc. | 90.9% | deregistered_or_delist | deregistered_or_delist | 0001739614 |
| 11 | ADURO BIOTECH, INC. | 90.4% | deregistered_or_delist | deregistered_or_delist | 0001435049 |
| 12 | Morphic Holding, Inc. | 90.0% | deregistered_or_delist | deregistered_or_delist | 0001679363 |
| 13 | RAPT Therapeutics, Inc. | 89.9% | deregistered_or_delist | deregistered_or_delist | 0001673772 |
| 14 | Gritstone Oncology, Inc. | 89.6% | deregistered_or_delist | deregistered_or_delist | 0001656634 |
| 15 | KYTHERA BIOPHARMACEUTICALS INC | 89.3% | deregistered_or_delist | deregistered_or_delist | 0001436304 |
| 16 | TETRAPHASE PHARMACEUTICALS INC | 89.2% | deregistered_or_delist | deregistered_or_delist | 0001373707 |
| 17 | Clearside Biomedical, Inc. | 88.9% | deregistered_or_delist | deregistered_or_delist | 0001539029 |
| 18 | Achaogen Inc | 88.6% | deregistered_or_delist | deregistered_or_delist | 0001301501 |
| 19 | Axcella Health Inc. | 88.2% | deregistered_or_delist | deregistered_or_delist | 0001633070 |
| 20 | Calithera Biosciences, Inc. | 88.1% | deregistered_or_delist | deregistered_or_delist | 0001496671 |
| 21 | TREVENA INC | 88.0% | deregistered_or_delist | deregistered_or_delist | 0001429560 |
| 22 | Oyster Point Pharma, Inc. | 87.9% | deregistered_or_delist | deregistered_or_delist | 0001720725 |
| 23 | Rubius Therapeutics, Inc. | 87.8% | deregistered_or_delist | deregistered_or_delist | 0001709401 |
| 24 | Mirna Therapeutics, Inc. | 87.6% | deregistered_or_delist | deregistered_or_delist | 0001527599 |
| 25 | TCR2 THERAPEUTICS INC. | 87.6% | deregistered_or_delist | deregistered_or_delist | 0001750019 |
| 26 | Prevail Therapeutics Inc. | 87.5% | deregistered_or_delist | deregistered_or_delist | 0001714798 |
| 27 | Neon Therapeutics, Inc. | 87.5% | deregistered_or_delist | deregistered_or_delist | 0001694187 |
| 28 | GLOBEIMMUNE INC | 87.4% | deregistered_or_delist | deregistered_or_delist | 0001245104 |
| 29 | Turning Point Therapeutics, Inc. | 87.4% | deregistered_or_delist | deregistered_or_delist | 0001595893 |
| 30 | TETRALOGIC PHARMACEUTICALS CORP | 86.8% | deregistered_or_delist | deregistered_or_delist | 0001361248 |
| 31 | AERIE PHARMACEUTICALS INC | 86.7% | deregistered_or_delist | deregistered_or_delist | 0001337553 |
| 32 | Harpoon Therapeutics, Inc. | 86.7% | deregistered_or_delist | deregistered_or_delist | 0001708493 |
| 33 | BELLICUM PHARMACEUTICALS, INC | 86.6% | deregistered_or_delist | deregistered_or_delist | 0001358403 |
| 34 | Aimmune Therapeutics, Inc. | 86.2% | deregistered_or_delist | deregistered_or_delist | 0001631650 |
| 35 | Kaleido Biosciences, Inc. | 85.9% | deregistered_or_delist | deregistered_or_delist | 0001751299 |
| 36 | CATABASIS PHARMACEUTICALS INC | 85.9% | deregistered_or_delist | deregistered_or_delist | 0001454789 |
| 37 | OncoMed Pharmaceuticals Inc | 85.7% | deregistered_or_delist | deregistered_or_delist | 0001302573 |
| 38 | Revance Therapeutics, Inc. | 85.7% | deregistered_or_delist | deregistered_or_delist | 0001479290 |
| 39 | Aptinyx Inc. | 85.3% | deregistered_or_delist | deregistered_or_delist | 0001674365 |
| 40 | scPharmaceuticals Inc. | 85.3% | deregistered_or_delist | deregistered_or_delist | 0001604950 |
| 41 | Epizyme, Inc. | 85.0% | deregistered_or_delist | deregistered_or_delist | 0001571498 |
| 42 | Otonomy, Inc. | 85.0% | deregistered_or_delist | deregistered_or_delist | 0001493566 |
| 43 | Regado Biosciences Inc | 84.9% | deregistered_or_delist | deregistered_or_delist | 0001311596 |
| 44 | CONSTELLATION PHARMACEUTICALS INC | 84.9% | deregistered_or_delist | deregistered_or_delist | 0001434418 |
| 45 | Translate Bio, Inc. | 84.9% | deregistered_or_delist | deregistered_or_delist | 0001693415 |
| 46 | AGILE THERAPEUTICS INC | 84.8% | deregistered_or_delist | deregistered_or_delist | 0001261249 |
| 47 | Celladon Corp | 84.6% | deregistered_or_delist | deregistered_or_delist | 0001305253 |
| 48 | Tricida, Inc. | 84.4% | deregistered_or_delist | deregistered_or_delist | 0001595585 |
| 49 | Audentes Therapeutics, Inc. | 84.0% | deregistered_or_delist | deregistered_or_delist | 0001628738 |
| 50 | Spark Therapeutics, Inc. | 84.0% | deregistered_or_delist | deregistered_or_delist | 0001609351 |
| 51 | MERRIMACK PHARMACEUTICALS INC | 83.9% | deregistered_or_delist | deregistered_or_delist | 0001274792 |
| 52 | Forty Seven, Inc. | 83.7% | deregistered_or_delist | deregistered_or_delist | 0001667633 |
| 53 | NGM BIOPHARMACEUTICALS INC | 83.7% | deregistered_or_delist | deregistered_or_delist | 0001426332 |
| 54 | PORTOLA PHARMACEUTICALS INC | 83.6% | deregistered_or_delist | deregistered_or_delist | 0001269021 |
| 55 | Versartis, Inc. | 83.6% | deregistered_or_delist | deregistered_or_delist | 0001513818 |
| 56 | OptiNose, Inc. | 83.5% | deregistered_or_delist | deregistered_or_delist | 0001494650 |
| 57 | MARINUS PHARMACEUTICALS INC | 83.3% | deregistered_or_delist | deregistered_or_delist | 0001267813 |
| 58 | Evelo Biosciences, Inc. | 83.1% | deregistered_or_delist | deregistered_or_delist | 0001694665 |
| 59 | Adamas Pharmaceuticals Inc | 82.8% | deregistered_or_delist | deregistered_or_delist | 0001328143 |
| 60 | AKCEA THERAPEUTICS, INC. | 82.6% | deregistered_or_delist | deregistered_or_delist | 0001662524 |
| 61 | Synthorx, Inc. | 82.3% | deregistered_or_delist | deregistered_or_delist | 0001609727 |
| 62 | CONCERT PHARMACEUTICALS, INC. | 82.2% | deregistered_or_delist | deregistered_or_delist | 0001367920 |
| 63 | Avalanche Biotechnologies, Inc. | 81.9% | deregistered_or_delist | deregistered_or_delist | 0001501756 |
| 64 | Auspex Pharmaceuticals, Inc. | 81.8% | deregistered_or_delist | deregistered_or_delist | 0001454189 |
| 65 | Receptos, Inc. | 81.5% | deregistered_or_delist | deregistered_or_delist | 0001463729 |
| 66 | HOOKIPA Pharma Inc. | 81.4% | deregistered_or_delist | deregistered_or_delist | 0001760542 |
| 67 | ACCELERON PHARMA INC | 81.4% | deregistered_or_delist | deregistered_or_delist | 0001280600 |
| 68 | Cidara Therapeutics, Inc. | 81.3% | deregistered_or_delist | deregistered_or_delist | 0001610618 |
| 69 | SpringWorks Therapeutics, Inc. | 81.3% | deregistered_or_delist | deregistered_or_delist | 0001773427 |
| 70 | GENOCEA BIOSCIENCES, INC. | 81.0% | deregistered_or_delist | deregistered_or_delist | 0001457612 |
| 71 | Evoke Pharma Inc | 81.0% | deregistered_or_delist | deregistered_or_delist | 0001403708 |
| 72 | Jounce Therapeutics, Inc. | 81.0% | deregistered_or_delist | deregistered_or_delist | 0001640455 |
| 73 | Iterum Therapeutics Ltd | 80.9% | deregistered_or_delist | deregistered_or_delist | 0001659323 |
| 74 | Clovis Oncology, Inc. | 80.8% | deregistered_or_delist | deregistered_or_delist | 0001466301 |
| 75 | Ophthotech Corp. | 80.6% | deregistered_or_delist | deregistered_or_delist | 0001410939 |
| 76 | Satsuma Pharmaceuticals, Inc. | 80.5% | deregistered_or_delist | deregistered_or_delist | 0001692830 |
| 77 | Carbylan Therapeutics, Inc. | 80.3% | deregistered_or_delist | deregistered_or_delist | 0001348911 |
| 78 | Immune Design Corp. | 80.2% | deregistered_or_delist | deregistered_or_delist | 0001437786 |
| 79 | Conatus Pharmaceuticals Inc | 80.2% | deregistered_or_delist | deregistered_or_delist | 0001383701 |
| 80 | Eleven Biotherapeutics, Inc. | 80.0% | deregistered_or_delist | deregistered_or_delist | 0001485003 |
| 81 | Atreca, Inc. | 79.9% | deregistered_or_delist | deregistered_or_delist | 0001532346 |
| 82 | Loxo Oncology, Inc. | 79.7% | deregistered_or_delist | deregistered_or_delist | 0001581720 |
| 83 | Viela Bio, Inc. | 79.3% | deregistered_or_delist | deregistered_or_delist | 0001734517 |
| 84 | Neos Therapeutics, Inc. | 79.2% | deregistered_or_delist | deregistered_or_delist | 0001467652 |
| 85 | Aridis Pharmaceuticals, Inc. | 79.1% | deregistered_or_delist | deregistered_or_delist | 0001614067 |
| 86 | Unity Biotechnology, Inc. | 78.8% | deregistered_or_delist | deregistered_or_delist | 0001463361 |
| 87 | Dimension Therapeutics, Inc. | 78.6% | deregistered_or_delist | deregistered_or_delist | 0001592288 |
| 88 | HYPERION THERAPEUTICS INC | 78.4% | deregistered_or_delist | deregistered_or_delist | 0001386858 |
| 89 | Surface Oncology, Inc. | 78.4% | deregistered_or_delist | deregistered_or_delist | 0001718108 |
| 90 | Myovant Sciences Ltd. | 78.4% | deregistered_or_delist | deregistered_or_delist | 0001679082 |
| 91 | APPLIED GENETIC TECHNOLOGIES CORP | 78.3% | deregistered_or_delist | deregistered_or_delist | 0001273636 |
| 92 | Y-mAbs Therapeutics, Inc. | 77.8% | deregistered_or_delist | deregistered_or_delist | 0001722964 |
| 93 | BIND Therapeutics, Inc | 77.8% | deregistered_or_delist | deregistered_or_delist | 0001385228 |
| 94 | Dicerna Pharmaceuticals Inc | 77.4% | deregistered_or_delist | deregistered_or_delist | 0001399529 |
| 95 | Provention Bio, Inc. | 77.1% | deregistered_or_delist | deregistered_or_delist | 0001695357 |
| 96 | Juno Therapeutics, Inc. | 77.0% | deregistered_or_delist | deregistered_or_delist | 0001594864 |
| 97 | LogicBio Therapeutics, Inc. | 77.0% | deregistered_or_delist | deregistered_or_delist | 0001664106 |
| 98 | Codiak BioSciences, Inc. | 76.5% | deregistered_or_delist | deregistered_or_delist | 0001659352 |
| 99 | Neurotrope, Inc. | 76.3% | deregistered_or_delist | deregistered_or_delist | 0001513856 |
| 100 | Deciphera Pharmaceuticals, Inc. | 75.8% | deregistered_or_delist | deregistered_or_delist | 0001654151 |
| 101 | Sienna Biopharmaceuticals, Inc. | 75.7% | deregistered_or_delist | deregistered_or_delist | 0001656328 |
| 102 | FIVE PRIME THERAPEUTICS INC | 75.7% | deregistered_or_delist | deregistered_or_delist | 0001175505 |
| 103 | Novan, Inc. | 75.5% | deregistered_or_delist | deregistered_or_delist | 0001467154 |
| 104 | Mersana Therapeutics, Inc. | 75.2% | deregistered_or_delist | deregistered_or_delist | 0001442836 |
| 105 | Zosano Pharma Corp | 75.0% | deregistered_or_delist | deregistered_or_delist | 0001587221 |
| 106 | Karuna Therapeutics, Inc. | 74.6% | deregistered_or_delist | deregistered_or_delist | 0001771917 |
| 107 | Eidos Therapeutics, Inc. | 74.2% | deregistered_or_delist | deregistered_or_delist | 0001731831 |
| 108 | CoLucid Pharmaceuticals, Inc. | 74.1% | deregistered_or_delist | deregistered_or_delist | 0001348649 |
| 109 | Durata Therapeutics, Inc. | 74.0% | deregistered_or_delist | deregistered_or_delist | 0001544116 |
| 110 | ARMO BioSciences, Inc. | 73.9% | deregistered_or_delist | deregistered_or_delist | 0001693664 |
| 111 | CHIMERIX INC | 73.9% | deregistered_or_delist | deregistered_or_delist | 0001117480 |
| 112 | PhaseBio Pharmaceuticals Inc | 73.8% | deregistered_or_delist | deregistered_or_delist | 0001169245 |
| 113 | ALDER BIOPHARMACEUTICALS INC | 73.7% | deregistered_or_delist | deregistered_or_delist | 0001423824 |
| 114 | MyoKardia Inc | 73.6% | deregistered_or_delist | deregistered_or_delist | 0001552451 |
| 115 | SOPHIRIS BIO INC. | 73.5% | deregistered_or_delist | deregistered_or_delist | 0001563855 |
| 116 | Vitae Pharmaceuticals, Inc | 72.0% | deregistered_or_delist | deregistered_or_delist | 0001157602 |
| 117 | Kite Pharma, Inc. | 71.7% | deregistered_or_delist | deregistered_or_delist | 0001510580 |
| 118 | Akero Therapeutics, Inc. | 71.6% | deregistered_or_delist | deregistered_or_delist | 0001744659 |
| 119 | Insys Therapeutics, Inc. | 71.3% | deregistered_or_delist | deregistered_or_delist | 0001516479 |
| 120 | Urovant Sciences Ltd. | 71.2% | deregistered_or_delist | deregistered_or_delist | 0001740547 |
| 121 | Pfenex Inc. | 71.1% | deregistered_or_delist | deregistered_or_delist | 0001478121 |
| 122 | Acucela Inc | 70.6% | deregistered_or_delist | deregistered_or_delist | 0001400482 |
| 123 | Omthera Pharmaceuticals, Inc. | 70.6% | deregistered_or_delist | deregistered_or_delist | 0001477598 |
| 124 | 89bio, Inc. | 70.0% | deregistered_or_delist | deregistered_or_delist | 0001785173 |
| 125 | Ra Pharmaceuticals, Inc. | 69.8% | deregistered_or_delist | deregistered_or_delist | 0001481512 |
| 126 | Global Blood Therapeutics, Inc. | 69.7% | deregistered_or_delist | deregistered_or_delist | 0001629137 |
| 127 | PHASERX, INC. | 69.5% | deregistered_or_delist | deregistered_or_delist | 0001429386 |
| 128 | Sage Therapeutics, Inc. | 69.0% | deregistered_or_delist | deregistered_or_delist | 0001597553 |
| 129 | ARATANA THERAPEUTICS, INC. | 68.9% | deregistered_or_delist | deregistered_or_delist | 0001509190 |
| 130 | Civitas Therapeutics, Inc. | 68.7% | stalled_filing | stalled_filing | 0001509697 |
| 131 | Entasis Therapeutics Holdings Inc. | 68.7% | deregistered_or_delist | deregistered_or_delist | 0001724344 |
| 132 | IGM Biosciences, Inc. | 68.4% | deregistered_or_delist | deregistered_or_delist | 0001496323 |
| 133 | EAGLE PHARMACEUTICALS, INC. | 67.9% | deregistered_or_delist | deregistered_or_delist | 0000827871 |
| 134 | KOLLTAN PHARMACEUTICALS INC | 67.7% | deregistered_or_delist | stalled_filing | 0001442835 |
| 135 | Esperion Therapeutics Inc | 67.0% | deregistered_or_delist | deregistered_or_delist | 0001434868 |
| 136 | Peloton Therapeutics, Inc. | 67.0% | stalled_filing | stalled_filing | 0001525145 |
| 137 | Aralez Pharmaceuticals Inc. | 66.7% | deregistered_or_delist | deregistered_or_delist | 0001660719 |
| 138 | Flexion Therapeutics Inc | 65.5% | deregistered_or_delist | deregistered_or_delist | 0001419600 |
| 139 | Dova Pharmaceuticals, Inc. | 65.4% | deregistered_or_delist | deregistered_or_delist | 0001685071 |
| 140 | NephroGenex, Inc. | 65.1% | deregistered_or_delist | deregistered_or_delist | 0001338095 |
| 141 | ALPINE IMMUNE SCIENCES, INC. | 64.6% | deregistered_or_delist | deregistered_or_delist | 0001626199 |
| 142 | Centrexion Therapeutics Corp | 64.5% | stalled_filing | stalled_filing | 0001592052 |
| 143 | bluebird bio, Inc. | 64.4% | deregistered_or_delist | deregistered_or_delist | 0001293971 |
| 144 | AveXis, Inc. | 64.4% | deregistered_or_delist | deregistered_or_delist | 0001652923 |
| 145 | PREMIER BIOMEDICAL INC | 64.4% | deregistered_or_delist | deregistered_or_delist | 0001515740 |
| 146 | BiomX Inc. | 64.4% | deregistered_or_delist | actively_filing | 0001739174 |
| 147 | Lumena Pharmaceuticals, Inc. | 64.3% | deregistered_or_delist | stalled_filing | 0001513157 |
| 148 | Abpro Corp | 63.9% | deregistered_or_delist | deregistered_or_delist | 0001670356 |
| 149 | TFF Pharmaceuticals, Inc. | 62.9% | deregistered_or_delist | deregistered_or_delist | 0001733413 |
| 150 | Menlo Therapeutics, Inc. | 62.6% | deregistered_or_delist | actively_filing | 0001566044 |
| 151 | Cancer Prevention Pharmaceuticals, Inc. | 62.5% | stalled_filing | stalled_filing | 0001471002 |
| 152 | Athenex, Inc. | 62.4% | deregistered_or_delist | deregistered_or_delist | 0001300699 |
| 153 | Phio Pharmaceuticals Corp. | 62.4% | deregistered_or_delist | actively_filing | 0001533040 |
| 154 | Applied Therapeutics Inc. | 61.9% | deregistered_or_delist | deregistered_or_delist | 0001697532 |
| 155 | Vaccinex Inc | 61.8% | deregistered_or_delist | deregistered_or_delist | 0001205922 |
| 156 | CHIASMA, INC | 61.4% | deregistered_or_delist | deregistered_or_delist | 0001339469 |
| 157 | ANTERIOS INC | 61.2% | stalled_filing | stalled_filing | 0001390085 |
| 158 | Viamet Pharmaceuticals Holdings LLC | 61.1% | stalled_filing | stalled_filing | 0001538928 |
| 159 | Tobira Therapeutics, Inc. | 60.9% | stalled_filing | stalled_filing | 0001409690 |
| 160 | STEMLINE THERAPEUTICS INC | 60.9% | deregistered_or_delist | deregistered_or_delist | 0001264587 |
| 161 | Inpellis, Inc. | 60.6% | stalled_filing | stalled_filing | 0001638851 |
| 162 | SteadyMed Ltd. | 60.2% | deregistered_or_delist | deregistered_or_delist | 0001619087 |
| 163 | Matinas BioPharma Holdings, Inc. | 59.2% | deregistered_or_delist | actively_filing | 0001582554 |
| 164 | Cirius Therapeutics, Inc. | 59.2% | stalled_filing | stalled_filing | 0001702956 |
| 165 | ProNAi Therapeutics Inc | 58.8% | deregistered_or_delist | deregistered_or_delist | 0001290149 |
| 166 | Dance Biopharm, Inc. | 58.4% | stalled_filing | stalled_filing | 0001596126 |
| 167 | CEMPRA, INC. | 58.1% | deregistered_or_delist | deregistered_or_delist | 0001461993 |
| 168 | Blueprint Medicines Corp | 57.7% | stalled_filing | deregistered_or_delist | 0001597264 |
| 169 | SANCILIO PHARMACEUTICALS COMPANY, INC. | 57.3% | stalled_filing | stalled_filing | 0001641908 |
| 170 | PROTEOSTASIS THERAPEUTICS, INC. | 57.2% | deregistered_or_delist | actively_filing | 0001445283 |
| 171 | Dermavant Sciences Ltd | 57.1% | stalled_filing | stalled_filing | 0001753483 |
| 172 | Homology Medicines, Inc. | 56.9% | deregistered_or_delist | actively_filing | 0001661998 |
| 173 | CONTRAFECT Corp | 56.3% | stalled_filing | stalled_filing | 0001478069 |
| 174 | Corium International, Inc. | 55.8% | deregistered_or_delist | deregistered_or_delist | 0001594337 |
| 175 | THAR PHARMACEUTICALS INC | 55.8% | stalled_filing | stalled_filing | 0001428369 |
| 176 | TYME TECHNOLOGIES, INC. | 55.5% | stalled_filing | deregistered_or_delist | 0001537917 |
| 177 | Ignyta, Inc. | 55.5% | stalled_filing | deregistered_or_delist | 0001557421 |
| 178 | Regulus Therapeutics Inc. | 55.5% | deregistered_or_delist | deregistered_or_delist | 0001505512 |
| 179 | ALZHEON, INC. | 54.9% | stalled_filing | stalled_filing | 0001582636 |
| 180 | AQUINOX PHARMACEUTICALS, INC | 54.5% | deregistered_or_delist | actively_filing | 0001404644 |
| 181 | Axovant Sciences Ltd. | 54.5% | stalled_filing | stalled_filing | 0001636050 |
| 182 | S1 Biopharma, Inc. | 54.3% | stalled_filing | stalled_filing | 0001613723 |
| 183 | Aptalis Holdings Inc. | 54.1% | stalled_filing | stalled_filing | 0001588172 |
| 184 | Oncolix, Inc. | 53.7% | stalled_filing | stalled_filing | 0001584137 |
| 185 | Evofem Biosciences, Inc. | 53.2% | deregistered_or_delist | actively_filing | 0001618835 |
| 186 | Egalet Corp | 53.1% | stalled_filing | stalled_filing | 0001586105 |
| 187 | Visterra, Inc. | 53.0% | stalled_filing | stalled_filing | 0001426375 |
| 188 | Zynerba Pharmaceuticals, Inc. | 52.8% | stalled_filing | deregistered_or_delist | 0001621443 |
| 189 | Recro Pharma, Inc. | 52.8% | stalled_filing | deregistered_or_delist | 0001588972 |
| 190 | CARDAX, INC. | 52.4% | stalled_filing | stalled_filing | 0001544238 |
| 191 | Gemphire Therapeutics Inc. | 52.3% | deregistered_or_delist | actively_filing | 0001638287 |
| 192 | BioCardia, Inc. | 51.5% | stalled_filing | stalled_filing | 0001635886 |
| 193 | AMBRX INC | 51.1% | stalled_filing | stalled_filing | 0001264647 |
| 194 | EYENOVIA, INC. | 51.0% | deregistered_or_delist | actively_filing | 0001682639 |
| 195 | Unum Therapeutics, Inc. | 50.8% | deregistered_or_delist | actively_filing | 0001622229 |
| 196 | resTORbio, Inc. | 50.6% | deregistered_or_delist | actively_filing | 0001720580 |
| 197 | RELMADA THERAPEUTICS, INC. | 50.4% | stalled_filing | actively_filing | 0001553643 |
| 198 | Atossa Genetics Inc | 50.3% | stalled_filing | actively_filing | 0001488039 |
| 199 | Celsus Therapeutics Plc. | 49.7% | stalled_filing | actively_filing | 0001541157 |
| 200 | Bellerophon Therapeutics, Inc. | 49.7% | stalled_filing | deregistered_or_delist | 0001600132 |
| 201 | Virobay Inc | 49.7% | stalled_filing | stalled_filing | 0001374261 |
| 202 | Dipexium Pharmaceuticals, LLC | 49.3% | stalled_filing | deregistered_or_delist | 0001497504 |
| 203 | AntriaBio, Inc. | 49.3% | stalled_filing | actively_filing | 0001509261 |
| 204 | MultiVir Inc. | 49.3% | stalled_filing | stalled_filing | 0001613490 |
| 205 | Regen BioPharma Inc | 49.3% | stalled_filing | actively_filing | 0001589150 |
| 206 | Aralez Pharmaceuticals Ltd | 49.3% | stalled_filing | stalled_filing | 0001648419 |
| 207 | Odonate Therapeutics, LLC | 49.3% | stalled_filing | deregistered_or_delist | 0001717452 |
| 208 | Braeburn Pharmaceuticals, Inc. | 49.2% | stalled_filing | stalled_filing | 0001688765 |
| 209 | Rib-X Pharmaceuticals, Inc. | 49.2% | stalled_filing | stalled_filing | 0001164994 |
| 210 | AUDEO ONCOLOGY, INC. | 49.1% | stalled_filing | stalled_filing | 0001552899 |
| 211 | CohBar, Inc. | 49.1% | stalled_filing | deregistered_or_delist | 0001522602 |
| 212 | Kannalife Inc | 49.1% | stalled_filing | stalled_filing | 0001615999 |
| 213 | Enumeral Biomedical Holdings, Inc. | 49.1% | stalled_filing | stalled_filing | 0001561551 |
| 214 | Propanc Biopharma, Inc. | 49.1% | stalled_filing | actively_filing | 0001517681 |
| 215 | Spring Bank Pharmaceuticals, Inc. | 49.1% | stalled_filing | deregistered_or_delist | 0001566373 |
| 216 | NANOANTIBIOTICS, INC. | 49.1% | stalled_filing | actively_filing | 0001580149 |
| 217 | Sun BioPharma, Inc. | 49.1% | stalled_filing | actively_filing | 0001029125 |
| 218 | IASO BioMed, Inc. | 49.1% | stalled_filing | stalled_filing | 0001662907 |
| 219 | Ruthigen, Inc. | 49.1% | stalled_filing | actively_filing | 0001574235 |
| 220 | MICROLIN BIO, INC. | 49.1% | stalled_filing | stalled_filing | 0001590930 |
| 221 | Nexvet Biopharma plc | 49.1% | stalled_filing | deregistered_or_delist | 0001618561 |
| 222 | Vyrix Pharmaceuticals, Inc. | 49.1% | stalled_filing | stalled_filing | 0001602413 |
| 223 | Sunset Island Group | 49.1% | stalled_filing | stalled_filing | 0001689066 |
| 224 | Cell Source, Inc. | 49.1% | stalled_filing | actively_filing | 0001569340 |
| 225 | Adgero Biopharmaceuticals Holdings, Inc. | 49.1% | stalled_filing | stalled_filing | 0001657598 |
| 226 | Osmotica Pharmaceuticals plc | 49.1% | stalled_filing | deregistered_or_delist | 0001739426 |
| 227 | Scopus Biopharma Inc. | 49.1% | stalled_filing | deregistered_or_delist | 0001772028 |
| 228 | Health-Right Discoveries, Inc. | 49.1% | stalled_filing | stalled_filing | 0001537663 |
| 229 | Zomedica Pharmaceuticals Corp. | 49.1% | stalled_filing | actively_filing | 0001684144 |
| 230 | Patheon N.V. | 49.1% | stalled_filing | deregistered_or_delist | 0001643848 |
| 231 | Stellar Biotechnologies, Inc. | 49.1% | stalled_filing | actively_filing | 0001540159 |
| 232 | Nemus Bioscience, Inc. | 49.1% | stalled_filing | actively_filing | 0001516551 |
| 233 | Accelerated Pharma, Inc. | 48.4% | stalled_filing | stalled_filing | 0001630970 |
| 234 | Cerulean Pharma Inc. | 48.4% | actively_filing | actively_filing | 0001401914 |
| 235 | PLX PHARMA INC. | 48.3% | stalled_filing | stalled_filing | 0001291520 |
| 236 | ZAFGEN, INC. | 48.2% | actively_filing | actively_filing | 0001374690 |
| 237 | AILERON THERAPEUTICS INC | 48.0% | actively_filing | actively_filing | 0001420565 |
| 238 | Conkwest, Inc. | 47.9% | actively_filing | actively_filing | 0001326110 |
| 239 | Cerecor Inc. | 47.7% | actively_filing | actively_filing | 0001534120 |
| 240 | LBC Bioscience Inc. | 47.5% | stalled_filing | stalled_filing | 0001683743 |
| 241 | Zander Therapeutics, Inc | 47.4% | stalled_filing | stalled_filing | 0001718644 |
| 242 | PAR PHARMACEUTICAL HOLDINGS, INC. | 47.2% | stalled_filing | stalled_filing | 0001559149 |
| 243 | Flex Pharma, Inc. | 47.1% | actively_filing | actively_filing | 0001615219 |
| 244 | PARATEK PHARMACEUTICALS INC | 46.8% | stalled_filing | stalled_filing | 0001037643 |
| 245 | BioNTech SE | 46.5% | stalled_filing | stalled_filing | 0001776985 |
| 246 | Aeglea BioTherapeutics, Inc. | 46.4% | actively_filing | actively_filing | 0001636282 |
| 247 | AC Immune SA | 46.4% | stalled_filing | stalled_filing | 0001651625 |
| 248 | Shuttle Pharmaceuticals, Inc. | 45.8% | stalled_filing | stalled_filing | 0001685462 |
| 249 | DiaMedica Therapeutics Inc. | 43.8% | actively_filing | actively_filing | 0001401040 |
| 250 | China Sxt Pharms Inc | 43.7% | stalled_filing | stalled_filing | 0001723980 |
| 251 | GLYCOMIMETICS INC | 43.5% | actively_filing | actively_filing | 0001253689 |
| 252 | Ascendis Pharma A/S | 43.3% | stalled_filing | stalled_filing | 0001612042 |
| 253 | InflaRx NV (Fireman BV?) | 42.6% | stalled_filing | stalled_filing | 0001708688 |
| 254 | KEMPHARM, INC | 42.6% | stalled_filing | actively_filing | 0001434647 |
| 255 | Kadmon Holdings, Inc. | 42.5% | stalled_filing | stalled_filing | 0001557142 |
| 256 | Sol-Gel Technologies Ltd | 42.2% | stalled_filing | stalled_filing | 0001684693 |
| 257 | Beam Therapeutics Inc. | 42.1% | actively_filing | actively_filing | 0001745999 |
| 258 | Onconova Therapeutics, Inc. | 41.8% | actively_filing | actively_filing | 0001130598 |
| 259 | Aquestive Therapeutics Inc | 41.1% | actively_filing | actively_filing | 0001398733 |
| 260 | AVROBIO, Inc. | 41.0% | actively_filing | actively_filing | 0001681087 |
| 261 | Lipocine Inc. | 40.8% | actively_filing | actively_filing | 0001535955 |
| 262 | PDS Biotechnology Corp | 40.5% | actively_filing | actively_filing | 0001472091 |
| 263 | Cortexyme, Inc. | 39.9% | actively_filing | actively_filing | 0001662774 |
| 264 | NuCana plc | 39.8% | stalled_filing | stalled_filing | 0001709626 |
| 265 | Outlook Therapeutics, Inc. | 37.9% | actively_filing | actively_filing | 0001649989 |
| 266 | Tocagen Inc | 37.8% | actively_filing | actively_filing | 0001419041 |
| 267 | Hoth Therapeutics, Inc. | 37.7% | actively_filing | actively_filing | 0001711786 |
| 268 | FIBROGEN INC | 37.4% | stalled_filing | actively_filing | 0000921299 |
| 269 | Novus Therapeutics, Inc. | 37.4% | stalled_filing | actively_filing | 0001404281 |
| 270 | Amphastar Pharmaceuticals Inc | 36.8% | actively_filing | actively_filing | 0001297184 |
| 271 | SELECTA BIOSCIENCES INC | 36.6% | actively_filing | actively_filing | 0001453687 |
| 272 | EYEGATE PHARMACEUTICALS INC | 36.1% | actively_filing | actively_filing | 0001372514 |
| 273 | VITAL THERAPIES INC | 35.3% | actively_filing | actively_filing | 0001280776 |
| 274 | Minerva Neurosciences Inc | 33.8% | actively_filing | actively_filing | 0001598646 |
| 275 | PROTEON THERAPEUTICS INC | 32.5% | actively_filing | actively_filing | 0001359931 |
| 276 | aTYR PHARMA INC | 32.1% | actively_filing | actively_filing | 0001339970 |
| 277 | HEAT BIOLOGICS, INC. | 30.6% | actively_filing | actively_filing | 0001476963 |
| 278 | Frequency Therapeutics, Inc. | 30.2% | actively_filing | actively_filing | 0001703647 |
| 279 | Annovis Bio, Inc. | 29.6% | actively_filing | actively_filing | 0001477845 |
| 280 | ProQR Therapeutics BV | 29.3% | stalled_filing | stalled_filing | 0001612940 |
| 281 | Cara Therapeutics, Inc. | 29.0% | actively_filing | actively_filing | 0001346830 |
| 282 | Angion Biomedica Corp. | 28.7% | actively_filing | actively_filing | 0001601485 |
| 283 | Magenta Therapeutics, Inc. | 28.1% | actively_filing | actively_filing | 0001690585 |
| 284 | Bicycle Therapeutics Ltd | 28.1% | actively_filing | actively_filing | 0001761612 |
| 285 | LEAP THERAPEUTICS, INC. | 27.9% | actively_filing | actively_filing | 0001509745 |
| 286 | INOTEK PHARMACEUTICALS CORP | 26.5% | actively_filing | actively_filing | 0001281895 |
| 287 | 4D Molecular Therapeutics Inc | 25.8% | actively_filing | actively_filing | 0001650648 |
| 288 | uniQure BV | 25.7% | actively_filing | actively_filing | 0001590560 |
| 289 | Amneal Pharmaceuticals, Inc. | 24.7% | actively_filing | actively_filing | 0001723128 |
| 290 | Arsanis, Inc. | 23.9% | actively_filing | actively_filing | 0001501697 |
| 291 | Inmune Bio Inc | 22.5% | actively_filing | actively_filing | 0001711754 |
| 292 | Liquidia Technologies Inc | 22.3% | actively_filing | actively_filing | 0001819576 |
| 293 | Kodiak Sciences Inc | 22.1% | actively_filing | actively_filing | 0001468748 |
| 294 | XBiotech Inc | 21.3% | actively_filing | actively_filing | 0001626878 |
| 295 | Zymeworks Inc | 20.8% | actively_filing | actively_filing | 0001937653 |
| 296 | Zoetis Inc | 20.5% | actively_filing | actively_filing | 0001555280 |
| 297 | Enanta Pharmaceuticals Inc | 19.1% | actively_filing | actively_filing | 0001177648 |
| 298 | BeiGene, Ltd. | 18.9% | actively_filing | actively_filing | 0001651308 |
| 299 | PTC Therapeutics Inc | 18.9% | actively_filing | actively_filing | 0001070081 |
| 300 | Ardelyx Inc | 18.7% | actively_filing | actively_filing | 0001437402 |
| 301 | MacroGenics | 18.5% | actively_filing | actively_filing | 0001125345 |
| 302 | CytomX Therapeutics Inc | 18.1% | actively_filing | actively_filing | 0001501989 |
| 303 | vTv Therapeutics Inc | 17.6% | actively_filing | actively_filing | 0001641489 |
| 304 | Xenon Pharmaceuticals Inc | 17.5% | actively_filing | actively_filing | 0001582313 |
| 305 | Galera Therapeutics Inc | 17.1% | actively_filing | actively_filing | 0001563577 |
| 306 | Sutro Biopharma Inc | 17.0% | actively_filing | actively_filing | 0001382101 |
| 307 | Milestone Pharmaceuticals Inc | 16.4% | actively_filing | actively_filing | 0001408443 |
| 308 | Entera Bio Ltd | 15.3% | actively_filing | actively_filing | 0001638097 |
| 309 | SCYNEXIS Inc | 13.5% | actively_filing | actively_filing | 0001178253 |
| 310 | Xencor Inc | 13.2% | actively_filing | actively_filing | 0001326732 |
| 311 | Aclaris Therapeutics Inc | 13.1% | actively_filing | actively_filing | 0001557746 |
| 312 | Gossamer Bio Inc | 12.7% | actively_filing | actively_filing | 0001728117 |
| 313 | Urogen Pharma Ltd | 12.3% | actively_filing | actively_filing | 0001668243 |
| 314 | Scholar Rock Holding Corp | 12.2% | actively_filing | actively_filing | 0001727196 |
| 315 | Precision Biosciences Inc | 12.1% | actively_filing | actively_filing | 0001357874 |
| 316 | CNS Pharmaceuticals Inc | 11.3% | actively_filing | actively_filing | 0001729427 |
| 317 | Alector Inc | 10.6% | actively_filing | actively_filing | 0001653087 |
| 318 | Moderna Inc | 10.6% | actively_filing | actively_filing | 0001682852 |
| 319 | Verastem Inc | 10.5% | actively_filing | actively_filing | 0001526119 |
| 320 | Collegium Pharmaceutical Inc | 10.3% | actively_filing | actively_filing | 0001267565 |
| 321 | Regenxbio Inc | 10.2% | actively_filing | actively_filing | 0001590877 |
| 322 | Aprea Therapeutics Inc | 9.9% | actively_filing | actively_filing | 0001781983 |
| 323 | Akebia Therapeutics Inc | 9.6% | actively_filing | actively_filing | 0001517022 |
| 324 | Fate Therapeutics | 9.6% | actively_filing | actively_filing | 0001434316 |
| 325 | Kala Pharmaceuticals Inc | 9.5% | actively_filing | actively_filing | 0001479419 |
| 326 | Solid Biosciences LLC | 9.3% | actively_filing | actively_filing | 0001707502 |
| 327 | Zai Lab Ltd | 8.7% | actively_filing | actively_filing | 0001704292 |
| 328 | Beyondspring Inc | 7.7% | actively_filing | actively_filing | 0001677940 |
| 329 | Ultragenyx Pharmaceutical | 7.7% | actively_filing | actively_filing | 0001515673 |
| 330 | Aldeyra Therapeutics Inc | 7.5% | actively_filing | actively_filing | 0001341235 |
| 331 | Cue Biopharma Inc | 7.5% | actively_filing | actively_filing | 0001645460 |
| 332 | Rhythm Pharmaceuticals Inc | 7.5% | actively_filing | actively_filing | 0001649904 |
| 333 | Protagonist Therapeutics Inc | 7.4% | actively_filing | actively_filing | 0001377121 |
| 334 | Coherus Biosciences Inc | 7.3% | actively_filing | actively_filing | 0001512762 |
| 335 | Kiniksa Pharmaceuticals LTD | 7.2% | actively_filing | actively_filing | 0001730430 |
| 336 | Viking Therapeutics Inc | 7.1% | actively_filing | actively_filing | 0001607678 |
| 337 | Ideaya Biosciences Inc | 7.0% | actively_filing | actively_filing | 0001676725 |
| 338 | Karyopharm Therapeutics | 7.0% | actively_filing | actively_filing | 0001503802 |
| 339 | Syndax Pharmaceuticals Inc | 6.6% | actively_filing | actively_filing | 0001395937 |
| 340 | Autolus Therapeutics Ltd | 6.5% | actively_filing | actively_filing | 0001730463 |
| 341 | Crinetics Pharmaceuticals Inc | 6.2% | actively_filing | actively_filing | 0001658247 |
| 342 | Phathom Pharmaceuticals Inc | 6.2% | actively_filing | actively_filing | 0001783183 |
| 343 | Bioxcel Therapeutics Inc | 6.0% | actively_filing | actively_filing | 0001720893 |
| 344 | Moleculin Biotech Inc | 6.0% | actively_filing | actively_filing | 0001659617 |
| 345 | Equillium | 6.0% | actively_filing | actively_filing | 0001746466 |
| 346 | Evolus Inc | 5.9% | actively_filing | actively_filing | 0001570562 |
| 347 | Ocular Therapeutix Inc | 5.8% | actively_filing | actively_filing | 0001393434 |
| 348 | Replimune Group Inc | 5.7% | actively_filing | actively_filing | 0001737953 |
| 349 | Trevi Therapeutics Inc | 5.7% | actively_filing | actively_filing | 0001563880 |
| 350 | AnaptysBio Inc | 5.5% | actively_filing | actively_filing | 0001370053 |
| 351 | Axsome Therapeutics Inc | 5.4% | actively_filing | actively_filing | 0001579428 |
| 352 | Verrica Pharmaceuticals Inc | 5.0% | actively_filing | actively_filing | 0001660334 |
| 353 | Cabaletta Bio Inc | 4.9% | actively_filing | actively_filing | 0001759138 |
| 354 | Genprex | 4.7% | actively_filing | actively_filing | 0001595248 |
| 355 | Mirum Pharmaceuticals Inc | 4.5% | actively_filing | actively_filing | 0001759425 |
| 356 | Arvinas Holding Co LLC | 4.4% | actively_filing | actively_filing | 0001655759 |
| 357 | Twist Bioscience Corp | 4.2% | actively_filing | actively_filing | 0001581280 |
| 358 | Spero Therapeutics Inc | 3.9% | actively_filing | actively_filing | 0001701108 |
| 359 | Denali Therapeutics Inc | 3.8% | actively_filing | actively_filing | 0001714899 |
| 360 | Seres Therapeutics Inc | 3.0% | actively_filing | actively_filing | 0001609809 |
| 361 | Voyager Therapeutics Inc | 2.7% | actively_filing | actively_filing | 0001640266 |
| 362 | Arcus Biosciences Inc | 2.7% | actively_filing | actively_filing | 0001724521 |
| 363 | Ovid Therapeutics Inc | 2.5% | actively_filing | actively_filing | 0001636651 |
| 364 | Krystal Biotech Inc | 2.4% | actively_filing | actively_filing | 0001711279 |
| 365 | Vir Biotechnology Inc | 2.4% | actively_filing | actively_filing | 0001706431 |
| 366 | Stoke Therapeutics Inc | 2.4% | actively_filing | actively_filing | 0001623526 |
| 367 | Fulcrum Therapeutics Inc | 2.1% | actively_filing | actively_filing | 0001680581 |
| 368 | CRISPR Therapeutics AG | 2.1% | actively_filing | actively_filing | 0001674416 |
| 369 | Editas Medicine Inc | 1.7% | actively_filing | actively_filing | 0001650664 |
| 370 | Allogene Therapeutics Inc. | 1.7% | actively_filing | actively_filing | 0001737287 |
| 371 | NextCure Inc | 1.7% | actively_filing | actively_filing | 0001661059 |
| 372 | BridgeBio Pharma Inc | 1.2% | actively_filing | actively_filing | 0001743881 |
| 373 | Meiragtx Holdings Plc | 1.2% | actively_filing | actively_filing | 0001735438 |
| 374 | Corvus Pharmaceuticals Inc | 1.0% | actively_filing | actively_filing | 0001626971 |
| 375 | WaVe Life Sciences Ltd | 0.9% | actively_filing | actively_filing | 0001631574 |
