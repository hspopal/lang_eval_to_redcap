import pandas as pd
import csv
import numpy as np
import re

import os
import fnmatch

work_dir = '/Users/axs97/Desktop/lang_eval_to_redcap-alexs'
os.chdir(work_dir)

# import tests (bnt30, lang_trans)
patientID = pd.read_csv(work_dir + '/patientID.csv')
patient_ID = patientID[['Subject', 'Date', 'PatientID']]
master = pd.read_csv(work_dir + '/master.csv', encoding='utf-8')
bnt30_test = pd.read_csv(work_dir + '/BNT30-FINAL.csv', encoding='utf-8')
lang_trans_test = pd.read_csv(work_dir + '/Lang_trans_final.csv', encoding='utf-8')
wab_rep_test = pd.read_csv(work_dir + '/wab_rep_final.csv', encoding='utf-8')
cowa = pd.read_csv(work_dir + '/COWA-final.csv', encoding='utf-8')
wab_comm = pd.read_csv(work_dir + '/WAB_comm.csv', encoding='utf-8')
wab_read_comm = pd.read_csv(work_dir + '/wab_read_comm.csv', encoding='utf-8')
wab_read_comp =pd.read_csv(work_dir + '/wab_read_comp.csv', encoding='utf-8')
writ_sample = pd.read_csv(work_dir + '/writ_sample.csv', encoding='utf-8')
spelling = pd.read_csv(work_dir + '/spelling-Final.csv', encoding='utf-8')
visitID = pd.read_csv(work_dir + '/visitID.csv', encoding='utf-8')

test_list = [bnt30_test, lang_trans_test, wab_rep_test, cowa, wab_comm, wab_read_comm, wab_read_comp, writ_sample, spelling, visitID]

# if no date, drop
for test in test_list:
    for x in test.index:
        if pd.isnull(test['Date'].loc[x]):
            test = test.drop([x])

# match tests into one 'master'
# match_test = pd.merge(master, patient_ID, on=['Subject', 'Date'], how='outer')
match_test = pd.merge(master, bnt30_test, on=['Subject', 'Date'], how='outer')
match_test = pd.merge(match_test, lang_trans_test, on=['Subject', 'Date'], how='outer')
match_test = pd.merge(match_test, wab_rep_test, on=['Subject', 'Date'], how='outer')
match_test = pd.merge(match_test, cowa, on=['Subject', 'Date'], how='outer')
# match_test = pd.merge(match_test, wab_comm, on=['Subject', 'Date'], how='outer')
match_test = pd.merge(match_test, wab_read_comm, on=['Subject', 'Date'], how='outer')
match_test = pd.merge(match_test, wab_read_comp, on=['Subject', 'Date'], how='outer')
match_test = pd.merge(match_test, writ_sample, on=['Subject', 'Date'], how='outer')
# match_test = pd.merge(match_test, spelling, on=['Subject', 'Date'], how='outer')
# match_test = pd.merge(match_test, visitID, on=['Subject', 'Date'], how='outer')

match_test = match_test.drop_duplicates(['Subject', 'Date'])
match_test = match_test.sort_index(by=['Subject', 'Date'], ascending=[True, True])
match_test.to_csv('match_test.csv', encoding='utf-8')

# Load Redcap csv as a dataframe

redcap_df = pd.read_csv(work_dir + '/DickersonMasterEnrol_DATA_2017-07-12_1344.csv')

# Create a column for IDs in Redcap df that match lang spreadsheet IDs (can just be first and last name)

redcap_df['Subject'] = redcap_df["name_last"].map(str) + '_' + redcap_df["name_first"]

# pull only relevant columns
## redcap_id, event, bnt30, wab, etc.

bnt30_col = []
lang_col = []
wab_rep_col = []

# wab command headers do not follow pattern so impossible to find
relevant_columns = ['Subject', 'redcap_event_name']
for col in redcap_df.columns:
    if 'bnt30' in col:
        relevant_columns.append(col)
        bnt30_col.append(col)
    if 'lang_transcr' in col:
        relevant_columns.append(col)
        lang_col.append(col)
    if 'wab_repitition' in col:
        relevant_columns.append(col)
        wab_rep_col.append(col)
    if 'cowa' in col:
        relevant_columns.append(col)
        bnt30_col.append(col)
    if 'wab_read_comm' in col:
        relevant_columns.append(col)
        bnt30_col.append(col)
    if 'wab_read_comp' in col:
        relevant_columns.append(col)
        bnt30_col.append(col)
    if 'writing_samp' in col:
        relevant_columns.append(col)
        bnt30_col.append(col)
    if 'spelling' in col:
        relevant_columns.append(col)
        bnt30_col.append(col)

redcap_relevant = redcap_df[relevant_columns]

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









