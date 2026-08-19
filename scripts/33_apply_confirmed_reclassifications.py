"""
Step 4.3e: Apply confirmed reclassifications from individual research on
companies flagged by the name-divergence check (script 32). Each of
these was verified against primary sources (SEC filings, company press
releases, trade press), not inferred from the mechanical check alone,
that check only identified WHO to research, not the answer itself.

exit_reason becomes "failure" for these (distinct from "bankruptcy",
since none of these filed for formal bankruptcy, they failed clinically
and then exited via reverse merger, dissolution, or an internal pivot).
A new exit_subtype column preserves which kind, since that distinction
matters for the eventual write-up even though all six affect the label
the same way.

This is a hand-curated list, not a mechanical rule, deliberately. Each
entry exists because it was individually verified, more get added here
only after the same standard of evidence, not by broadening a filter.

Run with: python scripts/33_apply_confirmed_reclassifications.py

Input:  data/processed/exit_reasons.csv
Output: data/processed/exit_reasons.csv (overwritten)
"""

from pathlib import Path

import pandas as pd

EXIT_PATH = Path("data/processed/exit_reasons.csv")

CONFIRMED_RECLASSIFICATIONS = {
    "Conatus Pharmaceuticals Inc": {
        "exit_subtype": "reverse_merger",
        "evidence_note": (
            "Emricasan failed 3 Phase 2 trials (ENCORE-NF/LF/PH, 2019), Novartis "
            "exited the partnership, 80% staff cut across two rounds. Own 10-Q named "
            "merger as an alternative to dissolution and liquidation. Reverse merged "
            "into Histogen, 2020. Emricasan discontinued entirely."
        ),
    },
    "Regado Biosciences Inc": {
        "exit_subtype": "reverse_merger",
        "evidence_note": (
            "Revolixys Phase 3 (REGULATE-PCI) terminated Aug 2014 on safety grounds. "
            "Own statement: 'no further development activities are ongoing nor have "
            "any been planned for the Regado pipeline.' Reverse merged into Tobira "
            "Therapeutics, May 2015."
        ),
    },
    "Axovant Sciences Ltd.": {
        "exit_subtype": "dissolution",
        "evidence_note": (
            "Intepirdine failed Phase 3 (MINDSET, Sept 2017) and a second Phase 3 in "
            "Lewy body dementia (2018); follow-on candidate nelotanserin also failed "
            "Phase 2. Pivoted to gene therapy as Sio Gene Therapies, those programs "
            "also disappointed. Board voted to dissolve and liquidate, Dec 2022, no acquirer."
        ),
    },
    "Ophthotech Corp.": {
        "exit_subtype": "rebrand_pivot",
        "evidence_note": (
            "Fovista failed 2 pivotal Phase 3 trials, Dec 2016 (90% stock drop). "
            "Original program abandoned; rebuilt around a different drug (Zimura) "
            "under a new name, Iveric bio. Original entity and program: failure. "
            "Note: the rebuilt entity later succeeded and was acquired by Astellas "
            "(2023) under a different drug and identity, worth a judgment call on "
            "how to treat this specific case."
        ),
    },
    "CATABASIS PHARMACEUTICALS INC": {
        "exit_subtype": "rebrand_pivot",
        "evidence_note": (
            "Edasalonexent failed Duchenne muscular dystrophy trials twice (2017, "
            "then Phase 3 PolarisDMD Oct 2020, missing primary and secondary "
            "endpoints). Own statement: 'stopping activities related to the "
            "development of edasalonexent.' Rebranded as Astria Therapeutics around "
            "an internally developed candidate."
        ),
    },
    "Versartis, Inc.": {
        "exit_subtype": "reverse_merger",
        "evidence_note": (
            "Somavaratan, the company's only clinical-stage asset, failed Phase 3 "
            "VELOCITY (Sept 2017), missing the primary non-inferiority endpoint, "
            "wiping over 80% off the stock. Own statement: 'does not intend to "
            "further develop somavaratan.' Two-thirds of staff cut. Reverse merged "
            "into Aravive Biologics, 2018."
        ),
    },
}


if __name__ == "__main__":
    df = pd.read_csv(EXIT_PATH, dtype={"cik": str})

    if "exit_subtype" not in df.columns:
        df["exit_subtype"] = None
    if "evidence_note" not in df.columns:
        df["evidence_note"] = None
    if "original_exit_reason" not in df.columns:
        df["original_exit_reason"] = None

    applied = []
    for name, details in CONFIRMED_RECLASSIFICATIONS.items():
        mask = df["company_name"] == name
        if not mask.any():
            print(f"WARNING: {name!r} not found in exit_reasons.csv, exact string mismatch, skipping.")
            continue
        df.loc[mask, "original_exit_reason"] = df.loc[mask, "exit_reason"]
        df.loc[mask, "exit_reason"] = "failure"
        df.loc[mask, "exit_subtype"] = details["exit_subtype"]
        df.loc[mask, "evidence_note"] = details["evidence_note"]
        applied.append(name)
        print(f"Reclassified: {name} -> failure ({details['exit_subtype']})")

    df.to_csv(EXIT_PATH, index=False)

    print(f"\n{len(applied)} of {len(CONFIRMED_RECLASSIFICATIONS)} reclassifications applied.")
    print(df["exit_reason"].value_counts())
