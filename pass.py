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
redcap_cols = filter(lambda x: x.startswith('pass_'), cols)
redcap_cols = redcap_cols[83:]
###############################################################################


single_test = pd.DataFrame()

pass_total = []
pass_header_error = [] # header error
missing_data = []
date_error = []

pass_df = pd.DataFrame()
all_test = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file
    
    if '/.' in file:  # If file is a hidden file, skip
        continue
    
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names    
    
    # pass

    if 'PASS' in sprdshts:
        pass_total.append(file)
        #pass = pd.read_excel(file, 'pass', skiprows=19)
        pass_ = xl.parse('PASS', skiprows=4, index_col=None, na_values=['NA'])
        #pass_ = pass_.replace(np.nan, '', regex=True)
        #if len(pass) > 20 or len(pass) < 10:
        #    pass_header_error.append(file)
        #    continue
        
        # Remove irrelevant headers
        remove_cols = ['pass_summary_date', 'pass_summary_rater_1', 
                       'pass_summary_artic_1', 'pass_survey_complete', 
                       'pass_survey_soc_comments']
        for item in remove_cols:
            if item in redcap_cols:
                redcap_cols.remove(item)
        #if  redcap_cols.remove('pass_summary_date')
        #redcap_cols.remove('pass_summary_rater_1')
        #redcap_cols.remove('pass_summary_artic_1')
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
        
        if not 'PASS ratings:' in pass_.columns:
            pass_header_error.append(file)
            continue
            
        pass_ = pass_[pass_['PASS ratings:'].str.contains("NaN") == False]
        pass_ = pass_[pass_['PASS ratings:'].str.contains("Supplemental:") == False]
        pass_ = pass_.dropna(axis='index',how='all')
        pass_ = pass_.replace(np.nan, '', regex=True)
        
        single_test['pass_rater_1'] = str(pass_.columns[1]).split("rater 1: ",1)[-1]
        
        # Get score and notes for first rater
        notes = list()
        if not isinstance(pass_.iloc[:,-1].name, datetime) and any([item.startswith('rater 1') for item in pass_.columns]) and not pass_.iloc[:,1].isnull().all():
            rater1_col = [s for s in pass_.columns if 'rater 1' in s.lower()][0]
        for n in range(len(pass_)):
            #if str(pass_[pass_.columns[1]].str.split(' ', 1, expand=True).iloc[n,0]) <> 'None' and str(pass_[pass_.columns[1]].str.split(' ', 1, expand=True).iloc[n,0]) <> 'nan':    
            if len(pass_[rater1_col].astype(str).str.split(' ', 1, expand=True).columns) > 1:  # Does cell contain score and note
                single_test[single_test.columns[n+4]].iloc[0] = str(pass_[rater1_col].astype(str).str.split(' ', 1, expand=True).iloc[n,0])  # Grab score
                if str(pass_[rater1_col].astype(str).str.split(' ', 1, expand=True).iloc[n,0]) not in [np.nan,'nan','None',None,'']:  # Grabe note if present
                    note = single_test.columns[n+4]+' note: '+str(pass_[rater1_col].astype(str).str.split(' ', 1, expand=True).iloc[n,1])
                    if 'None' not in note:
                        notes.append(note)
                    single_test['pass_r1_comm'] = '; '.join(notes)
            else:
                single_test[single_test.columns[n+4]].iloc[0] = pass_.iloc[n,1]
        
        # Get score and notes for second rater, if there was one
        if not isinstance(pass_.iloc[:,-1].name, datetime) and any([item.startswith('rater 2') for item in pass_.columns]) and not pass_.iloc[:,2].isnull().all():
            rater2_col = [s for s in pass_.columns if 'rater 2' in s.lower()][0]
            if str(rater2_col).split("rater 2: ",1)[-1] <> 'rater 2:':
                single_test['pass_rater_2'] = str(rater2_col).split("rater 2: ",1)[-1]
            for n in range(len(pass_)):
                if len(pass_[rater2_col].astype(str).str.split(' ', 1, expand=True).columns) > 1:
                    if type(pass_[rater2_col].iloc[n]) in [int,float]:
                        single_test[single_test.columns[n+21]].iloc[0] = str(pass_[rater2_col].astype(str).str.split(' ', 1, expand=True).iloc[n,0])
                    elif str(pass_[rater2_col].astype(str).str.split(' ', 1, expand=True).iloc[n,0]) not in [np.nan,'nan','None',None,'']:
                        note = single_test.columns[n+21]+' note: '+str(pass_[rater2_col].astype(str).str.split(' ', 1, expand=True).iloc[n,1])
                        notes.append(note)
                        single_test['pass_r2_comm'] = '; '.join(notes)
                else:
                    single_test[single_test.columns[n+21]].iloc[0] = pass_.iloc[n,2]
                    
        # Get consensus information
        #if len(pass_.columns) > 3:
        #    print file
        if not isinstance(pass_.iloc[:,-1].name, datetime) and any(['consensus' in item.lower() or 'final' in item.lower() for item in pass_.columns]) and not pass_.iloc[:,2].isnull().all():
            cons_col = [s for s in pass_.columns if 'final' in s.lower()]
            if cons_col == []:
                cons_col = [s for s in pass_.columns if 'consensus' in s.lower()]
            cons_col = cons_col[0]
            for n in range(len(pass_)):
                if len(pass_[str(cons_col)].astype(str).str.split(' ', 1, expand=True).columns) > 1:
                    if type(pass_[str(cons_col)].iloc[n]) in [int,float]:
                        single_test[single_test.columns[n+38]].iloc[0] = str(pass_[str(cons_col)].astype(str).str.split(' ', 1, expand=True).iloc[n,0])

        if single_test.drop(['Subject','Date','pass_rater_1'], axis=1).empty:
            missing_data = missing_data.append(single_test) 
        all_test = all_test.append(single_test)


all_test = all_test.replace(u'\u2019', "'")   

# Change for strings to be in correct Redcap field value
all_test = all_test.replace('n/a', 'na')   
all_test = all_test.replace('not administered', 'na')
all_test = all_test.replace('not assessed', 'na') 
all_test.to_csv('dataframe_output/pass.csv', index=False, encoding='utf-8')
            
            
            
            