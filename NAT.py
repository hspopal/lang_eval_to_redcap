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

missing_nat = []

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

    # NAT
    if 'NAT' in sprdshts:
        nat = pd.read_excel(file, 'NAT', skiprows=[1, 2, 3, 4, 5, 6, 7, 8,
                                                   9, 10, 11, 12, 13, 14, 15,
                                                   16, 17, 18, 19, 52, 53, 54,
                                                   55, 56, 57, 58, 59, 60, 61,
                                                   62, 63])
        headers = ['prompt', 'error word string', 'A', 
                   'P', 'S(Wh)', 'O(Wh)', 'SC', 'OC', '']

        nat.columns = headers

        nat_clear = nat.drop('prompt', axis=1)

        for i in nat_clear.index:
            temp_list = ['', '', '']
            if nat_clear.loc[i]['A'] == 1:
                temp_list[0] = 'Active'
                temp_list[1] = 'correct'
            elif nat_clear.loc[i]['A'] == 0:
                temp_list[0] = 'Active'
                temp_list[1] = 'incorrect'
                temp_list[2] = nat_clear.loc[i]['error word string']

            if nat_clear.loc[i]['P'] == 1:
                temp_list[0] = 'Passive'
                temp_list[1] = 'correct'
            elif nat_clear.loc[i]['P'] == 0:
                temp_list[0] = 'Passive'
                temp_list[1] = 'incorrect'
                temp_list[2] = nat_clear.loc[i]['error word string']

            if nat_clear.loc[i]['S(Wh)'] == 1:
                temp_list[0] = 'Subject-Wh?'
                temp_list[1] = 'correct'
            elif nat_clear.loc[i]['S(Wh)'] == 0:
                temp_list[0] = 'Subject-Wh?'
                temp_list[1] = 'incorrect'
                temp_list[2] = nat_clear.loc[i]['error word string']

            if nat_clear.loc[i]['O(Wh)'] == 1:
                temp_list[0] = 'Object-Wh?'
                temp_list[1] = 'correct'
            elif nat_clear.loc[i]['O(Wh)'] == 0:
                temp_list[0] = 'Object-Wh?'
                temp_list[1] = 'incorrect'
                temp_list[2] = nat_clear.loc[i]['error word string']

            if nat_clear.loc[i]['SC'] == 1:
                temp_list[0] = 'Subject Cleft'
                temp_list[1] = 'correct'
            elif nat_clear.loc[i]['SC'] == 0:
                temp_list[0] = 'Subject Cleft'
                temp_list[1] = 'incorrect'
                temp_list[2] = nat_clear.loc[i]['error word string']

            if nat_clear.loc[i]['OC'] == 1:
                temp_list[0] = 'Object Cleft'
                temp_list[1] = 'correct'
            elif nat_clear.loc[i]['OC'] == 0:
                temp_list[0] = 'Object Cleft'
                temp_list[1] = 'incorrect'
                temp_list[2] = nat_clear.loc[i]['error word string']

            temp_df = pd.DataFrame([temp_list]) #  ,
                                   # columns=[col for col in cols.columns
                                            # if 'bnt30' in col and
                                            # '_'+str(i) in col[-2:]])

            single_test = pd.concat([single_test, temp_df], axis=1)
