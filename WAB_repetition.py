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

# ****** This script does not capture second trys

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
# '/Patients/LastNameA_F/Adamian_Daniel
# /010815/adamian_lang_010815.xls']

data = []

# cols will be used to build dataframe off of specific Redcap headers
cols = pd.read_csv(work_dir + '/redcap_headers.csv')

single_test = pd.DataFrame()
count = 0

date_error = []

missing_bnt30 = []

missing_wab_commands = []

total_wab_rep = [] # 231
missing_wab_repetition = [] # 62
wab_rep_error = [] # 0

missing_wab_reading = []

header_error_bnt30 = []
header_error_wab_reading = []

all_test = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file

    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names

    # WAB Repitition
    if 'WAB Repetition' in sprdshts:
        single_test = pd.DataFrame()

        total_wab_rep.append(file)
        wab_rep = pd.read_excel(file, 'WAB Repetition', skiprows=1)
        wab_rep_notNaN = wab_rep[~pd.isnull(wab_rep['Unnamed: 0'])]
        wab_rep_headers = []
        for n in range(1, 16):
            wab_rep_headers.append('wab_repetition_'+str(n))
            wab_rep_headers.append('wab_repetition_'+str(n)+'_vrbtm')

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
    
        match = re.search(r'/(\d\d\d\d\d\d)/', file)
        if match is None:
            match = re.search(r'(\d\d\d\d\d\d)/', file)
            if match is None:
                match = re.search(r'(\d\d\d\d\d\d).xls', file)
                if match is None:
                    match = re.search(r'(\d\d_\d\d_\d\d)', file)
                    if match is None:
                        match = re.search(r'(\d\d.\d\d.\d\d)', file)
                        if match is None:
                            match = re.search(r'_(\d\d\d\d\d\d)', file)
                            if match is None:
                                date_error.append(file)
                                single_test.ix[0, 'Date'] = ''
                            else:
                                date = datetime.strptime((match.group())[1:], '%m%d%y').date()
                                single_test.ix[0, 'Date'] = str(date)
                        else:
                            date = datetime.strptime((match.group()), '%m.%d.%y').date()
                            single_test.ix[0, 'Date'] = str(date)
                    else:
                        date = datetime.strptime((match.group()), '%m_%d_%y').date()
                        single_test.ix[0, 'Date'] = str(date)
                else:
                    date = datetime.strptime((match.group())[:-4], '%m%d%y').date()
                    single_test.ix[0, 'Date'] = str(date)
            else:
                date = datetime.strptime((match.group())[:-1], '%m%d%y').date()
                single_test.ix[0, 'Date'] = str(date)
        else:
            date = datetime.strptime((match.group())[1:-1], '%m%d%y').date()
            single_test.ix[0, 'Date'] = str(date)
    
        temp_items = []
        wab_rep_notNaN['Verbatim response if incorrect'] = (wab_rep_notNaN
                                                            ['Verbatim response '
                                                             'if incorrect']
                                                            .replace(np.nan,
                                                                     '',
                                                                     regex=True
                                                                     ))
        wab_rep_notNaN = wab_rep_notNaN.reset_index()
        for n in range(0, 15):
            temp_items.append(wab_rep_notNaN['Score'][n])
            temp_items.append(wab_rep_notNaN
                              ['Verbatim response if incorrect'][n])

        temp_df = pd.DataFrame([temp_items], columns=wab_rep_headers)
        single_test = pd.concat([single_test, temp_df], axis=1)
        if len(single_test.columns) < 3:
            wab_rep_error.append(file)

    else:
        missing_wab_repetition.append(file)
    all_test = all_test.append(single_test)
    all_test = all_test.drop_duplicates(['Subject', 'Date'])

    wab_rep_patients = pd.DataFrame()
    wab_rep_patients = all_test.groupby(all_test['Subject'].tolist(),as_index=False).size() # 104 out of 126 total
    
all_test.to_csv('wab_rep_final.csv', encoding='utf-8')
