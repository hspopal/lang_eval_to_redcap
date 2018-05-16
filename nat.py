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
    if '~$' in file:
        lang_files.remove(file)
data = []

# cols will be used to build dataframe off of specific Redcap headers
cols = pd.read_csv(work_dir + '/' + glob.glob('DickersonMasterEnrollment_ImportTemplate_*.csv')[0])
redcap_cols = cols.columns.tolist()
redcap_cols = filter(lambda k: 'nat_' in k, cols)
redcap_cols = redcap_cols[2:]
###############################################################################


single_test = pd.DataFrame()

nat_total = []
missing_nat = []
nat_header_error = [] # header error
empty_nat = []
date_error = []

nat_df = pd.DataFrame()
all_test = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file
    
    if '/.' in file:  # If file is a hidden file, skip
        continue
    
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names    
    
    # nat

    if 'NAT' in sprdshts:
        nat_total.append(file)
        #nat = pd.read_excel(file, 'nat', skiprows=19)
        nat = xl.parse('NAT', skiprows=19, index_col=None, na_values=['NA'])
        nat = nat.replace(np.nan, '', regex=True)
        #if len(nat) > 20 or len(nat) < 10:
        #    nat_header_error.append(file)
        #    continue
        
        single_test = pd.DataFrame(columns=redcap_cols)
                
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
        
        #if len(nat.columns) != 10:
        #    print file
        if len(nat.columns) < 4:
            nat_header_error = nat_header_error.append(file)
            continue
        
        nat['Unnamed: 0'] = nat['Unnamed: 0'].astype(str).str.split(',')
        
        for n in range(32):
            score = nat.iloc[n][3:9].tolist()
            if 0 in score:  # This if statement series will grad the score
                single_test[single_test.columns[1::3][n]].iloc[0] = 0
            elif 1 in score:
                single_test[single_test.columns[1::3][n]].iloc[0] = 1
            single_test[single_test.columns[2::3][n]].iloc[0] = nat[nat.columns[-1]][n]  # Grab notes
            single_test[single_test.columns[::3][n]].iloc[0] = nat['(errors only)'][n]  # Grab notes
        single_test['nat_30_pass_notes'] = single_test['nat_30_pass_notes'].replace('total:', '', regex=True)
        
        """
        temp_df = nat.dropna(axis=0, how='all')
        temp_df = temp_df.reset_index(drop=True)

        if temp_df.empty:
            empty_nat.append(file)
        # Check to see if correct column headers are in spreadsheet
        elif not set(['From the BDAE','correct/incorrect (0/1)','response if incorrect']).issubset(temp_df.columns):
            nat_header_error.append(file)
        else:
            for i in range(len(temp_df)-1):
                item = temp_df['From the BDAE'].astype(str).iloc[i].split()[0].lower()
                single_test['nat_'+item] = temp_df['correct/incorrect (0/1)'].iloc[i]
                single_test['nat_'+item+'_error'] = temp_df['response if incorrect'].iloc[i]
                if 'Unnamed: 2' in temp_df.columns:
                    single_test['nat_'+item+'_notes'] = temp_df['Unnamed: 2'].iloc[0]
                    
            single_test['nat_date'] = date
            
        """      
        # Check if test is empty besides subject name and date
        single_test = single_test.dropna(thresh=3)
        if single_test.empty:
            empty_nat.append(file)
        else:
            all_test = all_test.append(single_test)


all_test = all_test.replace(u'\u2019', "'")      
all_test.to_csv('dataframe_output/nat.csv', index=False, encoding='utf-8')
            
            
            
            