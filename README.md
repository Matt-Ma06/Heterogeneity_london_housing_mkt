# Heterogeneous Green Premiums and Flat Penalties: Evidence from London
Author: Ma Yuxuan (Matt)\
Email: matt.ma.24@ucl.ac.uk\
Paper Link: Available in this repo as Paper_Draft.pdf

---

## 📌 Project Overview
This repository contains the replication code, data, and paper for my research project. 
This study analyses how micro-level housing characteristics (Energy Performance Certificates (EPC) and property types) structurally reprice under severe macroeconomic shocks (interest rate hikes and energy crises after 2022), using Greater London's housing market.

By constructing a spatial **Payment-to-Income (PTI) Filter** framework and implementing a **Post-Double-Selection LASSO (PDS-LASSO)** machine learning algorithm following Belloni (2014) et al., we uncover how regional credit constraints (Housing Affordability Ratio, HAR) distort micro-level asset valuation and green capitalisation.

---

## 📂 Repository Structure

```text
├── DATA_ANALYSIS  # open this folder for analysis after data cleaning
│  ├── 📜data_analysis.py
│  ├── 📜final_17_london_data.csv
│  ├── 📜final_24_london_data.csv
│  ├── 📜final_london_data.csv
│  ├── 📜lsoa_lad_converter.csv
│  ├── 📜postcode_lookup_2602.csv
│  ├── 📜table1_log_diff.html
│  ├── 📜table2_cs_lasso.html
│  └── 📜table3_cs_standardized.html
├── RAW_DATA_AND_CLEANING  # open this folder when try to clean raw data
│  ├── 📜data_cleaning.py  # main file for data cleaning
│  ├── 📜iod15.csv
│  ├── 📜iod19.csv
│  ├── 📜iod25.csv
│  ├── 📜LA_annual_pay_2024.xlsx
│  ├── 📜la_ukpay_17.xlsx
│  ├── 📜la_ukpay_24.xlsx
│  ├── 📜lsoa11_21_lookup.csv
│  ├── 📜lsoa_har_17.csv
│  ├── 📜lsoa_har_24.csv
│  ├── 📜lsoa_medppd_17.csv
│  ├── 📜lsoa_medppd_24.csv
│  ├── 📜missing_ppd_17.csv
│  ├── 📜missing_ppd_24.csv
│  ├── 📜msoa_income_2018.xls
│  ├── 📜msoa_income_2023.xlsx
│  ├── 📜postcode_lookup_2602.csv
│  ├── 📜pp-2017-part1.csv
│  ├── 📜pp-2017-part2.csv
│  ├── 📜pp-2017.csv
│  ├── 📜pp-2024.csv
│  ├── 📜ptal2015.csv
│  ├── 📜ptal2023.csv
│  ├── 📜rawepc_17.csv
│  └── 📜rawepc_24.csv
├── README.md
```

---
## Data Description
This project utilises a highly granular spatial panel dataset covering Greater London at the **2021 Lower Layer Super Output Area (LSOA)** level (comprising 4,994 LSOAs, with ~4,987 and ~4,986 valid LSOAs retained for 2017 and 2024 respectively, after excluding City of London, which had no recorded transactions). The raw and processed data files are harmonised from multiple UK government and administrative databases.

All datasets are stored in the `RAW_DATA_AND_CLEANING/` directory and are categorised into the following six modules based on their econometric functions:
### 1. House Prices & Transactions (Dependent Variable)
* **Source:** HM Land Registry – *Price Paid Data (PPD)*
* **Files:**
    * `pp-2017.csv`, `pp-2017-part1.csv`, `pp-2017-part2.csv`, `pp-2024.csv`: Raw micro-level housing transaction records for 2017 and 2024. Note that HMLR only allows separate downloads of PPD data 2017 in two parts, as specified by file names. `pp-2017.csv` is created using `pd.concat` on the two separate 2017 files.
    * `lsoa_medppd_17.csv`, `lsoa_medppd_24.csv`: Processed median property prices aggregated to the LSOA level.
    * `missing_ppd_17.csv`, `missing_ppd_24.csv`: Lists of LSOAs excluded from the panel due to zero recorded property transactions in the respective years.

### 2. Incomes & Credit Constraints (HAR)
* **Source:** Office for National Statistics (ONS) – *Income estimates for small areas, England and Wales* & *Earnings and hours worked, place of residence by local authority: ASHE Table 8*
* **Files:**
    * `msoa_income_2018.xls`, `msoa_income_2023.xlsx`: ONS Middle Layer Super Output Area (MSOA) income estimates for FYE 2018 (used as the 2017 baseline) and FYE 2023.
    * `la_ukpay_17.xlsx`, `la_ukpay_24.xlsx`, `LA_annual_pay_2024.xlsx`: Local Authority (borough) level wage growth rates, utilised to project final 2024 incomes ($Y_{24} = Y_{23} \times (1 + \text{growth})$).
    * `lsoa_har_17.csv`, `lsoa_har_24.csv`: The calculated **Housing Affordability Ratio (HAR)** ($HAR = \text{House Price} / \text{Annual Income}$), which acts as the core spatial proxy for credit constraints.

### 3. Energy Performance & Property Attributes
* **Source:** Ministry of Housing, Communities and Local Government (MHCLG) – *Energy Performance of Buildings Data England and Wales*
* **Files:**
    * `rawepc_17.csv`, `rawepc_24.csv`: Raw Energy Performance Certificate (EPC) records.
* **Variables Extracted:** Property type (Flat vs. House) and energy efficiency ratings (EPC A/B/C vs. D-G). *Note: The 2017 baseline physical characteristics are deliberately utilised to rule out reverse causality, capturing initial structural vulnerabilities before the exogenous macroeconomic shocks.*

### 4. Socio-Economic Controls (Indices of Deprivation)
* **Source:** Ministry of Housing, Communities and Local Government (MHCLG) – *English indices of deprivation (2015, 2019, 2025)*
* **Files:**
    * `iod15.csv`, `iod19.csv`, `iod25.csv`: Indices of Multiple Deprivation (IMD) datasets.
* **Variables Extracted:** Domain scores including Crime, Education, Health, Income, and Employment. These serve as the high-dimensional control feature space for the Post-LASSO machine learning algorithm.

### 5. Public Transport Accessibility
* **Source:** Transport for London (TfL) – *TfL GIS Open Data Hub*
* **Files:**
    * `ptal2015.csv`, `ptal2023.csv`: Public Transport Accessibility Level (PTAL) scores.
* **Variables Extracted:** Mean PTAL and intra-LSOA PTAI gaps, strategically included to capture micro-spatial inequalities and neighbourhood gentrification effects masked by macro averages.

### 6. Spatial Lookups & Geography
* **Source:** ONS Open Geography Portal
* **Files:**
    * `postcode_lookup_2602.csv`: Postcode to LSOA mapping directory, essential for accurately geocoding scattered transaction and EPC records into spatial grids.
    * `lsoa11_21_lookup.csv`: Conversion lookup table between 2011 and 2021 LSOA boundaries to ensure strict spatial polygon consistency across the studied timeframe.
 
---

## 🛠 Prerequisites & Dependencies (Data Cleaning Pipeline)

The initial data cleaning, preprocessing, and spatial harmonisation pipeline (`data_cleaning.py`) is built entirely in **Pure Python**. 

It is highly recommended to set up a virtual environment (e.g., using `conda` or `venv`) before running the script. You can install all necessary dependencies via the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```
---

## 🛠 Prerequisites & Dependencies (Data Analysis Pipeline)

The econometric modelling, machine learning feature selection, and statistical output generation are executed entirely in **Pure Python** (`data_analysis.py`). 

It is highly recommended to set up a virtual environment (e.g., using `conda` or `venv`) before running the script. You can install all necessary dependencies via the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Core Python Libraries Utilised:
* **`pandas`** & **`numpy`**: Utilised for extensive data manipulation, handling infinity/missing values, and executing logarithmic transformations prior to modelling.
* **`scikit-learn`**: Specifically utilised for the standardisation of variables (`StandardScaler`) and implementing the Post-Double-Selection LASSO framework using cross-validated penalty models (`LassoCV`, `LogisticRegressionCV`) to isolate high-dimensional controls.
* **`statsmodels`**: Essential for conducting Ordinary Least Squares (OLS) regressions via the formula API, performing Wald tests, and computing clustered robust standard errors (`cov_type='cluster'`).
* **`stargazer`**: Employed to render and export publication-quality, standardised regression tables directly into HTML format (`table1_log_diff.html`, `table2_cs_lasso.html`, `table3_cs_standardized.html`).
* **`os`** & **`warnings`**: Standard Python libraries utilised for directory path configuration and suppressing deprecation warnings during the machine learning iterations.
* **`openpyxl & xlrd`**: Essential engines required by pandas to read unformatted ONS administrative income data provided in both `.xlsx` and `.xls` spreadsheet formats.

---

## 🚀 Replication Steps

To ensure strict reproducibility, the empirical pipeline is separated into two sequential stages. Please execute the scripts in the exact order specified below.

*Note: Ensure your terminal/command prompt is directed to the root directory of this repository and the virtual environment (with all dependencies from `requirements.txt` installed) is activated.*

### Step 1: Data Cleaning & Preprocessing
This script cleans the raw administrative datasets (HM Land Registry, EPC, ONS Income, IMD, PTAL), computes the spatial Payment-to-Income (PTI) proxies (HAR), filters invalid LSOAs, and calculates the baseline logarithmic differences.

```bash
python data_cleaning.py
```
* **Expected Output:** The script will automatically create an analysis directory and export three cleaned, LSOA-level spatial panel datasets ready for econometric modelling:
  * `final_london_data.csv` (Full log-difference panel)
  * `final_17_london_data.csv` (2017 baseline cross-section)
  * `final_24_london_data.csv` (2024 shock cross-section)

### Step 2: Post-LASSO Feature Selection & Econometric Modelling
Once the cleaned datasets are generated, this script executes the Post-Double-Selection LASSO machine learning algorithm (utilising 5-fold cross-validation) to isolate unbiased controls from the high-dimensional feature space. It then runs the ultimate Ordinary Least Squares (OLS) regressions (Cross-Sectional and Log-Difference) with clustered robust standard errors.

```bash
python data_analysis.py
```
* **Expected Output:** The console will print the regression summaries and Wald test results. Furthermore, the script will render and export three publication-quality regression tables directly into your directory:
  * `table1_log_diff.html` (Dynamic growth deficits)
  * `table2_cs_lasso.html` (Cross-Sectional models utilising within-year LASSO controls)
  * `table3_cs_standardized.html` (Cross-Sectional models utilising the standardised full-sample feature set)
 
---
## Empirical Results

### Cross-Sectional Models

**Table 1: Cross-Sectional OLS Regression Models: Standardised Feature Set**

| Feature | (1) 2017 Model | (2) 2024 Model |
| :--- | :--- | :--- |
| **Intercept** | 11.600*** (0.116) | 12.340*** (0.173) |
| **is_abc** | 0.085* (0.050) | 0.306*** (0.053) |
| **is_abc:is_hhar** | 0.130** (0.066) | -0.105 (0.073) |
| **is_flat** | -0.108** (0.045) | -0.159*** (0.043) |
| **is_flat:is_hhar** | 0.258*** (0.056) | 0.227*** (0.069) |
| **is_hhar** | 0.226*** (0.027) | 0.146*** (0.036) |
| **Selected Controls** | | |
| **Crime Index** | -0.009 | -0.065*** |
| **Employment Index** | 1.007*** | 0.396 |
| **Environment Index** | 0.003*** | 0.005*** |
| **Income (Log)** | 0.000*** | 0.000*** |
| **Number of Rooms** | 0.092*** | 0.152*** |
| **Observations** | 4,803 | 4,536 |
| $R^{2}$ | 0.717 | 0.629 |

*Note: \* p<0.1; \*\* p<0.05; \*\*\* p<0.01. Clustered SE by LAD in parentheses.*

---

### Dynamic Model

**Table 2: Post-LASSO Log Difference Model (Full Sample)**

| Variable | Log Difference Model |
| :--- | :--- |
| **Intercept** | 0.080 (0.122) |
| **is_abc** | 0.100*** (0.036) |
| **is_abc:is_hhar** | -0.122*** (0.041) |
| **is_flat** | -0.071*** (0.027) |
| **is_flat:is_hhar** | -0.015 (0.029) |
| **is_hhar** | -0.092*** (0.019) |
| **Control Variables** | Included (20+ features) |
| **Observations** | 4,358 |
| $R^{2}$ | 0.127 |
| **Adjusted $R^{2}$** | 0.123 |
| **F Statistic** | 41.887*** |

*Note: \* p<0.1; \*\* p<0.05; \*\*\* p<0.01. Clustered SE by LAD in parentheses.*

---

## Main Conclusions & Implications

Based on the empirical modeling of London's property market across the 2017 baseline and the 2024 shock period, this study outlines several critical market transitions driven by macroeconomic volatility:

* **Paradigm Shift from Quality to Affordability:** The underlying pricing logic within the housing market has fundamentally shifted. Facing the dual-shock of severe energy cost inflation and rapid interest rate hikes, market constraints have increasingly subordinated property quality to strict affordability thresholds. 
* **Structural Repricing of Energy Efficiency (Green Premiums):** Following energy price surges, there was a pronounced market correction regarding the value of energy efficiency. The cross-sectional premium for energy-efficient (`is_abc`) properties surged from a marginally significant 0.085 in 2017 to a highly significant 0.306 in 2024, correcting widespread undervaluation from the preceding era of cheap credit. 
* **Credit Frictions Exacerbate Inequality:** The benefits of energy efficiency are deeply heterogeneous and gated by credit constraints. In Low-HAR areas, buyers leverage budgetary slack to push green premiums up, realizing future energy savings. Conversely, in High-HAR areas, escalating rates push marginal buyers against their Payment-to-Income (PTI) limits. This financial exclusion results in a relative growth penalty for green assets dynamically, effectively trapping credit-constrained households in depreciating, inefficient homes.
* **The Flat Penalty and Market Down-Laddering:** While flats generally experienced a dynamic pricing discount compared to houses, a structural "price-floor" protected flats in High-HAR (credit-constrained) areas. Because properties higher on the housing ladder breach rigid PTI limits, marginalised first-time buyers are forced to "down-ladder" into flats, generating an inelastic localised demand.
* **Liquidity Shocks Puncture Localised Bubbles:** Although "down-laddering" cushions flat prices in static environments, macroeconomic rate shocks aggressively eroded this dynamic over time. Between 2017 and 2024, the localised flat premium within High-HAR areas compressed from 16.2% to 7.0%. In the cumulative log-difference model, High-HAR flats suffered the worst growth deficit (-16.3%). This demonstrates that macro liquidity withdrawals disproportionately decimate highly leveraged, entry-level assets.
