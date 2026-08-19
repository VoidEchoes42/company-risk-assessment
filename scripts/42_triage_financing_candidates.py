"""
Analyze financing_candidates.csv - break down by confidence tier,
sample sentences, and identify which companies have clean vs noisy data.
"""
import pandas as pd

df = pd.read_csv(
    "/mnt/c/Users/Aman/OneDrive/Desktop/projects/Company-risk-assessment/data/processed/financing_candidates.csv",
    dtype={"cik": str},
)

print("=" * 60)
print(f"Total candidate sentences: {len(df)}")
print(f"Companies with hits: {df['cik'].nunique()}")
print()

# Confidence tiers
pp = df[df["has_proceeds_phrasing"]]
med = df[(df["mentions_round"]) & (df["mentions_dollar_amount"])]
low = df[(~df["mentions_round"]) & (df["mentions_dollar_amount"])]
rd = df[(df["mentions_round"]) & (~df["mentions_dollar_amount"])]

print("=== has_proceeds_phrasing (HIGH confidence) ===")
print(f"  Rows: {len(pp)}, Companies: {pp['cik'].nunique()}")
print()
print("=== mentions_round AND mentions_dollar (MEDIUM confidence) ===")
print(f"  Rows: {len(med)}, Companies: {med['cik'].nunique()}")
print()
print("=== mentions_dollar only (LOW confidence, noise) ===")
print(f"  Rows: {len(low)}, Companies: {low['cik'].nunique()}")
print()
print("=== mentions_round only, no dollar (supplemental) ===")
print(f"  Rows: {len(rd)}, Companies: {rd['cik'].nunique()}")
print()

# Companies covered at each tier
tier1_companies = set(pp["cik"].unique()) if len(pp) else set()
tier2_companies = set(med["cik"].unique()) if len(med) else set()
tier3_companies = set(low["cik"].unique()) if len(low) else set()
all_companies = set(df["cik"].unique())

print("=" * 60)
print(f"Companies with ANY candidate: {len(all_companies)}")
print(f"Companies with high-confidence (proceeds phrasing): {len(tier1_companies)}")
print(f"Companies with medium-confidence (round + dollar): {len(tier2_companies)}")
print(f"Companies with low-confidence (dollar only): {len(tier3_companies)}")
print(
    f"Companies with NO high or medium confidence hits: {len(all_companies - tier1_companies - tier2_companies)}"
)
print()

# Sample high-confidence sentences
print("=" * 60)
print("Sample PROCEEDS-PHRASING sentences:")
print("=" * 60)
for _, r in pp.head(15).iterrows():
    print(f"\n[{r['company_name'][:50]}]")
    print(f"  {r['sentence'][:300]}")

# Sample medium confidence
print("\n" + "=" * 60)
print("Sample ROUND+DOLLAR sentences:")
print("=" * 60)
for _, r in med.head(10).iterrows():
    print(f"\n[{r['company_name'][:50]}]")
    print(f"  {r['sentence'][:300]}")

# How many dollars in the dollar-only noise?
print("\n" + "=" * 60)
print("Dollar-only noise: are these financial statement noise?")
print("Sample dollar-only sentences:")
print("=" * 60)
for _, r in low.head(10).iterrows():
    print(f"\n[{r['company_name'][:50]}]")
    print(f"  {r['sentence'][:300]}")

# Save tier summary
summary = pd.DataFrame(
    {
        "cik": list(all_companies),
    }
)
summary["has_high_conf"] = summary["cik"].isin(tier1_companies)
summary["has_med_conf"] = summary["cik"].isin(tier2_companies)
summary["has_any"] = True

# Save high-confidence sentences for review
pp_out = pp[
    ["company_name", "cik", "sentence_rank", "sentence", "mentions_round", "mentions_dollar_amount"]
].copy()
pp_out.to_csv(
    "/mnt/c/Users/Aman/OneDrive/Desktop/projects/Company-risk-assessment/data/processed/financing_high_confidence.csv",
    index=False,
)
print(f"\nSaved {len(pp_out)} high-confidence sentences to financing_high_confidence.csv")

med_out = med[
    ["company_name", "cik", "sentence_rank", "sentence", "mentions_round", "mentions_dollar_amount"]
].copy()
med_out.to_csv(
    "/mnt/c/Users/Aman/OneDrive/Desktop/projects/Company-risk-assessment/data/processed/financing_medium_confidence.csv",
    index=False,
)
print(f"Saved {len(med_out)} medium-confidence sentences to financing_medium_confidence.csv")
