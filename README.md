# Heterogeneous Green Premiums and Flat Penalties: Evidence from London

**Author:** Yuxuan (Matt) Ma, University College London · matt.ma.24@ucl.ac.uk
**Paper:** [`Here`](./essay.pdf)

---

## Overview

This repository contains the data, code and paper for an independent research project on the London housing market between 2017 and 2024, a period that includes the 2022 energy price surge and the rise in Bank Rate from 0.25% to 5.25%.

The project asks how the price associations of two property characteristics, energy efficiency (EPC bands A–C) and property type (flat vs. house), changed over this period, and whether these changes differ between areas with high and low Housing Affordability Ratios (HAR), used here as a proxy for credit constraints.

Controls are selected from a high-dimensional set of energy, deprivation and transport-access features using post-double-selection LASSO (Belloni, Chernozhukov and Hansen, 2014), followed by OLS. The estimates are **conditional associations, not causal effects**; see [Limitations](#limitations).

---

## Repository Structure

```text
├── paper/
│   └── Green_Premiums_Flat_Penalties_London.pdf
├── RAW_DATA_AND_CLEANING/          # Stage 1: raw data and cleaning
│   ├── data_cleaning.py
│   ├── iod15.csv, iod19.csv, iod25.csv
│   ├── LA_annual_pay_2024.xlsx, la_ukpay_17.xlsx, la_ukpay_24.xlsx
│   ├── lsoa11_21_lookup.csv
│   ├── lsoa_har_17.csv, lsoa_har_24.csv
│   ├── lsoa_medppd_17.csv, lsoa_medppd_24.csv
│   ├── missing_ppd_17.csv, missing_ppd_24.csv
│   ├── msoa_income_2018.xls, msoa_income_2023.xlsx
│   ├── postcode_lookup_2602.csv
│   ├── pp-2017-part1.csv, pp-2017-part2.csv, pp-2017.csv, pp-2024.csv
│   ├── ptal2015.csv, ptal2023.csv
│   └── rawepc_17.csv, rawepc_24.csv
├── DATA_ANALYSIS/                  # Stage 2: estimation
│   ├── data_analysis.py
│   ├── final_london_data.csv, final_17_london_data.csv, final_24_london_data.csv
│   ├── lsoa_lad_converter.csv, postcode_lookup_2602.csv
│   └── table1_log_diff.html, table2_cs_lasso.html, table3_cs_standardized.html
├── requirements.txt
└── README.md
```

The cleaned datasets and output tables in `DATA_ANALYSIS/` are included so that Stage 2 can be run without Stage 1. Running Stage 1 regenerates the three `final_*.csv` files in `DATA_ANALYSIS/` and overwrites them.

---

## Data

The unit of observation is the **2021 Lower Layer Super Output Area (LSOA)** in Greater London (4,994 LSOAs, of which 4,987 have at least one recorded transaction in 2017 and 4,986 in 2024). All sources are public UK government or administrative data, harmonised to 2021 LSOA boundaries.

| Module | Source | Files | Use |
| :--- | :--- | :--- | :--- |
| House prices | HM Land Registry, *Price Paid Data* | `pp-*.csv`, `lsoa_medppd_*.csv`, `missing_ppd_*.csv` | LSOA median prices (dependent variable), from all recorded transactions (Category A and B). The 2017 data are downloaded in two parts and concatenated. `missing_ppd_*.csv` lists records without a postcode, which cannot be assigned to an LSOA. |
| Income and HAR | ONS, *Income estimates for small areas*; ONS, *ASHE Table 8* | `la_ukpay_17.xlsx`, `msoa_income_2023.xlsx`, `la_ukpay_24.xlsx`, `lsoa_har_24.csv` | Income is MSOA net equivalised household income before housing costs: FYE 2018 for 2017 (`la_ukpay_17.xlsx`, despite its name) and FYE 2023 for 2024, projected one year with the borough's ASHE 2024 annual pay growth, $Y_{24} = Y_{23}(1+g)$. HAR = LSOA median price / MSOA income. |
| Energy performance and property type | MHCLG, *Energy Performance of Buildings Data* | `rawepc_*.csv` | Certificates lodged in each year, averaged by LSOA. `is_flat` and `is_abc` are therefore **shares** of certificates for flats/maisonettes and for bands A–C, not property-level dummies. |
| Deprivation | MHCLG, *English Indices of Deprivation* (2015, 2019, 2025) | `iod*.csv` | Seven IMD domain scores, part of the candidate control set. |
| Transport access | TfL, *GIS Open Data Hub* | `ptal*.csv` | Mean PTAL and intra-LSOA PTAI gaps, part of the candidate control set. |
| Geography | ONS, *Open Geography Portal* | `postcode_lookup_2602.csv`, `lsoa11_21_lookup.csv` | Postcode-to-LSOA mapping and 2011-to-2021 LSOA conversion. |

**Samples.** Each cross-sectional model uses all LSOAs with complete data in that year (4,803 in 2017; 4,536 in 2024). The log-difference model requires complete data in both years and at least five recorded sales in each year, leaving 4,358 LSOAs (87.26% of London).

**Borough coverage.** ASHE 2024 does not publish annual pay growth for the City of London, Harrow or Richmond upon Thames. For the City, Inner London growth is used instead. For Harrow and Richmond no growth rate is imputed, so 2024 income and HAR are missing and their LSOAs are excluded from the 2024 cross-section and the log-difference model.

**Unused files.** `msoa_income_2018.xls` and `LA_annual_pay_2024.xlsx` are kept for reference but are not read by the code.

**Design choice.** The High-HAR indicator (`is_hhar`) is defined by 2017 HAR above the median and is held fixed in both years. This avoids a mechanical link between 2024 prices and the 2024 classification, but does not remove other sources of confounding. The median is computed within each estimation sample, so the threshold differs slightly between the log-difference and cross-sectional models.

---

## Method

1. **Control selection.** Post-double-selection LASSO, run separately within the High-HAR and Low-HAR subsamples. In each subsample, a LASSO regresses the outcome on the standardised candidate controls (`LassoCV`), and L1-penalised logistic regressions do the same for each variable of interest, `is_flat` and `is_abc` (`LogisticRegressionCV`). Penalties are chosen by 5-fold cross-validation. The union of controls selected in either subsample is retained. Because `is_flat` and `is_abc` are shares, they are converted to integers before the logistic step, which in practice flags LSOAs where the share equals one (see Limitations).
2. **Estimation.** OLS on the variables of interest, their interactions with `is_hhar`, and the selected controls:
   - a **log-difference model** of 2017–2024 median price growth;
   - **cross-sectional models** for 2017 and 2024, using the same control set selected from the full-sample model so that the controls are held fixed across years.

Controls are standardised only for selection; the OLS models use the original units. Standard errors are clustered by local authority district (LAD).

---

## Replication

**Requirements:** Python 3.x and the packages in `requirements.txt` (`pandas`, `numpy`, `scikit-learn`, `statsmodels`, `stargazer`, `openpyxl`, `xlrd`). A virtual environment is recommended.
<!-- CHECK: fill in the exact Python version used. -->

```bash
pip install -r requirements.txt
```

Run from the repository root:

```bash
# Stage 1: clean raw data, compute HAR, harmonise boundaries
python RAW_DATA_AND_CLEANING/data_cleaning.py

# Stage 2: double-selection LASSO and OLS; prints summaries and Wald tests
python DATA_ANALYSIS/data_analysis.py
```

| Output file | Content | Table below |
| :--- | :--- | :--- |
| `table3_cs_standardized.html` | Cross-sectional models, common control set from the full-sample selection | Table 1 |
| `table1_log_diff.html` | Log-difference model | Table 2 |
| `table2_cs_lasso.html` | Cross-sectional models with within-year LASSO controls (robustness check, not reported in the paper) | — |

---

## Results

**Table 1. Cross-sectional OLS with the common control set**

| Variable | (1) 2017 | (2) 2024 |
| :--- | :--- | :--- |
| Intercept | 11.600*** (0.116) | 12.340*** (0.173) |
| is_abc | 0.085* (0.050) | 0.306*** (0.053) |
| is_abc × is_hhar | 0.130** (0.066) | −0.105 (0.073) |
| is_flat | −0.108** (0.045) | −0.159*** (0.043) |
| is_flat × is_hhar | 0.258*** (0.056) | 0.227*** (0.069) |
| is_hhar | 0.226*** (0.027) | 0.146*** (0.036) |
| *Selected controls* | | |
| Crime index | −0.009 | −0.065*** |
| Employment index | 1.007*** | 0.396 |
| Environment index | 0.003*** | 0.005*** |
| Income (£) | 0.000*** | 0.000*** |
| Number of rooms | 0.092*** | 0.152*** |
| Observations | 4,803 | 4,536 |
| R² | 0.717 | 0.629 |

*\* p<0.1; \*\* p<0.05; \*\*\* p<0.01. Standard errors clustered by LAD in parentheses. Income enters in pounds, so its coefficient rounds to 0.000; the 2024 value is projected from FYE 2023 using borough wage growth.*

**Table 2. Log-difference model, 2017–2024**

| Variable | Coefficient |
| :--- | :--- |
| Intercept | 0.080 (0.122) |
| is_abc | 0.100*** (0.036) |
| is_abc × is_hhar | −0.122*** (0.041) |
| is_flat | −0.071*** (0.027) |
| is_flat × is_hhar | −0.015 (0.029) |
| is_hhar | −0.092*** (0.019) |
| Selected controls | 20+ features |
| Observations | 4,358 |
| R² / Adjusted R² | 0.127 / 0.123 |
| F statistic | 41.887*** |

*\* p<0.1; \*\* p<0.05; \*\*\* p<0.01. Standard errors clustered by LAD in parentheses.*

---

## Main Findings

All findings are conditional associations; the mechanisms are interpretations consistent with the estimates, not tested causal channels. Because `is_flat` and `is_abc` are LSOA-level shares, each percentage below compares an LSOA where all EPC-registered dwellings are flats (or rated A–C) with one where none are.

- **Energy efficiency.** The cross-sectional premium for EPC A–C properties rose from 0.085 (p<0.1) in 2017 to 0.306 (p<0.01) in 2024, consistent with a repricing of energy efficiency after the energy cost shock.
- **Energy efficiency across HAR regimes.** In the log-difference model, EPC A–C properties are associated with about 10.5% higher price growth in Low-HAR areas but about 2.2% lower growth in High-HAR areas. One interpretation is that credit-constrained buyers in High-HAR areas were less able to pay for future energy savings as rates rose. The 2024 cross-sectional interaction is not significant, so this evidence comes from the growth model.
- **Flats.** In the cross-section, flats sell at a discount in Low-HAR areas but at a premium over houses in High-HAR areas (+16.2% in 2017, +7.0% in 2024). This is consistent with "down-laddering": buyers priced out of houses turning to flats in the same area.
- **Flats over time.** Flats show lower price growth than houses (−6.9%), and High-HAR flats show the largest growth deficit relative to Low-HAR houses (−16.3%). Together with the shrinking High-HAR flat premium, this suggests that tighter credit weighed most on entry-level properties in high-HAR areas.

---

## Limitations

1. **Identification.** Double selection protects inference from model-selection error, but it does not address confounding. The design relies on unconfoundedness given the selected controls, with no alternative identification strategy (such as an instrument or a difference-in-differences design) to fall back on.
2. **Selection and specification.** Controls are selected separately within each HAR group but enter the final OLS additively, so their coefficients are restricted to be equal across groups. The interactions with `is_hhar` are not treated as separate selection targets.
3. **Penalty choice.** Penalties are chosen by cross-validation rather than the theory-driven plug-in penalty of Belloni, Chernozhukov and Hansen (2014).
4. **Heterogeneity.** Heterogeneity is examined along one pre-chosen dimension (High/Low HAR). Effects may vary along other dimensions that this design cannot detect; data-driven methods such as causal forests would be needed to search for them.
5. **Data.** Median prices use all Price Paid records, including non-standard (Category B) transactions, so a few LSOAs have implausible medians (for example, below £10,000 or above £40 million in 2017). The log-difference sample requires at least five sales per year, which limits their influence; the cross-sectional samples have no such restriction. Harrow and Richmond upon Thames are missing from the 2024 and log-difference samples, which may make them less representative of higher-income outer London. Results have not been re-estimated with these issues corrected.
6. **Treatment selection.** In the selection step, the share variables `is_flat` and `is_abc` are converted to integers, so the treatment equations select controls that predict whether an LSOA consists entirely of flats (or A–C dwellings), rather than the shares themselves. A linear LASSO on the shares would be the correct implementation.

---

## Data Licences

Contains HM Land Registry data © Crown copyright and database right. Contains public sector information from ONS, MHCLG and TfL, licensed under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/). Contains OS data © Crown copyright and database right.
<!-- CHECK: EPC raw files include addresses, which carry separate Royal Mail / OS terms. Check the EPC site's licensing page; if redistribution is not allowed, remove rawepc_*.csv and add download instructions instead. Also check GitHub's 100 MB per-file limit for the pp-*.csv files. -->

## Citation

Ma, Y. (2026). *Heterogeneous Green Premiums and Flat Penalties: Evidence from London*. Independent research paper, University College London.
