"""Verify the cleaned financing features."""
import pandas as pd

df = pd.read_csv(
    "/mnt/c/Users/Aman/OneDrive/Desktop/projects/Company-risk-assessment/data/processed/financing_features.csv",
    dtype={"cik": str},
)

print("=== Top 15 by capital raised ===")
top = df.nlargest(15, "total_pre_ipo_capital_m")[
    ["company_name", "total_pre_ipo_capital_m", "num_rounds_detected", "confidence"]
]
for _, r in top.iterrows():
    print(f"  {r['company_name'][:50]:50s}  ${r['total_pre_ipo_capital_m']:>10,.1f}M  rounds={r['num_rounds_detected']}  [{r['confidence']}]")

print()
print("=== Top 15 high-confidence (proceeds phrasing) ===")
hc = df[df["confidence"] == "high"].nlargest(15, "total_pre_ipo_capital_m")[
    ["company_name", "total_pre_ipo_capital_m", "num_rounds_detected"]
]
for _, r in hc.iterrows():
    print(f"  {r['company_name'][:50]:50s}  ${r['total_pre_ipo_capital_m']:>10,.1f}M  rounds={r['num_rounds_detected']}")

print()
print("=== Distribution ===")
print(df["confidence"].value_counts().to_string())
print()
print("=== Capital raised by IPO year (high conf) ===")
import json

# Merge with roster to get ipo_year
roster = pd.read_csv(
    "/mnt/c/Users/Aman/OneDrive/Desktop/projects/Company-risk-assessment/data/processed/final_roster.csv",
    dtype={"cik": str},
)
roster["cik"] = roster["cik"].str.zfill(10)
df["cik"] = df["cik"].str.zfill(10)
merged = df.merge(roster[["cik", "ipo_year", "classification"]], on="cik", how="left")
merged["has_data"] = merged["total_pre_ipo_capital_m"].notna()
print("Companies with data by IPO year:")
for year in sorted(merged["ipo_year"].dropna().unique()):
    yr_data = merged[merged["ipo_year"] == year]
    has = yr_data["has_data"].sum()
    print(f"  {int(year)}: {has}/{len(yr_data)}")

print()
print("Companies with data by classification:")
print(merged.groupby("classification")["has_data"].agg(["sum", "count"]))
