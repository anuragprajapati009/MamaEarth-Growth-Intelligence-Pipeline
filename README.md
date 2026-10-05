# MamaEarth Growth Intelligence Pipeline

A business analytics pipeline for analyzing Mamaearth-style customer, product, and order data across SQL, Python/Pandas, and GenAI-powered business narration.

## Project Overview

This project is divided into three layers:

1. **SQL** — database schema, raw data loading, and business reports.
2. **Python/Pandas** — data cleaning, exploratory data analysis, hypothesis testing, segmentation, correlation analysis, outlier handling, time-series analysis, and visualizations.
3. **GenAI Narrator** — converts verified analytical findings into a three-part Situation–Complication–Resolution (SCR) business narrative using Gemini, with a fully offline fallback.

The raw CSV files are kept unchanged. Data cleaning is performed in Python.

---

## Project Structure

```text
MamaEarth-Growth-Intelligence-Pipeline/
│
├── README.md
│
├── sql/
│   ├── schema.sql
│   ├── seed_data.sql
│   └── reports.sql
│
├── data/
│   ├── customers.csv
│   ├── products.csv
│   └── orders.csv
│
├── analysis/
│   ├── clean_and_eda.py
│   └── visualize.py
│
├── visualizations/
│   ├── return_rate_by_payment.png
│   └── monthly_revenue_trend.png
│
└── narrator/
    ├── findings.json
    ├── generate_narrative.py
    └── sample_output.txt
```

---

## 1. SQL Layer

### Step 1 — Create the database and tables

Open `sql/schema.sql` in MySQL Workbench and run it.

It creates:

- `customers`
- `products`
- `orders`

### Step 2 — Load the raw CSV data

Run `sql/seed_data.sql` after the schema has been created.

The script loads:

- `data/customers.csv`
- `data/products.csv`
- `data/orders.csv`

Blank `discount_pct` and `rating` values are loaded as SQL `NULL`.

> **MySQL Workbench note:** `LOAD DATA LOCAL INFILE` depends on the local-file settings of the MySQL client. If your Workbench setup does not resolve the project-relative paths, enable `LOCAL INFILE` and adjust the local file paths for your machine. Do not commit personal absolute Windows paths to GitHub.

### Step 3 — Run the business reports

Run `sql/reports.sql`.

It contains nine business reports covering:

- overall order and revenue summary
- returned vs non-returned orders
- top customer
- city-wise return analysis
- top 5 customers
- category-wise revenue
- customer name filtering
- acquisition sources
- loyalty-tier segmentation

---

## 2. Python / Pandas Analysis

The raw CSV files are intentionally not manually edited.

Run:

```bash
python analysis/clean_and_eda.py
```

The script performs the verified Part 2 workflow:

- loads the three raw CSV files
- standardizes payment-method values
- identifies and removes duplicate orders
- fills missing discount values with `0`
- fills missing ratings with the median
- merges customer and product information
- calculates order value
- flags quantity outliers using the IQR method without deleting them
- analyzes return rates
- performs payment-method and city-tier segmentation
- calculates the correlation matrix
- compares monthly revenue with and without flagged quantity outliers
- identifies the true revenue peak
- automatically generates `narrator/findings.json`

The findings JSON is generated from the analysis results rather than being manually typed.

---

## 3. Visualizations

Run:

```bash
python analysis/visualize.py
```

This generates:

- `visualizations/return_rate_by_payment.png`
- `visualizations/monthly_revenue_trend.png`

The first visualization compares return rates by payment method.

The second visualization shows the outlier-corrected monthly revenue trend.

---

## 4. GenAI-Powered Insight Narrator

The narrator reads the verified:

```text
narrator/findings.json
```

and generates an SCR narrative with exactly:

- Situation
- Complication
- Resolution

### Gemini API

The project supports a free Gemini API key through the `GEMINI_API_KEY` environment variable.

Example:

```bash
set GEMINI_API_KEY=YOUR_KEY
python narrator/generate_narrative.py
```

On macOS/Linux:

```bash
export GEMINI_API_KEY="YOUR_KEY"
python narrator/generate_narrative.py
```

**Never commit the API key to the repository.**

### Offline fallback

If `GEMINI_API_KEY` is not available or the Gemini request fails, the script automatically uses a deterministic offline fallback.

The fallback requires:

- no API key
- no network access
- no paid service

The script also checks the required verified figures in the generated narrative.

The final narrative is saved to:

```text
narrator/sample_output.txt
```

---

## Key Verified Findings

The verified analysis produced the following figures:

- Cleaned total revenue: **₹97,358.30**
- Raw total revenue: **₹99,860.20**
- Duplicate reconciliation delta: **₹2,501.90**
- COD return rate: **44.4%**
- Highest-risk segment: **COD + Tier-2**
- Highest-risk return rate: **54.5%**
- True revenue peak: **March 2026**
- March 2026 revenue: **₹20,318.90**

January's apparent revenue peak was affected by the identified quantity outliers; the outlier-corrected series shows March 2026 as the true peak.

---

## Requirements

Install the Python dependencies with:

```bash
pip install pandas matplotlib google-genai
```

The SQL layer requires:

- MySQL
- MySQL Workbench (or another MySQL client)

---

## Important Data Rules

- Raw CSV files are kept unchanged.
- Cleaning is performed in Python, not by manually editing the CSVs.
- Outliers are flagged rather than deleted.
- Verified findings are generated from the analysis results.
- API keys are stored outside the code.
- SQL and Python layers are intentionally kept separate.
