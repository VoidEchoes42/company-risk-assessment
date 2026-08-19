"""
Quick fix for a case-sensitivity miss in script 38: "Zafgen, Inc." was
used as the lookup key, but the actual stored name is all-caps,
"ZAFGEN, INC.", matching the same formatting as several other older
entries (GLYCOMIMETICS INC, NANOANTIBIOTICS, INC.). Adds just this one
missing row rather than rerunning the full batch.

Run with: python scripts/39_add_zafgen_fix.py
"""

from pathlib import Path

import pandas as pd

EXIT_PATH = Path("data/processed/exit_reasons.csv")
TRIAGE_PATH = Path("data/processed/outcome_triage.csv")

CORRECT_NAME = "ZAFGEN, INC."
EVIDENCE_NOTE = (
    "Beloranib caused 2 patient deaths in Phase 3 (bestPWS trial), FDA partial "
    "clinical hold, drug discontinued on safety grounds. Reverse merged, "
    "became Larimar Therapeutics."
)

if __name__ == "__main__":
    exits = pd.read_csv(EXIT_PATH, dtype={"cik": str})
    triage = pd.read_csv(TRIAGE_PATH, dtype={"cik": str})

    if CORRECT_NAME in exits["company_name"].values:
        print(f"{CORRECT_NAME!r} already present, nothing to do.")
    else:
        match = triage[triage["company_name"] == CORRECT_NAME]
        if match.empty:
            print(f"STILL NOT FOUND under {CORRECT_NAME!r} either, "
                  "paste the exact row from your triage file, don't guess again.")
        else:
            cik = match.iloc[0]["cik"]
            new_row = pd.DataFrame([{
                "company_name": CORRECT_NAME, "cik": cik, "exit_reason": "failure",
                "original_exit_reason": "actively_filing",
                "exit_subtype": "reverse_merger", "evidence_note": EVIDENCE_NOTE,
            }])
            exits = pd.concat([exits, new_row], ignore_index=True)
            exits.to_csv(EXIT_PATH, index=False)
            print(f"Added: {CORRECT_NAME} -> failure (reverse_merger)")
            print(exits["exit_reason"].value_counts())
