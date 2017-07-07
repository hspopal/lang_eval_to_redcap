import pandas as pd
import csv
import numpy as np
import re

import os
import fnmatch

work_dir = '/Users/axs97/Desktop/lang_eval_to_redcap-alexs'
os.chdir(work_dir)

# import tests (bnt30, lang_trans)

bnt30_test = pd.read_csv(work_dir + '/BNT30-FINAL.csv', encoding='utf-8')
lang_trans_test = pd.read_csv(work_dir + '/Lang_trans_final.csv', encoding='utf-8')
wab_rep_test = pd.read_csv(work_dir + '/wab_rep_final.csv', encoding='utf-8')

for i in bnt30_test.index:
    if pd.isnull(bnt30_test['Date'].loc[i]):
        bnt30_test = bnt30_test.drop([i])
for n in lang_trans_test.index:
    if pd.isnull(lang_trans_test['Date'].loc[n]):
        lang_trans_test = lang_trans_test.drop([n])
for m in wab_rep_test.index:
    if pd.isnull(wab_rep_test['Date'].loc[m]):
        wab_rep_test = wab_rep_test.drop([m])

# match tests into one 'master'

match_test = pd.merge(bnt30_test, lang_trans_test, on=['Subject', 'Date'], how='inner')
match_test = pd.merge(match_test, wab_rep_test, on=['Subject', 'Date'], how='inner')

match_test.to_csv('match_test.csv', encoding='utf-8')

# Load Redcap csv as a dataframe

redcap_df = pd.read_csv(work_dir + '/DickersonMasterEnrol_DATA_2017-06-29_1050.csv')

# Create a column for IDs in Redcap df that match lang spreadsheet IDs (can just be first and last name)

redcap_df['Subject'] = redcap_df["name_last"].map(str) + '_' + redcap_df["name_first"]

# pull only relevant columns
## redcap_id, event, bnt30, wab, etc.

relevant_columns = ['Subject', 'redcap_event_name']
for col in redcap_df.columns:
    if 'bnt30' in col:
        relevant_columns.append(col)
    if 'lang_transcr' in col:
        relevant_columns.append(col)
    if 'wab_repitition' in col:
        relevant_columns.append(col)

redcap_relevant = redcap_df[relevant_columns]
redcap_relevant.to_csv('redcap_test.csv', encoding='utf-8')

# Match lang spreadsheets to Redcap
match_final = pd.merge(redcap_relevant, match_test, on=['Subject'], how='inner')

match_final.to_csv('match_final.csv', encoding='utf-8')


"""
#examples
match_mrn = pd.merge(redcap_relevant, epic_nodups, on=['id_mrn'], how='inner')
#match_mrn = pd.merge(redcap_relevant, epic_report, how='inner', left_on=['email_address', 'match_id'], right_on=['email_address', 'match_id'])
match_id = pd.merge(redcap_relevant, epic_nodups, on=['match_id'], how='inner')
#match = pd.merge(redcap_report, epic_report, on=['id_mrn', 'match_id'], how='inner')
no_match_mrn = epic_nodups[~epic_nodups['id_mrn'].isin(match_mrn['id_mrn'])]
no_match_id = epic_nodups[~epic_nodups['match_id'].isin(match_id['match_id'])]
"""









