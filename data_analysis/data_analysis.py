'''
This file carries out DOUBLE SELECTION DATA ANALYSIS for the research of:
Heterogeneous Green Premiums and Flat Penalties under Credit Constraints and Macroeconomic Shocks: Evidence from London

This is an improved version of LASSO and post-LASSO OLS,
to aim for unbiased OLS estimators
Author: MA, Yuxuan Matt
Researcher: MA, Yuxuan Matt
Department of Economics, UCL
'''
import pandas as pd
import os
import numpy as np
from sklearn.preprocessing import StandardScaler
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor as vif
from stargazer.stargazer import Stargazer
from sklearn.linear_model import LassoCV, LogisticRegressionCV
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

#====================================
# LOAD DATA
#====================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, 'final_london_data.csv'))
print(f'Data loaded: {len(df)} rows, {len(df.columns)} columns.')

#====================================
# DEFINE A FUNCTION FOR TRIPLE SELECTION
#====================================
def selection(X, Y, D1, D2, group):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled_df = pd.DataFrame(X_scaled, columns = X.columns)
    #====================================
    # first stage LASSO: find S1
    #====================================
    print(f'Selection for {group}.')
    print("Running Step 1: Lasso for Y ~ X...")
    # use 5-fold CV
    lasso_y = LassoCV(cv = 5, random_state = 66, max_iter = 10000, n_jobs = -1)
    lasso_y.fit(X_scaled_df, Y)

    # collect variables with non-zero coefficients
    S1 = X.columns[lasso_y.coef_ != 0].tolist()
    print(f"Number of variables in S1: {len(S1)}")

    #====================================
    # second stage LASSO: find S2
    #====================================
    print("Running Step 2: Lasso for D1 ~ X...")
    # use 5-fold CV
    lasso_d1 = LogisticRegressionCV(cv = 5, penalty = 'l1', solver='liblinear', random_state = 66, max_iter = 10000, n_jobs = -1)
    lasso_d1.fit(X_scaled_df, D1.astype(int))

    # collect variables with non-zero coefficients
    S2 = X.columns[lasso_d1.coef_[0] != 0].tolist()
    print(f"Number of variables in S2: {len(S2)}")

    #====================================
    # third stage LASSO: find S3
    #====================================
    print("Running Step 2: Lasso for D2 ~ X...")
    # use 5-fold CV
    lasso_d2 = LogisticRegressionCV(cv = 5, penalty = 'l1', solver='liblinear', random_state = 66, max_iter = 10000, n_jobs = -1)
    lasso_d2.fit(X_scaled_df, D2.astype(int))

    # collect variables with non-zero coefficients
    S3 = X.columns[lasso_d2.coef_[0] != 0].tolist()
    print(f"Number of variables in S3: {len(S3)}")

    #====================================
    # variables for OLS
    #====================================
    union_S = list(set(S1) | set(S2) | set(S3))
    print(f"Number of variables in {group} S1 OR S2 OR S3: {len(union_S)}")
    return union_S

#====================================
# LASSO ON FULL SAMPLE
#====================================

#====================================
# PREPARE DATA: D, X AND Y
#====================================
har_median = df['har_17'].median()
df['is_hhar'] = (df['har_17'] > har_median).astype(int)
nonX_features = ['is_flat','is_abc','lsoa21cd', 'lad25cd', 'vol_17', 'vol_24', 'har_17', 'har_24',
                 'delta_log_price', 'delta_har', 'is_house', 'is_hhar', 'avg_rm_area', 'area']
df_h = df[df['is_hhar'] == 1].copy()
df_l = df[df['is_hhar'] == 0].copy()

D_fhhar = df_h['is_flat']
D_ehhar = df_h['is_abc']
X_hhar = df_h.drop(nonX_features, axis = 1).copy()
Y_hhar = df_h['delta_log_price']

D_flhar = df_l['is_flat']
D_elhar = df_l['is_abc']
X_lhar = df_l.drop(nonX_features, axis = 1).copy()
Y_lhar = df_l['delta_log_price']

union_hhar = selection(X_hhar, Y_hhar, D_fhhar, D_ehhar, 'High HAR')
union_lhar = selection(X_lhar, Y_lhar, D_flhar, D_elhar, 'Low HAR')
union_var = list(set(union_hhar) | set(union_lhar))
print(f'Union of kept variables{union_var}')
print(f'{len(union_var)} are selected')

#====================================
# LASSO ON CROSS SECTIONAL DATA
#====================================
df_17 = pd.read_csv(os.path.join(BASE_DIR, 'final_17_london_data.csv'))
df_24 = pd.read_csv(os.path.join(BASE_DIR, 'final_24_london_data.csv'))

df_17.replace([-np.inf,np.inf], np.nan, inplace = True)
df_17.dropna(inplace = True)
df_24.replace([-np.inf,np.inf], np.nan, inplace = True)
df_24.dropna(inplace = True)

df_17['log_price_17'] = np.log(df_17['medprice_17'])
df_24['log_price_24'] = np.log(df_24['medprice_24'])

har_median_17 = df_17['har_17'].median()
df_17['is_hhar'] = (df_17['har_17'] > har_median_17).astype(int)
lookup_17 = df_17[['lsoa21cd', 'is_hhar']].drop_duplicates() 
df_24_matched = pd.merge(df_24, lookup_17, on='lsoa21cd', how='inner')
df_24 = df_24_matched.copy()

# construct data 2017
nonX_cols_17 = ['lsoa21cd', 'lad25cd_17', 'log_price_17', 'medprice_17',
                'msoanm_17', 'is_flat_17', 'is_abc_17', 'is_hhar', 'har_17',
                'cost_per_sqm_17', 'avg_rm_area_17', 'lptai_17', 'is_house_17']
df_h17 = df_17[df_17['is_hhar'] == 1]
df_l17 = df_17[df_17['is_hhar'] == 0]

X_hhar17 = df_h17.copy().drop(nonX_cols_17, axis = 1)
Y_hhar17 = df_h17['log_price_17']
D_fhhar17 = df_h17['is_flat_17']
D_ehhar17 = df_h17['is_abc_17']

X_lhar17 = df_l17.copy().drop(nonX_cols_17, axis = 1)
Y_lhar17 = df_l17['log_price_17']
D_flhar17 = df_l17['is_flat_17']
D_elhar17 = df_l17['is_abc_17']

union_h17 = selection(X_hhar17, Y_hhar17, D_fhhar17, D_ehhar17, 'High-HAR 2017')
union_l17 = selection(X_lhar17, Y_lhar17, D_flhar17, D_elhar17, 'Low-HAR 2017')

# construct data 2024
nonX_cols_24 = ['lsoa21cd', 'lad25cd_24', 'log_price_24', 'medprice_24',
                'msoanm_24', 'is_flat_24', 'is_abc_24', 'is_hhar', 'har_24',
                'cost_per_sqm_24', 'avg_rm_area_24', 'lptai_24', 'is_house_24']
df_h24 = df_24[df_24['is_hhar'] == 1]
df_l24 = df_24[df_24['is_hhar'] == 0]

X_hhar24 = df_h24.copy().drop(nonX_cols_24, axis = 1)
Y_hhar24 = df_h24['log_price_24']
D_fhhar24 = df_h24['is_flat_24']
D_ehhar24 = df_h24['is_abc_24']

X_lhar24 = df_l24.copy().drop(nonX_cols_24, axis = 1)
Y_lhar24 = df_l24['log_price_24']
D_flhar24 = df_l24['is_flat_24']
D_elhar24 = df_l24['is_abc_24']

union_h24 = selection(X_hhar24, Y_hhar24, D_fhhar24, D_ehhar24, 'High-HAR 2024')
union_l24 = selection(X_lhar24, Y_lhar24, D_flhar24, D_elhar24, 'Low-HAR 2024')

# Take Union
union_17 = set(union_h17) | set(union_l17)
union_24 = set(union_h24) | set(union_l24)

#====================================
# Post-LASSO OLS
#====================================
# LOG DIFFERENCE MODEL
#====================================
controls_str = " + ".join(union_var)
formula = f"delta_log_price ~ 1 + (is_flat + is_abc + {controls_str}) * is_hhar"
formula = f"delta_log_price ~ 1 + is_flat * is_hhar + is_abc * is_hhar + {controls_str}"
model = smf.ols(formula = formula, data=df)

# cluster by LAD
results_logd = model.fit(cov_type='cluster', 
                    cov_kwds={'groups': df['lad25cd']})

# summary
print(results_logd.summary())

hypotheses = '(is_flat:is_hhar = 0), (is_abc:is_hhar = 0)'
wald_test = results_logd.wald_test(hypotheses)
print(wald_test)

#====================================
# CROSS SECTIONAL OLS: USE VARIABLES FROM 2017 AND 2024 LASSO
#====================================
union_base = set()
for var in union_17:
    union_base.add(var.replace('_17', ''))
for var in union_24:
    union_base.add(var.replace('_24', ''))
list17 = [f'{var}_17' for var in union_base]
remove17 = ['ptai_gap23_17', 'est24income_17', 'mean_ptai23_17', 'is_after2012_17']
cols_17lasso = [item for item in list17 if item not in remove17]

list24 = [f'{var}_24' for var in union_base]
remove24 = ['ptai_gap15_24', 'income_24', 'mean_ptai15_24', 'is_newbuilt_24']
cols_24lasso = [item for item in list24 if item not in remove24]

controls_str17lasso = ' + '.join(cols_17lasso)
formula_17lasso = f'log_price_17 ~ 1 + is_flat_17 * is_hhar + is_abc_17 * is_hhar + {controls_str17lasso}'
model_17lasso = smf.ols(formula = formula_17lasso, data = df_17)

controls_str24lasso = '+'.join(cols_24lasso)
formula_24lasso = f'log_price_24 ~ 1 + is_flat_24 * is_hhar + is_abc_24 * is_hhar + {controls_str24lasso}'
model_24lasso = smf.ols(formula = formula_24lasso, data = df_24)

results_17lasso = model_17lasso.fit(cov_type = 'cluster',
                                    cov_kwds = {'groups': df_17['lad25cd_17']})
results_24lasso = model_24lasso.fit(cov_type = 'cluster',
                                    cov_kwds = {'groups': df_24['lad25cd_24']})

print(results_17lasso.summary())
print(results_24lasso.summary())

#====================================
# CROSS SECTIONAL OLS: USE VARIABLES FROM FULL-SAMPLE LASSO
#====================================
cols_17 = [
    'is_poor_roof_17', 'income_17', 'hsbar_17', 'crm_17', 'health_17', 
    'emp_17', 'mean_ptai15_17', 'is_poor_wall_17', 'env_17', 'est_17', 
    'num_rms_17', 'is_off_gas_17', 'multiglaze_pct_17', 'ptai_gap15_17', 
    'is_newbuilt_17']
cols_24 = [
    'is_poor_roof_24', 'est24income_24', 'hsbar_24', 'crm_24', 'health_24', 
    'emp_24', 'mean_ptai23_24', 'is_poor_wall_24', 'env_24', 'est_24', 
    'num_rms_24', 'is_off_gas_24', 'multiglaze_pct_24', 'ptai_gap23_24', 
    'is_after2012_24']

controls_str_17 = " + ".join(cols_17)
controls_str_24 = " + ".join(cols_24)

df_24.dropna(subset=['is_hhar'], inplace=True)
df_24['is_hhar'] = df_24['is_hhar'].astype(int)

formula_17 = f"log_price_17 ~ 1 + is_flat_17 * is_hhar + is_abc_17 * is_hhar + {controls_str_17}"
model_17 = smf.ols(formula = formula_17, data = df_17)

formula_24 = f"log_price_24 ~ 1 + is_flat_24 * is_hhar + is_abc_24 * is_hhar + {controls_str_24}"
model_24 = smf.ols(formula = formula_24, data = df_24)

results_17 = model_17.fit(cov_type='cluster', 
                    cov_kwds={'groups': df_17['lad25cd_17']})

results_24 = model_24.fit(cov_type='cluster', 
                    cov_kwds={'groups': df_24['lad25cd_24']})


print(results_17.summary())
print(results_24.summary())

#====================================
# STARGAZER OUTPUT: FULL SAMPLE LASSO
#====================================
# Table 1: Log Difference
stargazer_1 = Stargazer([results_logd])
stargazer_1.title('Post-LASSO Log Difference Model (Full Sample)')
stargazer_1.custom_columns(['Log Difference Model'], [1])
stargazer_1.show_model_numbers(False)
stargazer_1.significant_digits(3)

with open("table1_log_diff.html", "w") as f:
    f.write(stargazer_1.render_html())
print("Saved Table 1 to table1_log_diff.html")

#====================================
# STARGAZER OUTPUT: 2017 2024 CROSS-SECTIONAL LASSO
#====================================
# Table 2: Within-year LASSO
stargazer_2 = Stargazer([results_17lasso, results_24lasso])
stargazer_2.title('Cross-Sectional OLS Regression Models using Within-year LASSO variables')
stargazer_2.custom_columns(['2017 Model', '2024 Model'], [1, 1])
stargazer_2.show_model_numbers(False)
stargazer_2.significant_digits(3)

with open("table2_cs_lasso.html", "w") as f:
    f.write(stargazer_2.render_html())
print("Saved Table 2 to table2_cs_lasso.html")

#====================================
# STARGAZER OUTPUT: 2017 2024 USING FULL-SAMPLE LASSO VAR
#====================================
# Table 3: Full-sample LASSO / Standardized 15 Features
stargazer_3 = Stargazer([results_17, results_24])
stargazer_3.title('Cross-Sectional OLS Regression Models using Standardized Feature Set')
stargazer_3.custom_columns(['2017 Model', '2024 Model'], [1, 1])
stargazer_3.show_model_numbers(False)
stargazer_3.significant_digits(3)

with open("table3_cs_standardized.html", "w") as f:
    f.write(stargazer_3.render_html())
print("Saved Table 3 to table3_cs_standardized.html")