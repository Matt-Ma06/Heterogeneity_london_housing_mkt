'''
Only initial data cleaning is carried out in this file, data analysis is in
data_analysis.py
This is the data cleaning section for the research of:
Heterogeneous Green Premiums and Flat Penalties under Credit Constraints and Macroeconomic Shocks: Evidence from London

Author: MA, Yuxuan Matt
Researcher: MA, Yuxuan Matt
Email: matt.ma.24@ucl.ac.uk
DEPARTMENT OF ECONOMICS, UNIVERSITY COLLEGE LONDON
'''

import pandas as pd
import numpy as np
import os

# set up path configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = BASE_DIR

#=========================================
# CLEAN: numerator, 2017 and 2024 PPD
#=========================================
file_17_p1 = os.path.join(DATA_DIR, 'pp-2017-part1.csv')
file_17_p2 = os.path.join(DATA_DIR, 'pp-2017-part2.csv')
file_24 = os.path.join(DATA_DIR, 'pp-2024.csv')

df17_p1 = pd.read_csv(file_17_p1, header = None)
df17_p2 = pd.read_csv(file_17_p2, header = None)
df24 = pd.read_csv(file_24, header = None)

df17 = pd.concat([df17_p1, df17_p2], axis=0, ignore_index=True)

len(df17) == len(df17_p1) + len(df17_p2)    # check

# drop unnecessary cols
df17_dropped = df17.drop([0, 2, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15], axis = 1)
df24_dropped = df24.drop([0, 2, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15], axis = 1)

df17_dropped = df17_dropped.rename(columns = {1: 'price', 3: 'postcode', 12: 'district', 13: 'county'})
df24_dropped = df24_dropped.rename(columns = {1: 'price', 3: 'postcode', 12: 'district', 13: 'county'})

df_london_17 = df17_dropped[df17_dropped['county'] == 'GREATER LONDON'].copy()
df_london_24 = df24_dropped[df24_dropped['county'] == 'GREATER LONDON'].copy()

# add LSOA columns to ppd
lookup_keep_cols = [
    'pcds', 'lsoa21cd', 'rgn25cd', 'lad25cd', 
    'doterm', 'lat', 'long', 'msoa21cd'
]
df_lookup = pd.read_csv(os.path.join(DATA_DIR, 'postcode_lookup_2602.csv'),
                        usecols = lookup_keep_cols, low_memory = False)
print(df_lookup.columns.tolist) # check headers
df_lookup_dropped = df_lookup[['pcds', 'lsoa21cd', 'rgn25cd','lad25cd',
                               'doterm', 'lat', 'long', 'msoa21cd']]
df_lookup_london = df_lookup_dropped[df_lookup_dropped['rgn25cd'] == 'E12000007'].copy()
df_lookup_london['clean_pc'] = df_lookup_london['pcds'].str.replace(' ','').str.upper()

df_london_17['clean_pc'] = df_london_17['postcode'].str.replace(' ', '').str.upper()
df_london_24['clean_pc'] = df_london_24['postcode'].str.replace(' ', '').str.upper()

# start to merge
df_merged_ppd_17 = pd.merge(df_london_17, 
                            df_lookup_london[['clean_pc', 'lsoa21cd', 'lad25cd', 'msoa21cd']],
                            how = 'inner',
                            on = 'clean_pc')
df_merged_ppd_24 = pd.merge(df_london_24, 
                            df_lookup_london[['clean_pc', 'lsoa21cd', 'lad25cd', 'msoa21cd']],
                            how = 'inner',
                            on = 'clean_pc')
df_check17 = pd.merge(df_london_17,
                    df_lookup_london[['clean_pc', 'lsoa21cd', 'lad25cd']],
                    how = 'left',
                    on = 'clean_pc')

df_check24 = pd.merge(df_london_24,
                    df_lookup_london[['clean_pc', 'lsoa21cd', 'lad25cd']],
                    how = 'left',
                    on = 'clean_pc')

# some data missing, save to analyse later
missing_17 = df_check17[df_check17['postcode'].isna()]

missing_24 = df_check24[df_check24['postcode'].isna()]

# number of missing data
no_missing_17 = len(missing_17)
no_missing_24 = len(missing_24)
print(f'Number of data missing 2017: {no_missing_17}.')
print(f'Number of data missing 2024: {no_missing_24}.')

# COMPUTE MEDIAN PPD FOR EACH LSOA
lsoa_medppd_17 = df_merged_ppd_17.groupby(['lsoa21cd', 'msoa21cd', 'lad25cd']).agg(
    medprice = ('price', 'median'),
    volume = ('price', 'count')
    ).reset_index()
missing_17.to_csv(os.path.join(DATA_DIR, 'missing_ppd_17.csv'), index=False)

lsoa_medppd_24 = df_merged_ppd_24.groupby(['lsoa21cd', 'msoa21cd', 'lad25cd']).agg(
    medprice = ('price', 'median'),
    volume = ('price', 'count')
    ).reset_index()
missing_24.to_csv(os.path.join(DATA_DIR, 'missing_ppd_24.csv'), index=False)

#=========================================
# CLEAN: denominator, 2024 annual income
#=========================================
# read 2024 income growth by borough
la_pay_24 = pd.read_excel(os.path.join(DATA_DIR,'la_ukpay_24.xlsx'), header = None)
la_pay_24.rename(columns = {0: 'LA', 1: 'lacd', 2: '24income', 3: 'annual_pct_chg'}, inplace = True)
la_pay_24.drop(index = [0, 1, 2, 3, 4], inplace = True)

# read 2023 income by lsoa
msoa_pay_23 = pd.read_excel(os.path.join(DATA_DIR,'msoa_income_2023.xlsx'),
                            sheet_name = 'Net income before housing costs', header = 3)
msoa_pay_23.rename(columns = {'MSOA code': 'msoacd',
                              'MSOA name': 'msoanm',
                              'Local authority code': 'lacd',
                              'Local authority name': 'lanm',
                              'Region code': 'rgncd',
                              'Region name': 'rgnnm',
                              'Disposable (net) annual income before housing costs (£)': '23income'}, inplace =True)
msoa_pay_23.drop(['Upper confidence limit (£)', 'Lower confidence limit (£)','Confidence interval (£)'], axis = 1, inplace = True)

# merge and compute 2024 income by MSOA
msoa_pay_24 = pd.merge(msoa_pay_23, la_pay_24[['LA', 'lacd', '24income', 'annual_pct_chg']],
                       how = 'left',
                       on = 'lacd')
df_check_pay24 = msoa_pay_24[msoa_pay_24['LA'].isna()]

# some LA were abolished on 1 Apr 2023, but doesn't affect London

# filter out london (starts with E09)
msoa_pay_24['lacd'] = msoa_pay_24['lacd'].astype(str)
london_msoa_pay_24 = msoa_pay_24[msoa_pay_24['lacd'].str.startswith('E09', na=False)].copy()
london_msoa_pay_24['est24income'] = london_msoa_pay_24['23income']*(1 + london_msoa_pay_24['annual_pct_chg']/100)
london_msoa_pay_24.reset_index(inplace = True)

# note that City doesn't have value due to few residents, use inner london growth
la_pay_24[la_pay_24['LA'] == '  City of London']
la_pay_24[la_pay_24['LA'] == 'Inner London']
london_msoa_pay_24[london_msoa_pay_24['lanm'] == 'City of London']
inner_growth = la_pay_24.loc[la_pay_24['LA'] == 'Inner London', 'annual_pct_chg'].values[0]

# hard code the estimated median income for City in 2024
city_mask = london_msoa_pay_24['lanm'] == 'City of London'

london_msoa_pay_24.loc[city_mask, 'est24income'] = london_msoa_pay_24.loc[city_mask, '23income'] * (1 + inner_growth / 100)
london_msoa_pay_24.rename(columns = {'msoacd': 'msoa21cd'}, inplace = True)

#=========================================
# merge 2024 income and 2024 ppd
#=========================================
lsoa_incppd_24 = pd.merge(lsoa_medppd_24,
                          london_msoa_pay_24[['est24income','msoa21cd', 'msoanm']],
                          on = 'msoa21cd',
                          how = 'left')

# compute 2024 HAR
lsoa_incppd_24['har'] = lsoa_incppd_24['medprice'] / lsoa_incppd_24['est24income']
lsoa_har_24 = lsoa_incppd_24[['lsoa21cd', 'har']].copy()
lsoa_har_24.to_csv(os.path.join(DATA_DIR, 'lsoa_har_24.csv'), index=False)
#=========================================
# merge 2017 income and 2017 ppd
#=========================================
msoa_pay_17 = pd.read_excel(os.path.join(DATA_DIR,'la_ukpay_17.xlsx'), header = 4)
msoa_pay_17.rename(columns = {'MSOA code': 'msoa21cd',
                              'MSOA name': 'msoanm',
                              'Local authority code': 'lacd',
                              'Local authority name': 'lanm',
                              'Region code': 'rgncd',
                              'Region name': 'rgnnm',
                              'Net annual income before housing costs (£)': 'income'}, inplace =True)
msoa_pay_17.drop(['Upper confidence limit (£)', 'Lower confidence limit (£)','Confidence interval (£)'], axis = 1, inplace = True)
msoa_pay_17 = msoa_pay_17[msoa_pay_17['lacd'].str.startswith('E09')]
lsoa_incppd_17 = pd.merge(lsoa_medppd_17,
                          msoa_pay_17[['income','msoa21cd', 'msoanm']],
                          on = 'msoa21cd',
                          how = 'left')
lsoa_incppd_17['har'] = lsoa_incppd_17['medprice'] / lsoa_incppd_17['income']

#=========================================
# Index of Deprivation
#=========================================
keep_cols_15 = [
    'LSOA code (2011)', 
    'Index of Multiple Deprivation (IMD) Score',
    'Income Score (rate)', 
    'Employment Score (rate)', 
    'Education, Skills and Training Score',
    'Health Deprivation and Disability Score', 
    'Crime Score', 
    'Barriers to Housing and Services Score', 
    'Living Environment Score'
]

keep_cols_19 = keep_cols_15

keep_cols_25 = [
    'LSOA code (2021)', 
    'Index of Multiple Deprivation (IMD) Score',
    'Income Score (rate)', 
    'Employment Score (rate)', 
    'Education, Skills and Training Score',
    'Health Deprivation and Disability Score', 
    'Crime Score', 
    'Barriers to Housing and Services Score', 
    'Living Environment Score'
]

rawiod15 = pd.read_csv(os.path.join(DATA_DIR, 'iod15.csv'), usecols = keep_cols_15)

rawiod15.rename(columns = {'LSOA code (2011)': 'lsoa11cd',
                           'Index of Multiple Deprivation (IMD) Score': 'imd',
                           'Income Score (rate)': 'inc',
                           'Employment Score (rate)': 'emp',
                           'Education, Skills and Training Score': 'est',
                           'Health Deprivation and Disability Score': 'health',
                           'Crime Score': 'crm',
                           'Barriers to Housing and Services Score': 'hsbar',
                           'Living Environment Score': 'env'}, inplace = True)

rawiod19 = pd.read_csv(os.path.join(DATA_DIR,'iod19.csv'), usecols = keep_cols_19)

rawiod19.rename(columns = {'LSOA code (2011)': 'lsoa11cd',
                           'Index of Multiple Deprivation (IMD) Score': 'imd',
                           'Income Score (rate)': 'inc',
                           'Employment Score (rate)': 'emp',
                           'Education, Skills and Training Score': 'est',
                           'Health Deprivation and Disability Score': 'health',
                           'Crime Score': 'crm',
                           'Barriers to Housing and Services Score': 'hsbar',
                           'Living Environment Score': 'env'}, inplace = True)

iod25 = pd.read_csv(os.path.join(DATA_DIR,'iod25.csv'), usecols = keep_cols_25)

iod25.rename(columns = {'LSOA code (2021)': 'lsoa21cd',
                           'Index of Multiple Deprivation (IMD) Score': 'imd',
                           'Income Score (rate)': 'inc',
                           'Employment Score (rate)': 'emp',
                           'Education, Skills and Training Score': 'est',
                           'Health Deprivation and Disability Score': 'health',
                           'Crime Score': 'crm',
                           'Barriers to Housing and Services Score': 'hsbar',
                           'Living Environment Score': 'env'}, inplace = True)

# merge 2015 and 2019 to get 2017
iod1711 = pd.merge(rawiod15, rawiod19,
                 how = 'inner', on = 'lsoa11cd')
iod1711['imd'] = (iod1711['imd_x'] + iod1711['imd_y']) / 2
iod1711['inc'] = (iod1711['inc_x'] + iod1711['inc_y']) / 2
iod1711['emp'] = (iod1711['emp_x'] + iod1711['emp_y']) / 2
iod1711['est'] = (iod1711['est_x'] + iod1711['est_y']) / 2
iod1711['crm'] = (iod1711['crm_x'] + iod1711['crm_y']) / 2
iod1711['hsbar'] = (iod1711['hsbar_x'] + iod1711['hsbar_y']) / 2 
iod1711['health'] = (iod1711['health_x'] + iod1711['health_y']) / 2 
iod1711['env'] = (iod1711['env_x'] + iod1711['env_y']) / 2
keep_cols = [
    'lsoa11cd', 'imd', 'inc', 'emp', 'est', 
    'health', 'crm', 'hsbar', 'env'
]
iod1711 = iod1711[keep_cols].copy()

# 2011 - 2021 LSOA conversion
df_lsoa_lookup = pd.read_csv(os.path.join(DATA_DIR,'lsoa11_21_lookup.csv'),
                            usecols = ['LSOA11CD', 'LSOA21CD', 'LAD22CD'])

df_lsoa_lookup.rename(columns = {'LSOA11CD': 'lsoa11cd',
                                 'LSOA21CD': 'lsoa21cd',
                                 'LAD22CD': 'lad22cd'}, inplace = True)

df_lsoa_lookup_ld = df_lsoa_lookup[df_lsoa_lookup['lad22cd'].str.startswith('E09')].copy()

iod17 = pd.merge(iod1711, df_lsoa_lookup_ld, how = 'inner', on = 'lsoa11cd').groupby(
    'lsoa21cd').mean(numeric_only = True).reset_index()

# merge 2017 iod with ppd and income
df_incppdiod_17 = pd.merge(lsoa_incppd_17, iod17,
                 how = 'inner', on = 'lsoa21cd')

# merge 2024 iod with ppd and income
df_incppdiod_24 = pd.merge(lsoa_incppd_24, iod25,
                           how = 'inner', on = 'lsoa21cd')

#=========================================
# EPC DATA
#=========================================
# keep cols
epc_keep_cols = [
    'POSTCODE',                   
    'LODGEMENT_DATE',              
    'CURRENT_ENERGY_RATING',       
    'CURRENT_ENERGY_EFFICIENCY',   
    'LIGHTING_COST_CURRENT',       
    'HEATING_COST_CURRENT',        
    'HOT_WATER_COST_CURRENT',      
    'TOTAL_FLOOR_AREA',            
    'NUMBER_HABITABLE_ROOMS',     
    'PROPERTY_TYPE',        
    'CONSTRUCTION_AGE_BAND',
    'MAINS_GAS_FLAG',           
    'WALLS_ENERGY_EFF',         
    'ROOF_ENERGY_EFF',          
    'MULTI_GLAZE_PROPORTION'       
]

# rename cols
epc_cols_renm = {           
    'LODGEMENT_DATE' : 'date',              
    'CURRENT_ENERGY_RATING': 'rating',       
    'CURRENT_ENERGY_EFFICIENCY': 'eff',   
    'LIGHTING_COST_CURRENT': 'cost_lighting',       
    'HEATING_COST_CURRENT': 'cost_heating',        
    'HOT_WATER_COST_CURRENT': 'cost_hwater',      
    'TOTAL_FLOOR_AREA': 'area',            
    'NUMBER_HABITABLE_ROOMS' : 'num_rms',     
    'PROPERTY_TYPE': 'prop_type',        
    'CONSTRUCTION_AGE_BAND': 'age',
    'MAINS_GAS_FLAG': 'mains_gas',           
    'WALLS_ENERGY_EFF': 'wall_eff',         
    'ROOF_ENERGY_EFF': 'roof_eff',          
    'MULTI_GLAZE_PROPORTION': 'multiglaze_pct' 
}
# handle 2024 data
raw_epc24 = pd.read_csv(os.path.join(DATA_DIR,'rawepc_24.csv'), usecols = epc_keep_cols)
raw_epc24['clean_pc'] = raw_epc24['POSTCODE'].str.replace(' ', '').str.strip()
raw_epc24.rename(columns = epc_cols_renm, inplace = True)
raw_epc24.drop('POSTCODE', axis = 1, inplace = True)

# add LSOA
lsoa_epc24 = pd.merge(raw_epc24, df_lookup_london[['lsoa21cd', 'clean_pc']],
                      how = 'inner', on = 'clean_pc')

# CONTINUOUS VARIABLE GENERATION
lsoa_epc24['total_energy_cost'] = lsoa_epc24['cost_lighting'] + lsoa_epc24['cost_heating'] + lsoa_epc24['cost_hwater']
lsoa_epc24['cost_per_sqm'] = lsoa_epc24['total_energy_cost']/lsoa_epc24['area']
lsoa_epc24['avg_rm_area'] = lsoa_epc24['area']/lsoa_epc24['num_rms']

# BINARY FLAGS
# EPC: A/B/C are good\
lsoa_epc24['is_abc'] = lsoa_epc24['rating'].isin(['A', 'B', 'C']).astype('int')

# roof: poor = 1, good/na = 0
is_poor_roof = lsoa_epc24['roof_eff'].str.contains('poor', na = False, case = False)
lsoa_epc24['is_poor_roof'] = is_poor_roof.astype('int')

# wall: poor = 1, good/na = 0
is_poor_wall = lsoa_epc24['wall_eff'].str.contains('poor', na = False, case = False)
lsoa_epc24['is_poor_wall'] = is_poor_wall.astype('int')

# gas: off gas = 1, na/y = 0
lsoa_epc24['is_off_gas'] = (lsoa_epc24['mains_gas'].str.strip().str.upper() == 'N').astype(int)

# flat: flat = 1, others = 0
lsoa_epc24['prop_type'].unique()    # check all possible types
lsoa_epc24['is_flat'] = lsoa_epc24['prop_type'].str.contains('Flat|Maisonette', na = False, case = False).astype('int')
lsoa_epc24['is_house'] = lsoa_epc24['prop_type'].str.contains('House|Bungalow', na = False, case = False).astype('int')

# age: pre 1930 = 1; after 2012 = 1; others = 0
lsoa_epc24['age'].unique()  # check all possible types
is_pre1930 = r'1900-1929|^19[012]\d$|before 1900|^18\d{2}$|before 1900'
lsoa_epc24['is_pre1930'] = lsoa_epc24['age'].str.strip().str.contains(
    is_pre1930, regex = True, case = False, na = False).astype('int')

is_after2012 = r'2012 onwards|^201[2-9]$|^20[2-9]\d$'
lsoa_epc24['is_after2012'] = lsoa_epc24['age'].str.strip().str.contains(
    is_after2012, regex = True, case = False, na = False).astype('int')

# ensure pct of double glazing windows is numeric
lsoa_epc24['multiglaze_pct'] = pd.to_numeric(lsoa_epc24['multiglaze_pct'], errors = 'coerce')
lsoa_epc24['cost_per_sqm'].isna().any()   # no NA, we have all values valid

# groupby LSOA
epc24 = lsoa_epc24.groupby('lsoa21cd').mean(numeric_only = True).reset_index()

# merge with all data we have
df_incppdiodepc_24 = pd.merge(df_incppdiod_24, epc24, how = 'inner', on = 'lsoa21cd')

# handle 2017 data
raw_epc17 = pd.read_csv(os.path.join(DATA_DIR,'rawepc_17.csv'), usecols = epc_keep_cols)
raw_epc17['clean_pc'] = raw_epc17['POSTCODE'].str.replace(' ', '').str.strip()
raw_epc17.rename(columns = epc_cols_renm, inplace = True)
raw_epc17.drop('POSTCODE', axis = 1, inplace = True)

# add LSOA
lsoa_epc17 = pd.merge(raw_epc17, df_lookup_london[['lsoa21cd', 'clean_pc']],
                      how = 'inner', on = 'clean_pc')

# CONTINUOUS VARIABLE GENERATION
lsoa_epc17['total_energy_cost'] = lsoa_epc17['cost_lighting'] + lsoa_epc17['cost_heating'] + lsoa_epc17['cost_hwater']
lsoa_epc17['cost_per_sqm'] = lsoa_epc17['total_energy_cost']/lsoa_epc17['area']
lsoa_epc17['avg_rm_area'] = lsoa_epc17['area']/lsoa_epc17['num_rms']

# BINARY FLAGS
# EPC: A/B/C are good\
lsoa_epc17['is_abc'] = lsoa_epc17['rating'].isin(['A', 'B', 'C']).astype('int')

# roof: poor = 1, good/na = 0
is_poor_roof = lsoa_epc17['roof_eff'].str.contains('poor', na = False, case = False)
lsoa_epc17['is_poor_roof'] = is_poor_roof.astype('int')

# wall: poor = 1, good/na = 0
is_poor_wall = lsoa_epc17['wall_eff'].str.contains('poor', na = False, case = False)
lsoa_epc17['is_poor_wall'] = is_poor_wall.astype('int')

# gas: off gas = 1, na/y = 0
lsoa_epc17['is_off_gas'] = (lsoa_epc17['mains_gas'].str.strip().str.upper() == 'N').astype(int)

# flat: flat = 1, others = 0
lsoa_epc17['prop_type'].unique()    # check all possible types
lsoa_epc17['is_flat'] = lsoa_epc17['prop_type'].str.contains('Flat|Maisonette', na = False, case = False).astype('int')
lsoa_epc17['is_house'] = lsoa_epc17['prop_type'].str.contains('House|Bungalow', na = False, case = False).astype('int')

# age: pre 1930 = 1; after 2012 = 1; others = 0
lsoa_epc17['age'].unique()  # check all possible types
is_pre1930 = r'1900-1929|before 1900'
lsoa_epc17['is_pre1930'] = lsoa_epc17['age'].str.strip().str.contains(
    is_pre1930, regex = True, case = False, na = False).astype('int')

is_newbuilt = r'2007 onwards'
lsoa_epc17['is_newbuilt'] = lsoa_epc17['age'].str.strip().str.contains(
    is_newbuilt, regex = True, case = False, na = False).astype('int')

# ensure pct of double glazing windows is numeric
lsoa_epc17['multiglaze_pct'] = pd.to_numeric(lsoa_epc17['multiglaze_pct'], errors = 'coerce')
lsoa_epc17['cost_per_sqm'].isna().any()   # no NA, we have all values valid

# groupby LSOA
epc17 = lsoa_epc17.groupby('lsoa21cd').mean(numeric_only = True).reset_index()

# merge with all data we have
df_incppdiodepc_17 = pd.merge(df_incppdiod_17, epc17, how = 'inner', on = 'lsoa21cd')

#=========================================
# PTAL DATA BY TFL
#=========================================
# 2015 data, for 2017
raw_ptal15 = pd.read_csv(os.path.join(DATA_DIR,'ptal2015.csv'))

raw_ptal15.rename(columns = {'LSOA2011': 'lsoa11cd', 'AvPTAI2015': 'mean_ptai15',
                             'PTAL': 'ptal', 'PTAIHigh': 'hptai', 'PTAILow': 'lptai'},
                             inplace = True)
lsoa21_ptal15 = pd.merge(raw_ptal15, df_lsoa_lookup[['lsoa11cd', 'lsoa21cd']], on = 'lsoa11cd', how = 'inner')

# compute gap (gap between potential PTAI)
lsoa21_ptal15['ptai_gap15'] = lsoa21_ptal15['hptai'] - lsoa21_ptal15['lptai']
lsoa21_ptal15.drop('lsoa11cd', axis = 1, inplace = True)

# after converting from 2011 LSOA to 2021, 
# some 11LSOA are mapped to one 21LSOA or one 11LSOA is splitted into several 21 LSOA
# so we need to group by lsoa21
ptal15 = lsoa21_ptal15.groupby('lsoa21cd').agg({
    'mean_ptai15': 'mean',
    'lptai': 'min',
    'hptai': 'max',
    'ptai_gap15': 'mean',
}).reset_index()

# 2023 data, for 2024
raw_ptal23 = pd.read_csv(os.path.join(DATA_DIR,'ptal2023.csv'))

raw_ptal23.rename(columns = {'LSOA21CD': 'lsoa21cd', 'mean_AI': 'mean_ptai23',
                             'MIN_AI': 'lptai', 'MAX_AI': 'hptai'},
                             inplace = True)
ptal23 = raw_ptal23[['lsoa21cd', 'mean_ptai23', 'lptai', 'hptai']].copy()
ptal23['ptai_gap23'] = ptal23['hptai'] - ptal23['lptai']


# merge 2015 & 2017, 2023 & 2024
df_incppdiodepcptal_17 = pd.merge(df_incppdiodepc_17, ptal15, how = 'inner', on = 'lsoa21cd')
df_incppdiodepcptal_24 = pd.merge(df_incppdiodepc_24, ptal23, how = 'inner', on = 'lsoa21cd')

#=========================================
# merge 2017 and 2024
#=========================================
df_master_17 = df_incppdiodepcptal_17.copy()
df_master_24 = df_incppdiodepcptal_24.copy()

# add suffix to columns
df_master_17 = df_master_17.set_index('lsoa21cd').add_suffix('_17').reset_index()
df_master_24 = df_master_24.set_index('lsoa21cd').add_suffix('_24').reset_index()

# drop unnecessary columns
df_master_17.drop(['msoa21cd_17', 'imd_17', 'total_energy_cost_17'], axis = 1, inplace = True)
df_master_24.drop(['msoa21cd_24', 'imd_24', 'total_energy_cost_24'], axis = 1, inplace = True)

# merge all
df_master = pd.merge(df_master_17, df_master_24, on = 'lsoa21cd', how = 'inner')
df_master.columns

#=========================================
# generate differences
#=========================================

# KEY DEPENDENT VARIABLE: PRICE, TAKE LOG DIFF
df_final = pd.DataFrame() # initialise a df for final data
df_final['lsoa21cd'] = df_master['lsoa21cd']
df_final['lad25cd'] = df_master['lad25cd_17']
df_final['delta_log_price'] = np.log(df_master['medprice_24']) - np.log(df_master['medprice_17'])

# KEY EXPLANATORY VARIABLE: INCOME, TAKE PCT CHANGE 17-24
df_final['delta_inc_pct'] = (df_master['est24income_24'] - df_master['income_17']) / df_master['income_17']

# VOLUME
df_final['vol_17'] = df_master['volume_17']
df_final['vol_24'] = df_master['volume_24']
# PTAL CHANGE
df_final['delta_avg_ptai'] = df_master['mean_ptai23_24'] - df_master['mean_ptai15_17']
df_final['delta_hptai'] = df_master['hptai_24'] - df_master['hptai_17']
df_final['mean_ptai15_17'] = df_master['mean_ptai15_17']
df_final['delta_ptai_gap'] = df_master['ptai_gap23_24'] - df_master['ptai_gap15_17']
df_final['ptai_gap_17'] = df_master['ptai_gap15_17']

# IOD SCORE CHANGES
df_final['delta_inc'] = df_master['inc_24'] - df_master['inc_17']
df_final['delta_emp'] = df_master['emp_24'] - df_master['emp_17']
df_final['delta_est'] = df_master['est_24'] - df_master['est_17']
df_final['delta_health'] = df_master['health_24'] - df_master['health_17']
df_final['delta_crm'] = df_master['crm_24'] - df_master['crm_17']
df_final['delta_hsbar'] = df_master['hsbar_24'] - df_master['hsbar_17']
df_final['delta_env'] = df_master['env_24'] - df_master['env_17']

# UNVARIED PHYSICAL IDENTITIES
df_final['area'] = df_master['area_17']
df_final['mean_num_rms'] = df_master['num_rms_17']
df_final['is_flat'] = df_master['is_flat_17']
df_final['is_house'] = df_master['is_house_17']
df_final['is_pre1930'] = df_master['is_pre1930_17']
df_final['cost_per_sqm'] = df_master['cost_per_sqm_17']
df_final['is_abc'] = df_master['is_abc_17']
df_final['multiglaze_pct'] = df_master['multiglaze_pct_17']
df_final['is_newbuilt'] = df_master['is_newbuilt_17']
df_final['is_poor_roof'] = df_master['is_poor_roof_17']
df_final['is_poor_wall'] = df_master['is_poor_wall_17']
df_final['is_off_gas'] = df_master['is_off_gas_17']
df_final['avg_rm_area'] = df_master['avg_rm_area_17']

# CONTROLS: BASELINE AT 2017
df_final['income_17'] = df_master['income_17']
df_final['hptai_17'] = df_master['hptai_17']
df_final['har_17'] = df_master['har_17']
df_final['har_24'] = df_master['har_24']
df_final['delta_har'] = df_master['har_24'] - df_master['har_17']

# eliminate those LSOA which has less than 5 property transactions
df_final = df_final[(df_final['vol_24'] >= 5) & (df_final['vol_17'] >= 5)].copy()

# if room is a studio, num_rms might be zero and avg_rm_area could be inf
df_final.replace([np.inf, -np.inf], np.nan, inplace=True)

# drop NaN values, which may cause errors in LASSO
print("True if there are NaN values:", df_final.isna().any().any())
if df_final.isna().any().any():
    print('Rows with NaN are deleted.')
    df_final = df_final.dropna()

# see final dimensions
print(f'df_final dataset has {len(df_final)} rows and {len(df_final.columns)} columns.')

#=========================================
# SAVE TO CSV
#=========================================
PARENT_DIR = os.path.dirname(BASE_DIR)
ANALYSIS_DIR = os.path.join(PARENT_DIR, 'data_analysis')
os.makedirs(ANALYSIS_DIR, exist_ok = True)

SAVE_PATH_ALL = os.path.join(ANALYSIS_DIR, 'final_london_data.csv')
df_final.to_csv(SAVE_PATH_ALL, index = False)
print(f'File saved to {SAVE_PATH_ALL}.')

SAVE_PATH_17 = os.path.join(ANALYSIS_DIR, 'final_17_london_data.csv')
df_master_17.to_csv(SAVE_PATH_17, index = False)
print(f'File saved to {SAVE_PATH_17}.')

SAVE_PATH_24 = os.path.join(ANALYSIS_DIR, 'final_24_london_data.csv')
df_master_24.to_csv(SAVE_PATH_24, index = False)
print(f'File saved to {SAVE_PATH_24}.')