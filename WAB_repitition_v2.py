import pandas as pd
import csv
import numpy as np
import re

import os
import fnmatch

# Capture all subject lang files
# Skip spreadsheets that have errors for missing tabs, or ill formatted headers
# Create a seperate list for each error with failed subjects/files

work_dir = '/Users/axs97/Desktop/lang_eval_to_redcap-alexs'

pd.options.mode.chained_assignment = None

os.chdir(work_dir)
cols = pd.read_csv(work_dir + '/redcap_headers.csv')

'''
def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

lang_files = find('*.xls', work_dir + '/Patients/')
# lang_files = [work_dir +
# '/Patients/LastNameA_F/Adamian_Daniel
# /010815/adamian_lang_010815.xls']

data = []

# cols will be used to build dataframe off of specific Redcap headers
cols = pd.read_csv(work_dir + '/redcap_headers.csv')

single_test = pd.DataFrame()
count = 0

missing_bnt30 = []
missing_wab_commands = []
missing_wab_repetition = []
missing_wab_reading = []

header_error_bnt30 = []
header_error_wab_reading = []

all_test = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file
    single_test = pd.DataFrame()

    # Find subject's name from file path
    single_test['Subject'] = []
    m = re.search(work_dir + '/Patients/LastNameA_F/(.+?)/', file)
    if m:
        found = m.group(1)
    m = re.search(work_dir + '/Patients/LastNameG_M/(.+?)/', file)
    if m:
        found = m.group(1)
    m = re.search(work_dir + '/Patients/LastNameN_Z/(.+?)/', file)
    if m:
        found = m.group(1)
    single_test.ix[0, 'Subject'] = found

    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names

    # WAB Repitition
    if 'WAB Repetition' in sprdshts:
'''
txt = pd.read_table(work_dir + '/filepath.txt')
file_ = txt.columns.tolist()
file = file_[0]
single_test = pd.DataFrame()

wab_rep = pd.read_excel(file, 'WAB Repetition', skiprows=1, encoding='utf-8')
#wab_rep = wab_rep.encode('ascii', 'ignore')

wab_rep_notNaN = wab_rep[~pd.isnull(wab_rep['Unnamed: 0'])]
wab_rep_headers = []
for n in range(1, 16):
    wab_rep_headers.append('wab_repetition_'+str(n))
    wab_rep_headers.append('wab_repetition_'+str(n)+'_vrbtm')

temp_items = []
wab_rep_notNaN['Verbatim response if incorrect'] = (wab_rep_notNaN
                                                    ['Verbatim response '
                                                     'if incorrect']
                                                    .replace(np.nan,
                                                             '',
                                                             regex=True
                                                             ))
for n in range(0, 15):
    temp_items.append(wab_rep_notNaN['Score'][n])
    temp_items.append(wab_rep_notNaN
                      ['Verbatim response if incorrect'][n])

temp_df = pd.DataFrame([temp_items], columns=wab_rep_headers)
single_test = pd.concat([single_test, temp_df], axis=1)
single_test.to_csv(work_dir + 'wab_rep_test.csv', encoding='utf-8')

'''
else:
    missing_wab_repetition.append(file)
'''
