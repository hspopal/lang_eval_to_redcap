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
              '/Patients/LastNameA_F/Altbach_Edith'
              '/092016/lang_eval_EA_092016.xls']

data = []

# cols will be used to build dataframe off of specific Redcap headers
cols = pd.read_csv(work_dir + '/redcap_headers.csv')

oral_single_test = pd.DataFrame()
ddks_single_test = pd.DataFrame()
aprax_3_single_test = pd.DataFrame()

count = 0

missing_bnt30 = []
missing_wab_commands = []
missing_wab_repetition = []
missing_wab_reading = []

header_error_bnt30 = []
header_error_wab_reading = []

missing_transcr = []
transcr_response_error = []

missing_nat = []

missing_aprax_screen = []

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

    # Aprax screening (oral apraxia)
    if 'Apraxia Screening' in sprdshts:
        aprax_oral = pd.read_excel(file, 'Apraxia Screening',
                                   skiprows=[1, 2, 13, 14, 15,
                                             16, 17, 18, 19, 20,
                                             21, 22, 23, 24, 25,
                                             26, 27, 28])

        headers = ['none', 'stimuli', 'search behav',
                   'notes', 'score']

        aprax_oral.columns = headers

        aprax_oral_clear = aprax_oral.drop(['none', 'stimuli'], axis=1)

        for i in aprax_oral_clear.index:
            temp_list = ['', '', '']
            temp_list[0] = aprax_oral_clear.loc[i]['search behav']
            temp_list[1] = aprax_oral_clear.loc[i]['notes']
            temp_list[2] = aprax_oral_clear.loc[i]['score']

            oral_df = pd.DataFrame([temp_list])  # ,
                                   # columns=[col for col in cols.columns
                                            # if 'bnt30' in col and
                                            # '_'+str(i) in col[-2:]])

            oral_single_test = pd.concat([oral_single_test, oral_df], axis=1)
    else:
        missing_aprax_screen.append(file)

        # Aprax screening (DDks)
    if 'Apraxia Screening' in sprdshts:
        aprax_ddks = pd.read_excel(file, 'Apraxia Screening',
                                   skiprows=[1, 2, 3, 4, 5,
                                             6, 7, 8, 9, 10,
                                             11, 12, 13, 14,
                                             15, 22, 23, 24,
                                             25, 26, 27, 28])

        headers = ['none', 'stimuli', 'response',
                   'notes', 'none2']

        aprax_ddks.columns = headers

        aprax_ddks_clear = aprax_ddks.drop(['none',
                                            'stimuli', 'none2'],
                                           axis=1)

        for i in aprax_ddks_clear.index:
            temp_list = ['', '']
            temp_list[0] = aprax_ddks_clear.loc[i]['response']
            temp_list[1] = aprax_ddks_clear.loc[i]['notes']

            ddks_df = pd.DataFrame([temp_list])  # ,
                                   # columns=[col for col in cols.columns
                                            # if 'bnt30' in col and
                                            # '_'+str(i) in col[-2:]])

            ddks_single_test = pd.concat([ddks_single_test, ddks_df], axis=1)
    else:
        missing_aprax_screen.append(file)

    # Aprax screening (3)
    if 'Apraxia Screening' in sprdshts:
        aprax_3 = pd.read_excel(file, 'Apraxia Screening',
                                skiprows=[1, 2, 3, 4, 5, 6,
                                          7, 8, 9, 10, 11,
                                          12, 13, 14, 15, 16,
                                          17, 18, 19, 20, 21,
                                          22, 23, 24])

        headers = ['none', 'stimuli', 'response',
                   'notes', 'none2']

        aprax_3.columns = headers

        aprax_3_clear = aprax_3.drop(['none', 'stimuli', 'none2'], axis=1)

        for i in aprax_3_clear.index:
            temp_list = ['', '']
            temp_list[0] = aprax_3_clear.loc[i]['response']
            temp_list[1] = aprax_3_clear.loc[i]['notes']

            aprax_3_df = pd.DataFrame([temp_list])  # ,
                                   # columns=[col for col in cols.columns
                                            # if 'bnt30' in col and
                                            # '_'+str(i) in col[-2:]])

            aprax_3_single_test = pd.concat([aprax_3_single_test,
                                             aprax_3_df], axis=1)
    else:
        missing_aprax_screen.append(file)
