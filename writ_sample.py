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
redcap_cols = pd.read_csv(work_dir + '/redcap_headers.csv')

single_test = pd.DataFrame()
count = 0

missing_transcr = []
transcr_response_error = []

missing_writ_sample = []
sample_error = []

all_trans = pd.DataFrame()

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

    # Language Transcription

    if 'Writing Samples' in sprdshts:
        writ_sample = pd.read_excel(file, 'Writing Samples', header=None)

        if writ_sample.empty:
            missing_writ_sample.append(file)
        else:
            sample_items = writ_sample.index.tolist()

            writ_clear = writ_sample.fillna('')
            writ_clear = writ_clear.drop(writ_clear.columns[0], axis=1)

            if writ_clear.empty:
                missing_writ_sample.append(file)

            else:
                mask = np.column_stack(
                                        [writ_clear[col].str.startswith
                                            (r"1.", na=False) for
                                            col in writ_clear])
                response1 = writ_clear.loc[mask.any(axis=1)]
                if '2.' or '3.' or '4.' in response1:
                    sample_error.append(file)

                mask = np.column_stack(
                                        [writ_clear[col].str.startswith
                                            (r"2.", na=False) for
                                            col in writ_clear])
                response2 = writ_clear.loc[mask.any(axis=1)]
                if '1.' or '3.' or '4.' in response2:
                    sample_error.append(file)

                mask = np.column_stack(
                                        [writ_clear[col].str.startswith
                                            (r"3.", na=False) for
                                            col in writ_clear])
                response3 = writ_clear.loc[mask.any(axis=1)]
                if '1.' or '2.' or '4.' in response3:
                    sample_error.append(file)

                mask = np.column_stack(
                                        [writ_clear[col].str.startswith
                                            (r"4.", na=False) for
                                            col in writ_clear])
                response4 = writ_clear.loc[mask.any(axis=1)]
                if '1.' or '2.' or '3.' in response4:
                    sample_error.append(file)

                sample = ['', '', '', '', '']
                if '1.' in str(response1.iloc[:, -1]):
                    sample[0] = response1.iloc[:, -1]
                if '2.' in str(response2.iloc[:, -1]):
                    sample[1] = response2.iloc[:, -1]
                if '3.' in str(response3.iloc[:, -1]):
                    sample[2] = response3.iloc[:, -1]
                if '4.' in str(response4.iloc[:, -1]):
                    sample[3] = response4.iloc[:, -1]

                trans_df = pd.DataFrame(data=[sample],
                                        columns=[col for col in
                                        redcap_cols.columns
                                        if '' in col])
                single_test = pd.concat([single_test, trans_df], axis=1)

    else:
        missing_transcr.append(file)

    all_trans = all_trans.append(single_test)
# all_test = pd.concat([all_test], axis=1)
all_trans.to_csv('writ_sample_Final.csv', encoding='utf-8')
