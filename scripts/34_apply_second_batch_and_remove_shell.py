"""
Step 4.3f: Second batch of confirmed reclassifications from individual
research (ProNAi, Spring Bank, Eleven Biotherapeutics, Carbylan), plus
removal of a genuine roster scope violation found along the way:
Dynamic Nutra Enterprises Holdings traces to a chronically-repurposed
penny-stock shell (il2m International Corp, a former music/social-media
company with $17 in trailing annual revenue) that was never a real
operating biotech, the same pattern as the AbbVie/Baxalta/Retrophin
exclusions from the earlier roster-integrity work, just one that slipped
through those checks at the time.

Run with: python scripts/34_apply_second_batch_and_remove_shell.py

Input:  data/processed/exit_reasons.csv
        data/processed/final_roster.csv
Output: both overwritten
"""

from pathlib import Path

import pandas as pd

EXIT_PATH = Path("data/processed/exit_reasons.csv")
ROSTER_PATH = Path("data/processed/final_roster.csv")

SECOND_BATCH = {
    "ProNAi Therapeutics Inc": {
        "exit_subtype": "rebrand_pivot",
        "evidence_note": (
            "PNT2258 showed only modest efficacy in Phase 2 (Wolverine trial, "
            "2016). Company explicitly dropped both the drug and the entire "
            "underlying DNAi platform, closed its research facility. Stock lost "
            "70% overnight; securities fraud suit followed. Rebranded Sierra "
            "Oncology (2017) around entirely licensed-in assets."
        ),
    },
    "Spring Bank Pharmaceuticals, Inc.": {
        "exit_subtype": "reverse_merger",
        "evidence_note": (
            "A patient death occurred in the Phase 2b trial of lead drug "
            "inarigivir, forcing discontinuation on safety grounds. 1:4 reverse "
            "stock split immediately preceded a reverse merger with F-star "
            "Therapeutics (private), which took 61.2% ownership."
        ),
    },
    "Eleven Biotherapeutics, Inc.": {
        "exit_subtype": "reverse_merger",
        "evidence_note": (
            "Original dry-eye-disease drug failed multiple Phase 3 trials "
            "(called a 'zombie biotech... on life support' by Fierce Biotech, "
            "2016). Merged with Viventia Bio, rebranded Sesen Bio around a "
            "bladder cancer drug, which the FDA then rejected. Reverse merged "
            "into Carisma Therapeutics, 2022. BioPharma Dive: 'the deal marks "
            "the end of the line.'"
        ),
    },
    "Carbylan Therapeutics, Inc.": {
        "exit_subtype": "reverse_merger",
        "evidence_note": (
            "1-for-14 reverse stock split immediately preceded a reverse merger "
            "with KalVista Pharmaceuticals (private, UK), full rename, followed "
            "by a securities law investigation. No single explicit trial-failure "
            "citation found, medium-high confidence based on the structural "
            "pattern alone."
        ),
    },
}

SHELL_COMPANY_NAME = "Dynamic Nutra Enterprises Holdings, Inc."
SHELL_REASON = (
    "roster scope violation, not an outcome misclassification: traces to "
    "il2m International Corp, a chronically-repurposed penny-stock shell "
    "(former music/social-media platform, $17 trailing annual revenue), "
    "never a real operating biotech, confirmed manually"
)


if __name__ == "__main__":
    exits = pd.read_csv(EXIT_PATH, dtype={"cik": str})
    if "exit_subtype" not in exits.columns:
        exits["exit_subtype"] = None
    if "evidence_note" not in exits.columns:
        exits["evidence_note"] = None
    if "original_exit_reason" not in exits.columns:
        exits["original_exit_reason"] = None

    applied = []
    for name, details in SECOND_BATCH.items():
        mask = exits["company_name"] == name
        if not mask.any():
            print(f"WARNING: {name!r} not found in exit_reasons.csv, skipping.")
            continue
        exits.loc[mask, "original_exit_reason"] = exits.loc[mask, "exit_reason"]
        exits.loc[mask, "exit_reason"] = "failure"
        exits.loc[mask, "exit_subtype"] = details["exit_subtype"]
        exits.loc[mask, "evidence_note"] = details["evidence_note"]
        applied.append(name)
        print(f"Reclassified: {name} -> failure ({details['exit_subtype']})")

    exits.to_csv(EXIT_PATH, index=False)
    print(f"\n{len(applied)} of {len(SECOND_BATCH)} second-batch reclassifications applied.")
    print(exits["exit_reason"].value_counts())

    # Remove the shell company from the roster and from exit_reasons.
    roster = pd.read_csv(ROSTER_PATH, dtype={"cik": str})
    shell_mask = roster["company_name"] == SHELL_COMPANY_NAME
    if shell_mask.any():
        roster = roster[~shell_mask]
        roster.to_csv(ROSTER_PATH, index=False)
        exits = exits[exits["company_name"] != SHELL_COMPANY_NAME]
        exits.to_csv(EXIT_PATH, index=False)
        print(f"\nRemoved {SHELL_COMPANY_NAME!r} from both files: {SHELL_REASON}")
    else:
        print(f"\nWARNING: {SHELL_COMPANY_NAME!r} not found in roster, nothing removed.")

    print(f"\n{len(roster)} companies remain in {ROSTER_PATH}.")
