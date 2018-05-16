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
total_wab = []
missing_wab_commands = []
missing_data = []

all_test = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file
    found = ''
    single_test = pd.DataFrame()
    
    if '/.' in file:
        continue
    
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names

    # WAB Commands
    if 'WAB commands' in sprdshts:
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
        
        wab_com = pd.read_excel(file, 'WAB commands', skiprows=1)
        wab_com_notNaN = wab_com[~pd.isnull(wab_com['Unnamed: 0'])] # goes to first non-Nan row
        if len(wab_com_notNaN.columns) < 5: # add in 'notes' column if none
            wab_com_notNaN['notes'] = ''
        
        wab_com_headers = ['wab_commands_date', 'wab_hand', 'wab_hand_notes',
                           'wab_eyes', 'wab_eyes_notes', 'wab_point_chair', 'wab_point_chair_notes',
                           'wab_window_door', 'wab_window_door_notes', 'wab_pen_book', 'wab_pen_book_notes',
                           'wab_book_with_pen', 'wab_book_with_pen_notes',
                           'wab_pen_with_book', 'wab_pen_with_book_notes', 'wab_comb_with_pen', 'wab_comb_with_pen_notes',
                           'wab_comb_with_book', 'wab_comb_with_book_notes', 'wab_pen_book_give', 'wab_pen_book_give_notes',
                           'wab_comb_pen_turn_book', 'wab_comb_pen_turn_book_notes', 'wab_comm_gen_notes']
        
        temp_items = [date]
        # for each test prompt, add score and possible note
        wab_com_notNaN = wab_com_notNaN.fillna('')
        for i in wab_com_notNaN.index:
            #if type(wab_com_notNaN['Score'][i]) == np.float64:
            #    wab_com_notNaN['Score'][i] = int(wab_com_notNaN['Score'][i])
            temp_items.append(wab_com_notNaN['Score'][i])
            temp_items.append(wab_com_notNaN.iloc[:,4][i])
        for i in range(len(temp_items)):
            if type(temp_items[i]) == float or type(temp_items[i]) == np.float64:
                temp_items[i] = str(int(temp_items[i]))
        
        temp_items.append('') # add spot for "wab_comm_gen_notes"
        
        temp_df = pd.DataFrame([temp_items],
                               columns=wab_com_headers)
        temp_df = temp_df.astype(str)
        single_test = pd.concat([single_test, temp_df], axis=1)
        
        
        if single_test.drop(['Subject','Date'], axis=1).empty:
            missing_data = missing_data.append(single_test)    
        else:
            all_test = all_test.append(single_test)

    else:
        missing_wab_commands.append(file)
    
    


all_test = all_test.drop('wab_commands_date', 1)
all_test = all_test.drop_duplicates(['Subject', 'Date'])
all_test.to_csv('dataframe_output/wab_commands.csv', encoding='utf-8', index=False)