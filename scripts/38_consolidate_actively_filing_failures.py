"""
Step 4.3j: Consolidate the extended actively_filing investigation into
the master outcome-label system. Two things happening here that haven't
happened before in this pipeline:

1. These 12 companies were sitting in outcome_triage.csv's
   "actively_filing" bucket, never in exit_reasons.csv at all, that file
   only ever covered the 224 companies that had stopped filing. Since
   these are now confirmed failures, they need to be ADDED to
   exit_reasons.csv as new rows, not just relabeled somewhere they
   already existed.

2. GridIron BioNutrients gets removed entirely, a second confirmed
   scope violation (a beverage company, never a real biotech), same
   category as Dynamic Nutra Enterprises Holdings.

Run with: python scripts/38_consolidate_actively_filing_failures.py

Input:  data/processed/exit_reasons.csv
        data/processed/outcome_triage.csv
        data/processed/final_roster.csv
Output: all three overwritten
"""

from pathlib import Path

import pandas as pd

EXIT_PATH = Path("data/processed/exit_reasons.csv")
TRIAGE_PATH = Path("data/processed/outcome_triage.csv")
ROSTER_PATH = Path("data/processed/final_roster.csv")

CONFIRMED_FAILURES = {
    "Zafgen, Inc.": {
        "exit_subtype": "reverse_merger",
        "evidence_note": "Beloranib caused 2 patient deaths in Phase 3 (bestPWS trial), FDA partial clinical hold, drug discontinued on safety grounds. Reverse merged, became Larimar Therapeutics.",
    },
    "Tocagen Inc": {
        "exit_subtype": "reverse_merger",
        "evidence_note": "Toca 511/Toca FC missed Phase 3 primary endpoint (Toca 5 trial, 2019). 65% layoffs. Reverse merged into Forte Biosciences, shareholders left with ~26%.",
    },
    "Frequency Therapeutics, Inc.": {
        "exit_subtype": "reverse_merger",
        "evidence_note": "FX-322 missed Phase IIb primary endpoint; FX-345 and MS program also discontinued. Reverse merged into Korro Bio, shareholders left with 8%.",
    },
    "AVROBIO, Inc.": {
        "exit_subtype": "reverse_merger",
        "evidence_note": "Halted all remaining gene therapy programs (2023), sold sole viable asset to Novartis for cash. Reverse merged into Tectonic Therapeutic, shareholders left with ~23-25%.",
    },
    "GLYCOMIMETICS INC": {
        "exit_subtype": "reverse_merger",
        "evidence_note": "Uproleselan failed 2 separate Phase 3 trials (2024). Rivipansel sold for $1.2M. Own 10-K: 'we do not currently intend to continue development.' Shareholders left with 3.1%.",
    },
    "PROTEOSTASIS THERAPEUTICS, INC.": {
        "exit_subtype": "reverse_merger",
        "evidence_note": "CF drugs uncompetitive vs Vertex, 79% workforce cut. Reverse merged into Yumanity (2020, all CF drugs sold off), Yumanity's own drug then also failed, merged again into Kineta (2022).",
    },
    "Homology Medicines, Inc.": {
        "exit_subtype": "reverse_merger",
        "evidence_note": "Gene therapy hit FDA hold (liver risk signals); gene editing program for PKU discontinued citing financing environment despite promising data. 87% headcount cut. Reverse merged into Q32 Bio.",
    },
    "Angion Biomedica Corp.": {
        "exit_subtype": "reverse_merger",
        "evidence_note": "ANG-3777 Phase 3 didn't support approval; ANG-3070 Phase 2 terminated for patient safety. Reverse merged into Elicio Therapeutics, shareholders left with 34.8%.",
    },
    "AQUINOX PHARMACEUTICALS, INC": {
        "exit_subtype": "reverse_merger",
        "evidence_note": "Rosiptor failed Phase 3 LEADERSHIP 301 (2018), stock fell 80-85%. Reverse merged into Neoleukin, which itself later merged into Neurogene, three identities under one shell.",
    },
    "Ruthigen, Inc.": {
        "exit_subtype": "reverse_merger",
        "evidence_note": "RUT58-60 (sole candidate) abandoned. Fierce Biotech: deal signals 'the end of the line' for RUT58-60. Reverse merged into Pulmatrix, shareholders left with 19%.",
    },
    "NANOANTIBIOTICS, INC.": {
        "exit_subtype": "program_discontinued",
        "evidence_note": "Original nanotechnology antibiotics program went inactive, unable to secure licensing deals. Acquired LAT Pharma (liver disease asset), became BioVie. Non-dilutive structure (share count preserved), softer confidence than typical reverse-merger cases.",
    },
    "Sun BioPharma, Inc.": {
        "exit_subtype": "zombie",
        "evidence_note": "Same drug program (SBP-101/ivospemin) continued under renames (Panbela Therapeutics), no abandonment or new owner. As of 2026: $0.01/share, $53,400 market cap, practically worthless without formal bankruptcy.",
    },
}

SHELL_COMPANY_NAME = "GridIron BioNutrients, Inc."
SHELL_REASON = (
    "roster scope violation: formed as a probiotic-water beverage company (2017), "
    "went through a 308:1 reverse stock split, became an admitted dormant shell "
    "('Innovation1 Biotech Inc. is a shell company... no operations'), later dealt "
    "in nutraceuticals/supplements, never a real regulated drug developer, confirmed manually"
)


if __name__ == "__main__":
    exits = pd.read_csv(EXIT_PATH, dtype={"cik": str})
    triage = pd.read_csv(TRIAGE_PATH, dtype={"cik": str})
    roster = pd.read_csv(ROSTER_PATH, dtype={"cik": str})

    for col in ["exit_subtype", "evidence_note", "original_exit_reason"]:
        if col not in exits.columns:
            exits[col] = None

    # Add the 12 confirmed failures as NEW rows, they were never in
    # exit_reasons.csv before, only in outcome_triage.csv's actively_filing bucket.
    new_rows = []
    for name, details in CONFIRMED_FAILURES.items():
        match = triage[triage["company_name"] == name]
        if match.empty:
            print(f"WARNING: {name!r} not found in outcome_triage.csv, skipping.")
            continue
        cik = match.iloc[0]["cik"]
        new_rows.append({
            "company_name": name, "cik": cik, "exit_reason": "failure",
            "original_exit_reason": "actively_filing",
            "exit_subtype": details["exit_subtype"],
            "evidence_note": details["evidence_note"],
        })
        print(f"Added: {name} -> failure ({details['exit_subtype']})")

    exits = pd.concat([exits, pd.DataFrame(new_rows)], ignore_index=True)
    exits.to_csv(EXIT_PATH, index=False)
    print(f"\n{len(new_rows)} of {len(CONFIRMED_FAILURES)} added to {EXIT_PATH}.")
    print(exits["exit_reason"].value_counts())

    # Remove the second confirmed shell company from all three files.
    shell_mask_roster = roster["company_name"] == SHELL_COMPANY_NAME
    if shell_mask_roster.any():
        roster = roster[~shell_mask_roster]
        roster.to_csv(ROSTER_PATH, index=False)

        triage = triage[triage["company_name"] != SHELL_COMPANY_NAME]
        triage.to_csv(TRIAGE_PATH, index=False)

        exits = exits[exits["company_name"] != SHELL_COMPANY_NAME]
        exits.to_csv(EXIT_PATH, index=False)

        print(f"\nRemoved {SHELL_COMPANY_NAME!r} from all three files: {SHELL_REASON}")
    else:
        print(f"\nWARNING: {SHELL_COMPANY_NAME!r} not found in roster.")

    print(f"\n{len(roster)} companies remain in {ROSTER_PATH}.")
