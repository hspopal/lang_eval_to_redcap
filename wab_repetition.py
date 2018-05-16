import pandas as pd
import csv
import numpy as np
import re
import glob

import os
import fnmatch
from datetime import datetime

def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

# Capture all subject lang files
# Skip spreadsheets that have errors for missing tabs, or ill formatted headers
# Create a seperate list for each error with failed subjects/files


###############################################################################
# Define relevant paths and variables
work_dir = os.path.expanduser('~/Dropbox (Partners HealthCare)/Haroon/projects/lang_eval_to_redcap-alexs')
lang_files_dir = os.path.expanduser('/Volumes/aphasia$/Patients/')
#lang_files_dir = os.path.expanduser('/Users/AXS97/Desktop/lang_eval_to_redcap-alexs/Patients/')
os.chdir(work_dir)

lang_files = find('*.xls*', lang_files_dir+'PPA/LastNameA_F')
lang_files = lang_files + (find('*.xls*', lang_files_dir+'PPA/LastNameG_M'))
lang_files = lang_files + (find('*.xls*', lang_files_dir+'PPA/LastNameN_Z'))
lang_files = lang_files + (find('*.xls*', lang_files_dir+'PCA patients (put copies of lang summaries in dropbox)/LastNameA_F'))
lang_files = lang_files + (find('*.xls*', lang_files_dir+'PCA patients (put copies of lang summaries in dropbox)/LastNameG_M'))
lang_files = lang_files + (find('*.xls*', lang_files_dir+'PCA patients (put copies of lang summaries in dropbox)/LastNameN_Z'))
for file in lang_files[:]:
    if '~$' in file:
        lang_files.remove(file)
data = []

# cols will be used to build dataframe off of specific Redcap headers
cols = pd.read_csv(work_dir + '/' + glob.glob('DickersonMasterEnrollment_ImportTemplate_*.csv')[0])
#redcap_cols = filter(lambda k: 'csbwpm' in k, cols)
###############################################################################

count = 0

date_error = []

total_wab_rep = [] # 231
empty_wab_rep = []
missing_wab_repetition = [] # 62
wab_rep_error = [] # 0

all_test = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file
    
    if '/.' in file:  # If file is a hidden file, skip
        continue

    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names

    # WAB Repitition
    if 'WAB Repetition' in sprdshts:
        single_test = pd.DataFrame()

        total_wab_rep.append(file)
        wab_rep = pd.read_excel(file, 'WAB Repetition', skiprows=1)
        wab_rep_notNaN = wab_rep[~pd.isnull(wab_rep['Unnamed: 0'])]
        wab_rep_headers = []
        for n in range(1, 16): # create headers
            wab_rep_headers.append('wab_repetition_'+str(n))
            wab_rep_headers.append('wab_repetition_'+str(n)+'_vrbtm')
            wab_rep_headers.append('wab_repetition_'+'notes_'+str(n))

        # Find subject's name from file path
        path_split = file.split('/')
        idx = path_split.index([i for i in path_split if i.startswith('LastName')][0])
        single_test['Subject'] = []
        """found = ''
        m = re.search(lang_files_dir + 'LastNameA_F/(.+?)/', file)
        if m:
            found = m.group(1)
        m = re.search(lang_files_dir + 'LastNameG_M/(.+?)/', file)
        if m:
            found = m.group(1)
        m = re.search(lang_files_dir + 'LastNameN_Z/(.+?)/', file)
        if m:
            found = m.group(1)"""
        single_test.ix[0, 'Subject'] = path_split[idx+1]
        
        # find date searching through different types of formats
        date = re.findall('\d\d\d\d\d\d+', file)
        #date = date[0]
        if not date:
            date = ''
        else:
            date = datetime.strptime(date[0], '%m%d%y')
            date = date.strftime('%Y-%m-%d')
 
        if date == '':
            date_error.append(file)
            continue
        single_test['Date'] = date
        
        if single_test.ix[0, 'Date'] == '':
            date_error.append(file)
            continue
        if wab_rep_notNaN.empty:
            empty_wab_rep.append(file)
        else:
        
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
                temp_items.append('')
    
            temp_df = pd.DataFrame([temp_items], columns=wab_rep_headers)
            single_test = pd.concat([single_test, temp_df], axis=1)
            if len(single_test.columns) < 3:
                wab_rep_error.append(file)
        all_test = all_test.append(single_test)

    else:
        missing_wab_repetition.append(file)
    


    #wab_rep_patients = pd.DataFrame()
    #wab_rep_patients = all_test.groupby(all_test['Subject'].tolist(),as_index=False).size() # 104 out of 126 total

all_test = all_test.drop_duplicates(['Subject', 'Date'])
all_test.to_csv('dataframe_output/wab_repetition.csv', encoding='utf-8', index=False)

no_wab_rep = len(missing_wab_repetition)
captured = (len(total_wab_rep))
empty = len(empty_wab_rep)
correct = (len(total_wab_rep)-len(wab_rep_error))
error = len(wab_rep_error)

