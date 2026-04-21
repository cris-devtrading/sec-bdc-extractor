"""
extract_bdc_subset.py
=====================
Extracts key financial metrics for a defined BDC universe
from the SEC monthly BDC ZIP dataset.

Usage:
    python extract_bdc_subset.py --zip 2026_03_bdc.zip

NOTE: Each monthly ZIP only contains BDCs that filed that month.
Large BDCs (ARCC, BXSL, FSK) file quarterly — try Q4 or annual ZIPs
if they don't appear in a monthly file.

Author: Cristian Chavez (@cristianchav460)
"""

import zipfile
import os
import argparse
import shutil
import pandas as pd
from datetime import datetime

# ─────────────────────────────────────────────
# BDC UNIVERSE — exact SEC registered names
# Key = ticker, Value = partial name to match
# ─────────────────────────────────────────────
BDC_NAMES = {
    # Large publicly traded BDCs (file quarterly)
    "ARCC":  "ARES CAPITAL",
    "FSK":   "FS KKR",
    "BXSL":  "BLACKSTONE SECURED LENDING",
    "CGBD":  "TCG BDC",
    "CSWC":  "CAPITAL SOUTHWEST",
    "GBDC":  "GOLUB CAPITAL BDC",
    "GLAD":  "GLADSTONE INVESTMENT",
    "NMFC":  "NEW MOUNTAIN FINANCE",
    "OCSL":  "OAKTREE SPECIALTY LENDING",
    "TSLX":  "SIXTH STREET SPECIALTY LENDING",
    "MSDL":  "MORGAN STANLEY DIRECT LENDING",

    # Names confirmed in SEC dataset
    "BCSF":  "BAIN CAPITAL PRIVATE CREDIT",
    "NCDL":  "NUVEEN CHURCHILL BDC",

    # Additional common BDCs found in dataset
    "HTGC":  "HERCULES CAPITAL",
    "MAIN":  "MAIN STREET CAPITAL",
    "ORCC":  "OWL ROCK CAPITAL",
    "OBDC":  "BLUE OWL CAPITAL CORP",
    "OBDC2": "BLUE OWL CREDIT INCOME",
    "OBDCBT":"BLUE OWL TECHNOLOGY",
    "GSBD":  "GOLDMAN SACHS BDC",
    "GSBD2": "GOLDMAN SACHS PRIVATE MIDDLE MARKET",
    "GSCP":  "GOLDMAN SACHS PRIVATE CREDIT",
    "PFLT":  "PENNANTPARK FLOATING",
    "PNNT":  "PENNANTPARK INVESTMENT",
    "SLRC":  "SLR INVESTMENT",
    "TPVG":  "TRIPLEPOINT VENTURE",
    "HRZN":  "HORIZON TECHNOLOGY",
    "RAND":  "RAND CAPITAL",
    "CION":  "CION INVESTMENT",
    "CSWC2": "CAPITAL SOUTHWEST",
    "WHF":   "WHITEHORSE FINANCE",
    "FCRD":  "FIRST EAGLE",
    "SURO":  "SURO CAPITAL",
    "OXSQ":  "OXFORD SQUARE",
    "MSD":   "MSD INVESTMENT",
    "NEXPOINT": "NEXPOINT CAPITAL",
    "OFS":   "OFS CAPITAL",
    "RMRA":  "REMORA CAPITAL",
}

# XBRL tags mapped to target metrics
TAG_MAP = {
    "NetAssetValuePerShare":                                    "nav_per_share",
    "NetAssetValuePerSharePeriodEnd":                           "nav_per_share",
    "InvestmentCompanyNetInvestmentIncomeLossPerShare":          "nii_per_share",
    "NetInvestmentIncomeLossPerShare":                          "nii_per_share",
    "InvestmentCompanyDividendPaidPerShare":                    "dividends_per_share",
    "DividendsCommonStockCash":                                 "dividends_per_share",
    "InvestmentCompanyDistributionToShareholderPerShare":       "dividends_per_share",
    "DebtEquityRatio":                                          "debt_to_equity",
    "RatioOfIndebtednessToNetCapital":                          "debt_to_equity",
    "InvestmentCompanyInvestmentOnNonaccrualFairValue":         "non_accrual_fv",
    "InvestmentsFairValueDisclosure":                           "portfolio_fv",
    "InvestmentOwnedAtFairValue":                               "portfolio_fv",
}


def extract_zip(zip_path, extract_dir):
    print(f"[1/4] Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_dir)
    return extract_dir


def find_tables(base_dir):
    sub_path = None
    num_path = None
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            full = os.path.join(root, f)
            if f in ("sub.txt", "sub.tsv") and sub_path is None:
                sub_path = full
            if f in ("num.txt", "num.tsv") and num_path is None:
                num_path = full
    return sub_path, num_path


def load_tables(extract_dir):
    print("[2/4] Loading SUB and NUM tables...")
    sub_path, num_path = find_tables(extract_dir)

    if not sub_path:
        raise FileNotFoundError("sub.tsv/sub.txt not found in ZIP")
    if not num_path:
        raise FileNotFoundError("num.tsv/num.txt not found in ZIP")

    print(f"    sub -> {sub_path}")
    print(f"    num -> {num_path}")

    sub = pd.read_csv(sub_path, sep="\t", dtype=str, low_memory=False)
    num = pd.read_csv(num_path, sep="\t", dtype=str, low_memory=False)

    print(f"    SUB rows: {len(sub):,}")
    print(f"    NUM rows: {len(num):,}")
    return sub, num


def filter_universe(sub):
    print(f"[3/4] Filtering BDC universe by name...")
    name_col = next((c for c in sub.columns if c.lower() == "name"), None)
    if not name_col:
        print("    WARNING: No name column — returning all rows")
        return sub.copy(), {}

    matched_rows = []
    ticker_map = {}
    not_found = []

    for ticker, partial_name in BDC_NAMES.items():
        mask = sub[name_col].str.upper().str.contains(partial_name, na=False)
        matches = sub[mask]
        if len(matches) > 0:
            matched_rows.append(matches)
            for adsh in matches["adsh"].values:
                ticker_map[adsh] = ticker
            print(f"    ✓ {ticker}: {matches[name_col].iloc[0]}")
        else:
            not_found.append(ticker)

    if not_found:
        print(f"\n    NOT IN THIS ZIP (likely filed in different month):")
        print(f"    {', '.join(not_found)}")

    if matched_rows:
        filtered = pd.concat(matched_rows).drop_duplicates()
    else:
        print("\n    WARNING: No matches — returning all rows")
        filtered = sub.copy()

    print(f"\n    Total matched: {len(filtered)} submissions")
    return filtered, ticker_map


def extract_metrics(sub_filtered, num, ticker_map):
    our_adsh = set(sub_filtered["adsh"].dropna().unique())
    num_f = num[num["adsh"].isin(our_adsh)].copy()

    num_f["metric"] = num_f["tag"].map(TAG_MAP)
    num_f = num_f[num_f["metric"].notna()].copy()
    num_f["value"] = pd.to_numeric(num_f["value"], errors="coerce")

    # Filter per-share metrics by USD unit
    per_share_metrics = ["nav_per_share", "nii_per_share", "dividends_per_share"]
    if "uom" in num_f.columns:
        per_share_mask = (
            num_f["metric"].isin(per_share_metrics) &
            num_f["uom"].str.upper().str.contains("USD", na=False)
        )
        other_mask = ~num_f["metric"].isin(per_share_metrics)
        num_f = pd.concat([num_f[per_share_mask], num_f[other_mask]])

    agg = num_f.groupby(["adsh", "metric"])["value"].mean().reset_index()
    wide = agg.pivot_table(index="adsh", columns="metric",
                           values="value", aggfunc="mean").reset_index()
    wide.columns.name = None

    sub_cols = ["adsh", "cik", "name", "period", "form"]
    result = sub_filtered[sub_cols].merge(wide, on="adsh", how="left")

    # Add ticker
    result["ticker"] = result["adsh"].map(ticker_map)

    # Fix per-share scale (values > 1000 are wrong scale)
    for col in per_share_metrics:
        if col in result.columns:
            result[col] = result[col].apply(
                lambda v: round(v, 4) if pd.notna(v) and abs(v) <= 1000 else None
            )

    # Derived metrics
    if "nii_per_share" in result.columns and "dividends_per_share" in result.columns:
        result["dividend_coverage"] = (
            result["nii_per_share"] / result["dividends_per_share"]
        ).round(4)

    if "non_accrual_fv" in result.columns and "portfolio_fv" in result.columns:
        result["non_accrual_pct"] = (
            result["non_accrual_fv"] / result["portfolio_fv"] * 100
        ).round(2)

    if "period" in result.columns:
        result["period"] = pd.to_datetime(
            result["period"], errors="coerce"
        ).dt.strftime("%Y-%m-%d")

    # Reorder columns nicely
    first_cols = ["ticker", "name", "cik", "period", "form"]
    rest = [c for c in result.columns if c not in first_cols + ["adsh"]]
    result = result[first_cols + rest]

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True,
                        help="Path to SEC BDC ZIP file")
    parser.add_argument("--out", default=None,
                        help="Output CSV filename")
    parser.add_argument("--all", action="store_true",
                        help="Include ALL BDCs in dataset, not just universe")
    args = parser.parse_args()

    if args.out is None:
        base = os.path.splitext(os.path.basename(args.zip))[0]
        args.out = f"bdc_subset_{base}.csv"

    extract_dir = f"_bdc_tmp_{datetime.now().strftime('%H%M%S')}"
    os.makedirs(extract_dir, exist_ok=True)

    try:
        extract_zip(args.zip, extract_dir)
        sub, num = load_tables(extract_dir)

        if args.all:
            sub_filtered = sub.copy()
            ticker_map = {}
        else:
            sub_filtered, ticker_map = filter_universe(sub)

        result = extract_metrics(sub_filtered, num, ticker_map)

        result.to_csv(args.out, index=False)
        print(f"\n[4/4] Done! Saved to: {args.out}")
        print(f"      Rows: {len(result)} | Columns: {list(result.columns)}")

        preview_cols = ["ticker", "name", "period", "nav_per_share",
                        "nii_per_share", "dividends_per_share", "dividend_coverage"]
        preview_cols = [c for c in preview_cols if c in result.columns]
        if not result.empty:
            print("\n── PREVIEW ──────────────────────────────────────────")
            print(result[preview_cols].to_string(index=False))

    finally:
        shutil.rmtree(extract_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
