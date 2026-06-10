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
