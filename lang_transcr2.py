import pandas as pd
import csv
import numpy as np
import re

import os
import fnmatch
from datetime import datetime

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

lang_files = find('*.xls', work_dir + '/Patients/')
# lang_files = [work_dir +
# '/Patients/LastNameA_F/Ciccariello_Mary
# /022416/lang_eval_MC_022416.xls']

data = []

# cols will be used to build dataframe off of specific Redcap headers
redcap_cols = pd.read_csv(work_dir + '/redcap_headers.csv')

single_test = pd.DataFrame()
count = 0
date_error = []

missing_transcr = []
transcr_response_error = []

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

    match = re.search(r'(\d\d\d\d\d\d)/', file)
    if match is None:
        date_error.append(file)
        #single_test.ix[1, 'Date'] = str(file[-10:-4])
        single_test.ix[0, 'Date'] = str("")
    else:
        date = datetime.strptime((match.group())[:-1], '%m%d%y').date()
        single_test.ix[0, 'Date'] = str(date)

    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names

    # Language Transcription

    if 'Lang transcriptions' in sprdshts:
        lang_trans = pd.read_excel(file, 'Lang transcriptions', header=None)

        if lang_trans.empty:
            missing_transcr.append(file)
        else:
            lang_items = lang_trans.index.tolist()

            trans_clear = lang_trans.fillna('')
            trans_clear = trans_clear.drop(trans_clear.columns[0], axis=1)

            if trans_clear.empty:
                missing_transcr.append(file)

            else:
                mask = np.column_stack(
                                        [trans_clear[col].str.startswith
                                            (r"1.", na=False) for
                                            col in trans_clear])
                response1 = trans_clear.loc[mask.any(axis=1)]
                if '2.' or '3.' or '4.' or '5.' or '6.' in response1:
                    transcr_response_error.append(file)

                mask = np.column_stack(
                                        [trans_clear[col].str.startswith
                                            (r"2.", na=False) for
                                            col in trans_clear])
                response2 = trans_clear.loc[mask.any(axis=1)]
                if '1.' or '3.' or '4.' or '5.' or '6.' in response2:
                    transcr_response_error.append(file)

                mask = np.column_stack(
                                        [trans_clear[col].str.startswith
                                            (r"3.", na=False) for
                                            col in trans_clear])
                response3 = trans_clear.loc[mask.any(axis=1)]
                if '1.' or '2.' or '4.' or '5.' or '6.' in response3:
                    transcr_response_error.append(file)

                mask = np.column_stack(
                                        [trans_clear[col].str.startswith
                                            (r"4.", na=False) for
                                            col in trans_clear])
                response4 = trans_clear.loc[mask.any(axis=1)]
                if '1.' or '2.' or '3.' or '5.' or '6.' in response4:
                    transcr_response_error.append(file)

                mask = np.column_stack(
                                        [trans_clear[col].str.startswith
                                            (r"5.", na=False) for
                                            col in trans_clear])
                response5 = trans_clear.loc[mask.any(axis=1)]
                if '1.' or '2.' or '3.' or '4.' or '6.' in response5:
                    transcr_response_error.append(file)

                mask = np.column_stack(
                                        [trans_clear[col].str.startswith
                                            (r"6.", na=False) for
                                            col in trans_clear])
                response6 = trans_clear.loc[mask.any(axis=1)]
                if '1.' or '2.' or '3.' or '4.' or '5.' in response6:
                    transcr_response_error.append(file)

                transcription = ['', '', '', '', '', '', '']
                if '1.' in str(response1.iloc[:, -1]):
                    transcription[0] = response1.iloc[:, -1]
                if '2.' in str(response2.iloc[:, -1]):
                    transcription[1] = response2.iloc[:, -1]
                if '3.' in str(response3.iloc[:, -1]):
                    transcription[2] = response3.iloc[:, -1]
                if '4.' in str(response4.iloc[:, -1]):
                    transcription[3] = response4.iloc[:, -1]
                if '5.' in str(response5.iloc[:, -1]):
                    transcription[4] = response5.iloc[:, -1]
                if '6.' in str(response6.iloc[:, -1]):
                    transcription[5] = response6.iloc[:, -1]

                trans_df = pd.DataFrame(data=[transcription],
                                        columns=[col for col in
                                        redcap_cols.columns
                                        if 'lang_transcr_' in col])
                single_test = pd.concat([single_test, trans_df], axis=1)

    else:
        missing_transcr.append(file)

    all_trans = all_trans.append(single_test)
# all_test = pd.concat([all_test], axis=1)
all_trans.to_csv('Lang_trans_Final.csv', encoding='utf-8')
