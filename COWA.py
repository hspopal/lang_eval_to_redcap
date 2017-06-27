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

missing_cowa = []

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

    # COWA

    if 'COWA' in sprdshts:
        cowa = pd.read_excel(file, 'COWA', skiprows=2)
        cowa_headers = cowa.loc[1].tolist()

        if cowa.empty:
            missing_cowa.append(file)
        else:
            temp_df = cowa.dropna()
            temp_df['f'] = cowa['F'].str.extract('(.*)', expand=True)
            temp_df['a'] = cowa['A'].str.extract('(.*)', expand=True)
            temp_df['s'] = cowa['S'].str.extract('(.*)', expand=True)
            temp_df['animals'] = (cowa['animals'].
                                  str.extract('(.*)', expand=True))
            temp_df['vegetables'] = (cowa['vegetables']
                                     .str.extract('(.*)', expand=True))

            F = temp_df['f'].tolist()
            A = temp_df['a'].tolist()
            S = temp_df['s'].tolist()
            animals = temp_df['animals'].tolist()
            vegetables = temp_df['vegetables'].tolist()

            scores_df = cowa.dropna()
            scores_df['f'] = cowa['F'].str.extract('(\d)', expand=True)
            F_score = scores_df['F'].tolist()
            A_score = scores_df['A'].tolist()
            S_score = scores_df['S'].tolist()
            animals_score = scores_df['animals'].tolist()
            vegetables_score = scores_df['vegetables'].tolist()

            temp_list = [F, A, S, animals, vegetables]
            cowa_df = pd.DataFrame([temp_list])

    else:
        missing_cowa.append(file)
