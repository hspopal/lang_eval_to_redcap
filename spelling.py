import pandas as pd
import csv
import numpy as np
import re
import glob

import os
import fnmatch
from datetime import datetime
import matplotlib.pyplot as plt

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
    if '~$' in file or '/.' in file:
        lang_files.remove(file)
data = []

# cols will be used to build dataframe off of specific Redcap headers
cols = pd.read_csv(work_dir + '/' + glob.glob('DickersonMasterEnrollment_ImportTemplate_*.csv')[0])
redcap_cols = cols.columns.tolist()
redcap_cols = filter(lambda k: 'spelling_' in k, cols)
###############################################################################


single_test = pd.DataFrame()

spelling_total = []
missing_spelling = []
spelling_header_error = [] # header error
empty_spelling = []
date_error = []

spelling_df = pd.DataFrame()
all_test = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names    
    
    # spelling

    if 'Spelling' in sprdshts:
        spelling_total.append(file)
        #spelling = pd.read_excel(file, 'spelling', skiprows=2)
        spelling = xl.parse('Spelling', skiprows=4, index_col=None, na_values=['NA'])
        if len(spelling) > 20 or len(spelling) < 10:
            spelling_header_error.append(file)
            continue
        spelling = spelling.drop(['Unnamed: 0','Unnamed: 1'], axis=1)
        #spelling = spelling.dropna(subset=['From the BDAE', 
        #'correct/incorrect (0/1)', 'response if incorrect'], how='all')
        #spelling = spelling.reset_index(drop=True)
        #spelling_headers = spelling.loc[0].tolist()
        
        single_test = pd.DataFrame(columns=redcap_cols)
                
        # Find subject's name from file path
        path_split = file.split('/')
        idx = path_split.index([i for i in path_split if i.startswith('LastName')][0])
        single_test['Subject'] = []
        #m = re.search(lang_files_dir + 'LastNameA_F/(.+?)/', file)
        #if m:
        #    found = m.group(1)
        #m = re.search(lang_files_dir + 'LastNameG_M/(.+?)/', file)
        #if m:
        #    found = m.group(1)
        #m = re.search(lang_files_dir + 'LastNameN_Z/(.+?)/', file)
        #if m:
        #    found = m.group(1)
        #single_test.ix[0, 'Subject'] = found
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
       
        temp_df = spelling.dropna(axis=0, how='all')
        temp_df = temp_df.reset_index(drop=True)

        if temp_df.empty:
            empty_spelling.append(file)
        # Check to see if correct column headers are in spreadsheet
        elif not set(['From the BDAE','correct/incorrect (0/1)','response if incorrect']).issubset(temp_df.columns):
            spelling_header_error.append(file)
        else:
            for i in range(len(temp_df)):
                item = temp_df['From the BDAE'].astype(str).iloc[i].split()[0].lower()
                if type(temp_df['correct/incorrect (0/1)'].iloc[i]) == str or type(temp_df['correct/incorrect (0/1)'].iloc[i]) == unicode:
                    single_test['spelling_'+item+'_notes'] = temp_df['correct/incorrect (0/1)'].iloc[i]
                elif 'spelling_'+item in redcap_cols:
                    single_test['spelling_'+item] = temp_df['correct/incorrect (0/1)'].iloc[i]
                    single_test['spelling_'+item] = single_test['spelling_'+item].replace(1.0, '1')
                    single_test['spelling_'+item] = single_test['spelling_'+item].replace(0.0, '0')
                    single_test['spelling_'+item+'_error'] = temp_df['response if incorrect'].iloc[i]
                if 'Unnamed: 2' in temp_df.columns:
                    single_test['spelling_'+item+'_notes'] = temp_df['Unnamed: 2'].iloc[0]
                    
            #single_test['spelling_date'] = date
            
            all_test = all_test.append(single_test)
            
#all_test = all_test.drop(['spelling_nan','spelling_nan_error',"spelling_couldn't",
#                          "spelling_couldn't_error",'spelling_percent:','spelling_percent:_error'], axis=1)

# Replace extra column grab from spreadsheets to general notes column
all_test['spelling_gen_notes'] = all_test['spelling_nan_notes']
all_test = all_test.drop('spelling_nan_notes', 1)

all_test.to_csv('dataframe_output/spelling.csv', encoding='utf-8', index=False)
            
            
            
            