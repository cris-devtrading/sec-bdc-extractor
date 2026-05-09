# SEC BDC Extractor — Business Development Company Data Pipeline

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Language](https://img.shields.io/badge/Built%20with-Python-blue?logo=python)
![Data](https://img.shields.io/badge/Data-SEC%20EDGAR%20API-red)
![Output](https://img.shields.io/badge/Output-CSV-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> Python script that extracts and analyzes **BDC (Business Development Company)** financial data from the SEC EDGAR monthly dataset. Outputs a clean, analysis-ready CSV with key metrics: NAV, NII, dividends, and leverage ratios.

---

## 🧠 What are BDCs?

Business Development Companies (BDCs) are SEC-regulated investment vehicles that lend to and invest in small-to-mid size US companies. They must distribute 90%+ of taxable income as dividends, making them high-yield instruments tracked by income investors and quant funds.

Key metrics:
- **NAV** — Net Asset Value per share (intrinsic value)
- **NII** — Net Investment Income (dividend coverage)
- **Leverage ratio** — debt/equity, critical for risk assessment
- **Dividends** — primary return driver for BDC investors

---

## ✨ Features

| Feature | Detail |
|---|---|
| **BDC subset extraction** | Filters BDCs from the full SEC EDGAR monthly dataset |
| **NAV per share** | Net Asset Value from XBRL filings |
| **NII** | Net Investment Income per share |
| **Dividend data** | Declared dividends per period |
| **Leverage metrics** | Debt-to-equity and asset coverage ratios |
| **Clean CSV output** | Analysis-ready, no manual cleaning required |
| **SEC EDGAR source** | Free, official, no API key required |

---

## 🏗️ Architecture

```
SEC EDGAR Monthly Dataset (bulk download)
        │
        ▼
  extract_bdc_subset.py
  ┌──────────────────────────────────────┐
  │  Load SEC monthly submission data    │
  │  Filter BDC entity type              │
  │  Extract target XBRL financial tags  │
  │    - NetAssetValuePerShare           │
  │    - InvestmentIncomeNet             │
  │    - DividendsDeclared               │
  │    - DebtToEquityRatio               │
  │  Normalize across periods            │
  │  Output clean CSV                    │
  └──────────────────────────────────────┘
        │
        ▼
  bdc_data.csv — ready for analysis
```

---

## 📊 Output Columns

| Column | Description |
|---|---|
| `ticker` | BDC ticker symbol |
| `company_name` | Full legal name |
| `period` | Filing period (quarterly) |
| `nav_per_share` | Net Asset Value per share (USD) |
| `nii_per_share` | Net Investment Income per share |
| `dividend_declared` | Dividends declared per period |
| `leverage_ratio` | Debt-to-equity ratio |
| `total_assets` | Total assets (USD) |
| `total_debt` | Total borrowings |

---

## 🚀 Quick Start

**Requirements:**
- Python 3.10+
- No API key required

```bash
git clone https://github.com/cris-devtrading/sec-bdc-extractor
cd sec-bdc-extractor
pip install pandas requests
python extract_bdc_subset.py
```

Output: `bdc_data.csv` with clean BDC metrics ready for screening or modeling.

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **pandas** — data processing and CSV output
- **requests** — SEC EDGAR bulk data download
- **SEC EDGAR API** — `data.sec.gov`

---

## 💡 Use Cases

- **Income investors** screening BDCs by NAV discount, NII coverage, and dividend sustainability
- **Quant developers** building BDC factor models or yield strategies
- **Fintech startups** needing free, clean BDC data without Bloomberg/FactSet
- **Researchers** analyzing leverage and income trends across the BDC sector

---

## 👤 About the Author

Built by **Cristian Chaves** — Algorithmic Trading & Fintech Developer.

Specializing in automated trading systems, broker API integrations, options analytics, and real-time financial dashboards for retail traders, prop firms, and fintech startups.

🔗 [AlgoTrader Pro — IBKR Automated Bot](https://github.com/cris-devtrading/algotrader-pro)  
🔗 [OptionsGuru — Live Options Analyzer](https://option-guru.vercel.app)  
🔗 [CCL Radar v2 — Argentine ADR/CEDEAR Monitor](https://ccl-radar.vercel.app)  
📧 Open for freelance projects — [Upwork](https://www.upwork.com/freelancers/cristianchaves) | [Fiverr](https://www.fiverr.com/cristianchaves)
📧 Contacto: quantedgelatam@gmail.com
🌐 GitHub: github.com/cris-devtrading
---

## 📄 License

MIT — free to use, modify, and distribute with attribution.
