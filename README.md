# BDC Subset Extractor — SEC Monthly Data
**Author:** Cristian Chavez | @cristianchav460  
**Version:** 1.0

---

## What this script does

Reads the SEC's monthly BDC ZIP dataset and produces a clean CSV with key financial metrics for a defined universe of Business Development Companies (BDCs).

**Output columns:**
| Column | Description |
|---|---|
| cik | SEC Central Index Key |
| ticker | Stock ticker |
| name | Company name |
| period | Period end date (YYYY-MM-DD) |
| nav_per_share | Net Asset Value per share |
| nii_per_share | Net Investment Income per share |
| dividends_per_share | Distributions paid per share |
| dividend_coverage | NII / Dividends (>1.0 = covered) |
| debt_to_equity | Leverage ratio |
| non_accrual_pct | Non-accruals as % of portfolio FV |

---

## Requirements

Python 3.8+ and pandas:

```bash
pip install pandas
```

---

## How to run

**Step 1:** Download the monthly ZIP from the SEC:
```
https://www.sec.gov/data-research/sec-markets-data/bdc-data-sets
```
Example file: `2026_03_bdc.zip`

**Step 2:** Run the script:
```bash
python extract_bdc_subset.py --zip 2026_03_bdc.zip
```

**Optional — custom output filename:**
```bash
python extract_bdc_subset.py --zip 2026_03_bdc.zip --out my_bdc_march.csv
```

**Optional — override BDC universe:**
```bash
python extract_bdc_subset.py --zip 2026_03_bdc.zip --tickers ARCC BXSL FSK NMFC
```

---

## How to update monthly

1. Go to: https://www.sec.gov/data-research/sec-markets-data/bdc-data-sets
2. Download the latest ZIP (e.g. `2026_04_bdc.zip`)
3. Run: `python extract_bdc_subset.py --zip 2026_04_bdc.zip`
4. Import the new CSV to Google Sheets

---

## BDC Universe (default)

ARCC, FSK, BCSF, BXSL, CGBD, CSWC, GBDC, GLAD, MSDL, NCDL, NMFC, OCSL, TSLX

To change the universe, edit the `BDC_TICKERS` list at the top of the script.

---

## SEC Field Mapping

| Our Metric | SEC XBRL Tag (NUM table) |
|---|---|
| nav_per_share | NetAssetValuePerShare |
| nii_per_share | InvestmentCompanyNetInvestmentIncomeLossPerShare |
| dividends_per_share | InvestmentCompanyDividendPaidPerShare |
| debt_to_equity | DebtEquityRatio |
| non_accrual_fv | InvestmentCompanyInvestmentOnNonaccrualFairValue |

---

## Troubleshooting

**"No ticker column found"** → The script will include all BDCs in the dataset. Filter manually by CIK if needed.

**Empty output** → Some BDCs may not file XBRL for all metrics. Check the SEC EDGAR page for the specific company.

**Missing metrics** → Not all BDCs report every metric in structured XBRL format. The script documents which fields are absent.
