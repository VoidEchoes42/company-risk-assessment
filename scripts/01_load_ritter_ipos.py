"""
Step 4.1a: Load Jay Ritter's IPO dataset and filter to the 2012-2019 window.

CORRECTION from the first version of this script: I assumed this file had
a SIC code column. It does not. The file at IPO-age.xlsx (what you already
downloaded) is Ritter's master company-level spreadsheet, columns are
offer date, IPO name, Ticker, CUSIP, ADR, VC, Dual, Post-issue shares,
Internet, CRSP Perm, Founding, Rollup. Founding date and IPO date, yes.
Industry classification, no. SIC lives only in Ritter's separate PDF
reports as aggregate statistics, not as a joinable per-company column.

So this script now does less than before: it filters by date only. SIC
based filtering moves to 02_lookup_sic_edgar.py, which fetches each
company's real SIC code straight from SEC EDGAR using the ticker column
already sitting in this file.

MANUAL STEP FIRST (this script does not download anything for you):
  1. Go to https://site.warrington.ufl.edu/ritter/ipo-data/
  2. Download IPO-age.xlsx (linked under several list names on that page,
     they all point to the same file).
  3. Save it as: data/raw/ritter_ipo_age.xlsx

Run with: python scripts/01_load_ritter_ipos.py

Output: data/processed/roster_by_date.csv
"""

from pathlib import Path

import pandas as pd

RAW_PATH = Path("data/raw/ritter_ipo_age.xlsx")
OUT_PATH = Path("data/processed/roster_by_date.csv")

IPO_YEAR_MIN = 2012
IPO_YEAR_MAX = 2019

# Confirmed from your actual printout. If a future re-download ever
# renames these, rerunning will show you immediately, the column list
# prints before anything else happens.
DATE_COL = "offer date"
NAME_COL = "IPO name"
TICKER_COL = "Ticker"
FOUNDING_COL = "Founding"


def load_raw(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Download it manually first from "
            "https://site.warrington.ufl.edu/ritter/ipo-data/"
        )
    df = pd.read_excel(path)
    print("Columns found in your file:")
    print(list(df.columns))
    print(f"\n{len(df)} total rows loaded.\n")
    return df


def parse_offer_date(series: pd.Series) -> pd.Series:
    print(f"offer date column dtype: {series.dtype}")
    print(f"sample raw values: {series.head(3).tolist()}")

    if pd.api.types.is_datetime64_any_dtype(series):
        return series

    # Values are YYYYMMDD (e.g. 19750130), not a Unix timestamp. Passing
    # raw numbers straight to pd.to_datetime does NOT raise or coerce to
    # NaT here, it silently reads them as nanoseconds since 1970-01-01,
    # which is exactly why the first version of this returned 0 rows for
    # 2012-2019, every date came out as 1970. Forcing the format below
    # fixes that. pd.to_numeric first protects against any stray
    # non-numeric junk in the column.
    numeric = pd.to_numeric(series, errors="coerce")
    as_str = numeric.astype("Int64").astype(str)
    return pd.to_datetime(as_str, format="%Y%m%d", errors="coerce")


def filter_by_year(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df[DATE_COL] = parse_offer_date(df[DATE_COL])
    df["ipo_year"] = df[DATE_COL].dt.year
    print(
        f"Parsed year range: {df['ipo_year'].min():.0f} to "
        f"{df['ipo_year'].max():.0f}, {df['ipo_year'].isna().sum()} rows "
        "unparseable. If that range looks wrong (e.g. stuck at 1970), "
        "something about this file's date format differs from what this "
        "script expects, stop and flag it rather than trusting the output."
    )

    mask = df["ipo_year"].between(IPO_YEAR_MIN, IPO_YEAR_MAX)
    keep_cols = [NAME_COL, DATE_COL, TICKER_COL, FOUNDING_COL, "ipo_year"]
    result = df.loc[mask, keep_cols].copy()
    result = result.rename(
        columns={
            NAME_COL: "company_name",
            DATE_COL: "ipo_date",
            TICKER_COL: "ticker",
            FOUNDING_COL: "founding_year",
        }
    )
    return result.sort_values("ipo_date").reset_index(drop=True)


if __name__ == "__main__":
    raw = load_raw(RAW_PATH)
    roster = filter_by_year(raw)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    roster.to_csv(OUT_PATH, index=False)
    print(f"{len(roster)} companies IPO'd 2012-2019, written to {OUT_PATH}")
    print("This is every sector, not just life science, that filter "
          "happens next in 02_lookup_sic_edgar.py.")
