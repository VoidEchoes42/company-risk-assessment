"""Spot-check publication features."""
import pandas as pd

df = pd.read_csv(
    "/mnt/c/Users/Aman/OneDrive/Desktop/projects/Company-risk-assessment/data/processed/publication_features.csv",
    dtype={"cik": str},
)

print("=== Full distribution ===")
print(f"Total: {len(df)}")
print(f"With publications: {(df['pubmed_pre_ipo_count'] > 0).sum()}")
print(f"Zero: {(df['pubmed_pre_ipo_count'] == 0).sum()}")
print(f"Query methods: {df['pubmed_query_method'].value_counts().to_dict()}")
print()
print("=== Top 20 ===")
for _, r in df.nlargest(20, "pubmed_pre_ipo_count").iterrows():
    print(f"  {r['company_name'][:45]:45s}  {r['pubmed_pre_ipo_count']:>5}  [{r['pubmed_query_method'][:15]}]")
print()
print("=== Bottom 20 (nonzero) ===")
has = df[df['pubmed_pre_ipo_count'] > 0]
for _, r in has.nsmallest(20, 'pubmed_pre_ipo_count').iterrows():
    print(f"  {r['company_name'][:45]:45s}  {r['pubmed_pre_ipo_count']:>5}")
print()
print("=== Zero publications (sample) ===")
zero = df[df['pubmed_pre_ipo_count'] == 0]
for _, r in zero.head(15).iterrows():
    print(f"  {r['company_name'][:50]}")
print(f"  ... and {len(zero) - 15} more")
