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

missing_ppt = []
header_error_ppt = []

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

    # PPT
    if 'PPT' in sprdshts:
        ppt = pd.read_excel(file, 'PPT', skiprows=[1, 2, 3, 4])

        relevant_headers = [
            'version:',
            '3 pictures',
            '3 written words',
            '1 written word, 2 pictures',
            '1 picture, 2 written words',
            '1 spoken word, 2 pictures',
            '1 spoken word, 2 written words'
            ]

        temp_head_errors = []

        if ppt.empty:
            missing_spelling.append(file)
        else:
            ppt_clear = ppt.fillna('')
            ppt_clear.columns = relevant_headers
            ppt_items = ppt.index.tolist()

            temp_list = ['', '', '', '', '', '', '']

            # replace first value with correct string
            for i in ppt_items:
                temp_list[0] = ppt_clear.loc[i]['version:']
                if ppt_clear.loc[i]['3 pictures'] == 1:
                    temp_list[1] = 'correct'
                elif ppt_clear.loc[i]['3 pictures'] == 1:
                    temp_list[1] = 'incorrect'

                temp_list[2] = ppt_clear.loc[i]['3 written words']
                temp_list[3] = ppt_clear.loc[i]['1 written word, 2 pictures']
                temp_list[4] = ppt_clear.loc[i]['1 picture, 2 written words']
                temp_list[5] = ppt_clear.loc[i]['1 spoken word, 2 pictures']
                temp_list[6] = (ppt_clear.loc[i]
                                ['1 spoken word, 2 written words'])

                ppt_df = pd.DataFrame([temp_list])  # ,
                                # columns=[col for col in cols.columns
                                            # if 'spelling' in col and
                                            # '_'+str(i) in col[-2:]])

                single_test = pd.concat([single_test, ppt_df], axis=1)
    else:
        missing_spelling.append(file)

all_test = all_test.append(single_test)
all_test.to_csv('PPT-Final.csv', encoding='utf-8')
