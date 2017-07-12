import pandas as pd
import csv
import numpy as np
import re
import matplotlib.pyplot as plt

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
date_error = []

# cols will be used to build dataframe off of specific Redcap headers
redcap_cols = pd.read_csv(work_dir + '/redcap_headers.csv')
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

    all_test = all_test.append(single_test)
    all_test = all_test.drop_duplicates(['Subject', 'Date'])

all_test = all_test.sort_index(by=['Subject', 'Date'], ascending=[True, True])
all_test = all_test.reset_index()
all_test = all_test.drop('index', 1)

# trying to do so that script iterates through and at each name finds out how many times the same name has come up before

# solution, transport the sorted df (all_test) to a new one so that a for loop is possible so that it only counts the before names
visitID = pd.DataFrame(columns=['Redcap event'])

for n in all_test.index.tolist():
    row = all_test.loc[[n]]
    visitID = (row).append(visitID)
    name = all_test.loc[n]['Subject']
    visit_num = visitID.Subject.str.contains(name).sum()
    if visit_num == 1:
        visit_num = 'first'
    visitID.loc[n]['Redcap event'] = 'visit_' + str(visit_num)
