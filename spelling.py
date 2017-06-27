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

os.chdir(work_dir)


def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

# lang_files = find('*.xls', work_dir + '/Patients/')
lang_files = [work_dir +
              '/Patients/LastNameA_F/Adamian_Daniel'
              '/010815/adamian_lang_010815.xls']

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

missing_transcr = []
transcr_response_error = []

missing_spelling = []
header_error_spelling = []

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

    # Spelling
    if 'Spelling' in sprdshts:
        spelling = pd.read_excel(file, 'Spelling', skiprows=[1, 2, 3, 4, 5])

        relevant_headers = [
            'words',
            'correct/incorrect (0/1)',
            'response if incorrect'
            ]

        temp_head_errors = []

        if spelling.empty:
            missing_spelling.append(file)
        else:
            spelling_clear = spelling.drop(spelling.
                                           columns[0:2], axis=1).fillna('')
            spelling_clear.columns = relevant_headers
            spelling_items = spelling.index.tolist()

            temp_list = ['', '']

            # replace first value with correct string
            for i in spelling_items:
                if spelling_clear.loc[i]['correct/incorrect (0/1)'] == 1:
                    temp_list[0] = 'correct'
                    temp_list[1] = ''

                elif spelling_clear.loc[i]['correct/incorrect (0/1)'] == 0:
                    temp_list[0] = 'incorrect'
                    temp_list[1] = ((spelling_clear.loc[i]
                                    ['response if incorrect']))
                spelling_df = pd.DataFrame([temp_list])  # ,
                                # columns=[col for col in cols.columns
                                            # if 'spelling' in col and
                                            # '_'+str(i) in col[-2:]])

                single_test = pd.concat([single_test, spelling_df], axis=1)
    else:
        missing_spelling.append(file)

all_test = all_test.append(single_test)
all_test.to_csv('spelling-Final.csv', encoding='utf-8')
