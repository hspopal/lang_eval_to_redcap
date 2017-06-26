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

lang_files = find('*.xls', work_dir + '/Patients/')
# lang_files = [work_dir +
# '/Patients/LastNameA_F/Adamian_Daniel'
# '/010815/adamian_lang_010815.xls']

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

raw_ID = []

ID_error_firstname = []
ID_error_lastname = []
ID_error_date = []

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
    sprdshts = xl.sheet_names

    date = str(file[-10:-4])

    raw = str(file[67:])
    raw_ID.append(raw)

ID = pd.DataFrame(raw_ID, columns=['raw'])
ID['first_name'] = ID['raw'].str.extract('/.+?_(.*)/\d', expand=True)
if ID['first_name'].isnull:
    ID_error_firstname.append(file)
else:
    ID['first_initial'] = ID['first_name'].astype(str).str[0]
    ID['last_name'] = ID['raw'].str.extract('/(.*)_.+?/\d', expand=True)
    if ID['last_name'].isnull:
        ID_error_lastname.append(file)
    else:
        ID['date'] = ID['raw'].str.extract('/(\d\d\d\d\d\d)/', expand=True)
        if ID['date'].isnull:
            ID_error_date.append(file)
        else:
            ID_lower = ID['first_initial'] + (ID['last_name'].astype
                                              (str).str[:3] + '_' + ID
                                              ['date'])
            ID['ID'] = ID_lower.str.upper()
