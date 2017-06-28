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

missing_CSB_WPM = []

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

    # CSB
    if 'CSB WPM' in sprdshts:
        csb = pd.read_excel(file, 'CSB WPM',
                            skiprows=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                      11, 12, 13, 14, 19,
                                      23, 27,
                                      31, 35,
                                      39, 43])
                                      
        headers = ['none', '1', '2', '3', '4', '5', '6', '7', '8',
                   'none2', 'none3']

        csb.columns = headers

        csb_clear = csb.drop(['none2', 'none3', 'none'], axis=1)
        
        d_animals = csb_clear.iloc[[0, 1, 2],:].reset_index()
        f_animals = csb_clear.iloc[[3, 4, 5],:].reset_index()
        birds = csb_clear.iloc[[6, 7, 8],:].reset_index()
        fruits = csb_clear.iloc[[9, 10, 11],:].reset_index()
        vehicles = csb_clear.iloc[[12, 13, 14],:].reset_index()
        l_house_obj = csb_clear.iloc[[15, 16, 17],:].reset_index()
        h_house_obj = csb_clear.iloc[[18, 19, 20],:].reset_index()
        tools = csb_clear.iloc[[21, 22, 23],:].reset_index()

        csb_all = pd.DataFrame()
        csb_types = [d_animals, f_animals, birds, fruits, vehicles, l_house_obj, h_house_obj, tools]
        for i in csb_types:
            for x in i.columns:
                temp_list = ['', '', '']
                temp_list[0] = i.loc[0][x]
                if i.loc[1][x] == 1:
                    temp_list[1] = 'correct'
                elif i.loc[1][x] == 0:
                    temp_list[1] = 'incorrect'
                    temp_list[2] = i.loc[2][x]

                type_df = pd.DataFrame([temp_list])  # ,
                                   # columns=[col for col in cols.columns
                                            # if 'bnt30' in col and
                                            # '_'+str(i) in col[-2:]])
                single_test = pd.concat([single_test,
                                         type_df], axis=1)
