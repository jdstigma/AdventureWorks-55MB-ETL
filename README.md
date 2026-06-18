# AdventureWorks 55MB ETL

A full ETL demonstration project built on the Microsoft AdventureWorks data warehouse — from raw SQLite database through Python-driven data profiling, regression analysis, and Power BI reporting.

---

## Prerequisites

| Tool | Purpose |
|------|---------|
| [Git LFS](https://git-lfs.github.com/) | Required to pull `AdventureWorks.db` and the `.pbix` file |
| Python 3.10+ | Running `db_doc.py`, `adventureworks_pbi.py`, and notebook scripts |
| `pandas`, `scikit-learn`, `matplotlib`, `seaborn` | Notebook dependencies |
| [DB Browser for SQLite](https://sqlitebrowser.org/) or VS Code SQLite extension | Browsing the database |
| Power BI Desktop | Opening `Adventure Works 55MB ETL.pbix` |

---

## Getting Started

### 1 — Clone with LFS

The database file is stored in Git LFS. You must have Git LFS installed before cloning, otherwise `AdventureWorks.db` will be a pointer file.

```bash
git lfs install
git clone https://github.com/jdstigma/AdventureWorks-55MB-ETL.git
cd AdventureWorks-55MB-ETL
git lfs pull
```

### 2 — Verify the database

```bash
sqlite3 AdventureWorks.db ".tables"
```

You should see all 20 tables listed. If the file is only a few hundred bytes, Git LFS did not pull correctly — re-run `git lfs pull`.

### 3 — Open in a Codespace (optional)

The repo ships a `.devcontainer` that auto-pulls LFS files and installs the SQLite Viewer extension. Open the repo in GitHub Codespaces and the database will be ready immediately after the container builds.

---

## Database Overview

**File:** `AdventureWorks.db` — 51.82 MB SQLite
**Tables:** 20 · **Columns:** 274 · **Rows:** 225,344 · **Foreign Keys:** 30

### Fact Tables

| Table | Rows | Description |
|-------|-----:|-------------|
| `FactInternetSales` | 60,398 | Direct-to-consumer internet sales with full order detail |
| `FactInternetSalesReason` | 64,515 | Bridge table linking internet sales orders to sales reasons |
| `FactResellerSales` | 58,820 | Sales through reseller/distributor channel |
| `FactCurrencyRate` | 14,264 | Daily exchange rates against USD |
| `FactSurveyResponse` | 2,727 | Customer survey responses |

### Dimension Tables

| Table | Rows | Description |
|-------|-----:|-------------|
| `DimCustomer` | 18,484 | Customer demographics, geography key, purchase history |
| `DimDate` | 3,652 | Full calendar and fiscal date hierarchy |
| `DimProduct` | 606 | Product master with cost, pricing, and classification |
| `DimProductSubcategory` | 37 | Product subcategory rollup |
| `DimProductCategory` | 4 | Top-level product categories (Bikes, Components, Clothing, Accessories) |
| `DimReseller` | 701 | Reseller profile — type, size, territory, order history |
| `DimEmployee` | 296 | Employee and sales rep master |
| `DimGeography` | 655 | City / state / country / postal code |
| `DimSalesTerritory` | 11 | Sales territory region, country, and group |
| `DimPromotion` | 16 | Promotion type, discount, and date range |
| `DimSalesReason` | 10 | Reason categories (Price, Quality, Manufacturer, etc.) |
| `DimCurrency` | 105 | ISO currency codes and names |
| `DimOrganization` | 14 | Internal org hierarchy with currency assignments |
| `DimDepartmentGroup` | 7 | Department group hierarchy |

### Analysis Table

| Table | Rows | Description |
|-------|-----:|-------------|
| `RegressionResults` | 22 | Persisted output from the regression pipeline |

Full schema documentation (columns, types, indexes, foreign keys) is in [`AdventureWorks_doc.txt`](AdventureWorks_doc.txt) and is regenerated automatically on every push to `main`.

---

## File Reference

```
AdventureWorks-55MB-ETL/
├── AdventureWorks.db                   SQLite database (Git LFS — 51.82 MB)
├── AdventureWorks_doc.txt              Auto-generated full schema documentation
├── db_doc.py                           Schema documentation generator script
├── adventureworks_pbi.py               Builds flat DataFrames for Power BI ingestion
├── dot-documentation.html              ERD-style relationship documentation (dot/Graphviz)
├── Adventure Works 55MB ETL.pbix       Power BI report file (Git LFS)
├── Adventure Works Report.pdf          Exported PDF of the Power BI report
├── notebooks/
│   ├── regression_analysis.ipynb       OLS + Random Forest regression notebook
│   └── regression_pipeline.py          Standalone Python pipeline for the same analysis
├── outputs/
│   └── regression_results_*.csv        Timestamped regression output CSVs
├── png charts/
│   ├── correlation_heatmap.png         Feature correlation matrix
│   ├── confusion_matrix_bucketed.png   Bucketed quantity confusion matrix
│   ├── confusion_matrix_orderquantity.png
│   ├── regression_OrderQuantity.png    OLS fit — OrderQuantity target
│   ├── regression_SalesAmount.png      OLS fit — SalesAmount target
│   ├── residuals_RandomForest_OrderQuantity.png
│   ├── residuals_RandomForest_SalesAmount.png
│   ├── rf_importance_OrderQuantity.png Random Forest feature importance
│   └── rf_importance_SalesAmount.png
├── png_charts.zip                      All charts bundled for download
├── .devcontainer/devcontainer.json     GitHub Codespaces config (Ubuntu + Git LFS + SQLite)
└── .github/workflows/
    ├── db_doc.yml                      CI: regenerates AdventureWorks_doc.txt on push
    └── open_db.yml                     CI: verifies LFS pull and SQLite integrity
```

---

## Running the Scripts

### Generate schema documentation

```bash
python db_doc.py AdventureWorks.db
```

Prints a full schema report to the terminal and writes it to `AdventureWorks_doc.txt`. The report includes row counts, column definitions, indexes, foreign keys, and an integrity check.

### Build Power BI DataFrames

```bash
python adventureworks_pbi.py
```

Opens `AdventureWorks.db` (update `DB_PATH` at the top of the file to match your local path), then builds the following pandas DataFrames:

| DataFrame | Source joins |
|-----------|-------------|
| `Sales_Internet` | `FactInternetSales` joined to Product, Customer, Geography, Territory, Date, Promotion |
| `Sales_Reseller` | `FactResellerSales` joined to Product, Reseller, Employee, Geography, Territory, Date, Promotion |
| `Dim_Product` | `DimProduct` + Subcategory + Category |
| `Dim_Customer` | `DimCustomer` + Geography |
| `Dim_Date` | `DimDate` (calendar and fiscal fields) |
| `Dim_Territory` | `DimSalesTerritory` |
| `Dim_Promotion` | `DimPromotion` |
| `Dim_Currency` | `DimCurrency` |
| `Dim_SalesReason` | `DimSalesReason` |
| `Bridge_SalesReason` | `FactInternetSalesReason` |

Add your own export logic (e.g. `to_csv`, `to_parquet`) after the DataFrames are built, or feed them directly into a Jupyter notebook.

---

## Regression Analysis

Open `notebooks/regression_analysis.ipynb` in JupyterLab or VS Code. The notebook:

1. Loads and joins the sales data from `AdventureWorks.db`
2. Encodes categorical features and builds a correlation heatmap
3. Trains OLS regression and Random Forest models against two targets: `SalesAmount` and `OrderQuantity`
4. Outputs residual plots, feature importance charts, and confusion matrices to `png charts/`
5. Writes timestamped results to `outputs/regression_results_<timestamp>.csv`

To run the pipeline non-interactively:

```bash
python notebooks/regression_pipeline.py
```

---

## Power BI Report

Open `Adventure Works 55MB ETL.pbix` in Power BI Desktop. The report connects to the flat tables produced by `adventureworks_pbi.py`. If the data source path is broken, go to **Transform Data → Data Source Settings** and update the file path to your local `AdventureWorks.db`.

A static export of the report is available as [`Adventure Works Report.pdf`](Adventure%20Works%20Report.pdf).

---

## GitHub Actions

| Workflow | Trigger | Action |
|----------|---------|--------|
| `db_doc.yml` | Push to `main` | Runs `db_doc.py` against every `.db` file and commits updated `*_doc.txt` files back to the branch |
| `open_db.yml` | Push to `main` | Pulls all LFS files, lists LFS-tracked assets, verifies each `.db` file opens cleanly in SQLite |
