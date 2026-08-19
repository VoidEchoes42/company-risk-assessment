"""Spot-check the top outliers and bottom values."""
import pandas as pd
import json

df = pd.read_csv(
    "/mnt/c/Users/Aman/OneDrive/Desktop/projects/Company-risk-assessment/data/processed/financing_features.csv",
    dtype={"cik": str},
)

print("=== Top 10 by capital raised ===")
for _, r in df.nlargest(10, "total_pre_ipo_capital_m").iterrows():
    details = json.loads(r["round_details"]) if r["round_details"] else []
    print(f"\n  {r['company_name'][:50]:50s}  ${r['total_pre_ipo_capital_m']:>10,.1f}M  [{r['confidence']}]")
    for d in details[:3]:
        if d.get("round"):
            print(f"    - {d['round']}: ${d['amount_m']:.1f}M  '{d['sentence'][:120]}'")
        else:
            print(f"    - proceeds: ${d.get('amount_m','?'):.1f}M  '{d['sentence'][:120]}'")

print("\n\n=== Bottom 5 (with data) ===")
has_data = df[df["total_pre_ipo_capital_m"].notna()]
for _, r in has_data.nsmallest(5, "total_pre_ipo_capital_m").iterrows():
    details = json.loads(r["round_details"]) if r["round_details"] else []
    print(f"\n  {r['company_name'][:50]:50s}  ${r['total_pre_ipo_capital_m']:>10,.1f}M  [{r['confidence']}]")
    for d in details[:3]:
        if d.get("round"):
            print(f"    - {d['round']}: ${d['amount_m']:.1f}M  '{d['sentence'][:120]}'")
