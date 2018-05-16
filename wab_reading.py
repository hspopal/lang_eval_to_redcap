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
#redcap_cols = cols.columns.tolist()
redcap_cols = filter(lambda k: 'wab_comp' in k, cols)
###############################################################################
count = 0

wab_comp_sent_total = []
missing_wab_comp_sent = [] # file doesnt have wab reading 
head_error_wab_comp_sent = [] # the columns are incorrectly named
empty_wab_read = []
date_error_wab_comp_sent = []


all_test_comp_sent = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file
    
    if '/.' in file:  # If file is a hidden file, skip
        continue
    
    single_test = pd.DataFrame(columns=redcap_cols)
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names
    
    if 'WAB Reading' in sprdshts:
        wab_read = pd.read_excel(file, 'WAB Reading', skiprows=1)
        #print file
        wab_comp_sent_total.append(file)
        # Find subject's name from file path
        path_split = file.split('/')
        idx = path_split.index([i for i in path_split if i.startswith('LastName')][0])
        single_test['Subject'] = []
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
            date_error_wab_comp_sent.append(file)
            continue
        single_test['Date'] = date
            
            
            
        if wab_read.empty:
            empty_wab_read.append(file)
            continue
        wab_comp_sent = pd.read_excel(file, 'WAB Reading', skiprows=1, encoding='utf-8')
        wab_comp_sent = wab_comp_sent.iloc[0:9]
        if not set(['Item #','Score','Patient response if incorrect']).issubset(wab_comp_sent.columns):
            head_error_wab_comp_sent.append(file)
            continue
        wab_comp_sent = wab_comp_sent.drop(['Item #'], axis=1)
        wab_comp_sent = wab_comp_sent.replace(np.nan, '', regex=True)
        if wab_comp_sent.empty:
            missing_wab_comp_sent.append(file)
            continue
        
        for n in range(8):
            single_test['wab_comp_'+str(n+1)] = wab_comp_sent['Score'].iloc[n]
            if wab_comp_sent['Score'].iloc[n] == 0:
                single_test['wab_comp_'+str(n+1)+'_response'] = wab_comp_sent['Patient response if incorrect'].iloc[n]
            """notes = wab_comp_sent.iloc[n][4:].tolist()
            for n in range(len(notes)):
                if isinstance(notes[n], int):
                    notes[n] = str(notes[n])
            notes = [w.replace(u'\u2019', "'") for w in notes]
            notes = [w.replace(u'\xef', "i") for w in notes]
            notes = [str(item) for item in [x for x in notes if x]]
            notes = ', '.join(notes)
            if notes:
                single_test['wab_comp_'+str(n)+'_notes'] = notes"""
        single_test = single_test.replace(np.nan, '', regex=True)
        
    else:
        missing_wab_comp_sent.append(file)
    
    all_test_comp_sent = all_test_comp_sent.append(single_test)
    
    
    
wab_read_total = []
missing_wab_reading = [] # file doesnt have wab reading 
missing_read_comm = [] # the wab reading sheet doesnt have command test 
wab_reading_comm_head_error = [] # the columns are incorrectly named
empty_wab_reading = []
date_error = []

header_error_wab_reading = []

all_test_read = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file
    
    if '/.' in file:  # If file is a hidden file, skip
        continue
    
    single_test = pd.DataFrame()
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names
    
    if 'WAB Reading' in sprdshts:
        wab_read = pd.read_excel(file, 'WAB Reading', skiprows=1)
        #print file
        wab_read_total.append(file)
        # Find subject's name from file path
        path_split = file.split('/')
        idx = path_split.index('PPA')
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
        single_test.ix[0, 'Subject'] = path_split[idx+2]
        
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
        if wab_read.empty:
            empty_wab_reading.append(file)
        else:
            wab_read_comm = pd.read_excel(file, 'WAB Reading', skiprows=15)
            wab_read_comm = wab_read_comm.iloc[0:6]
            if wab_read_comm.empty:
                missing_read_comm.append(file)
            else:
                if len(wab_read_comm.columns) == 6:
                    wab_read_comm['Unnamed: 6'] = ''
                    wab_reading_comm_head_error.append(file)
                else:
                    wab_read_comm_headers = []
                    for n in range(1, 7): # create header list
                        wab_read_comm_headers.append('wab_read_comm_'+str(n)+'_read')
                        wab_read_comm_headers.append('wab_read_comm_'+str(n)+'_perf')
                        wab_read_comm_headers.append('wab_read_comm_'+str(n)+'_notes')
                    temp_items = []
                    if wab_read_comm.columns[2] != 'Reading score earned':
                        wab_reading_comm_head_error.append(file)
                    elif wab_read_comm.columns[4] != 'Perf score earned':
                        wab_reading_comm_head_error.append(file)
                    else:
                        for n in range(0, 6):
                            if type(wab_read_comm['Reading score earned'][n]) == str:
                                temp_items.append("")
                                temp_items.append(wab_read_comm['Perf score earned'][n])
                                temp_items.append(wab_read_comm['Reading score earned'][n] + "," + wab_read_comm.iloc[:,6][n])
                            else:
                                temp_items.append(wab_read_comm['Reading score earned'][n])
                                temp_items.append(wab_read_comm['Perf score earned'][n])
                                temp_items.append(wab_read_comm.iloc[:,6][n])
                        for n, i in enumerate(temp_items):  # Turn floats into integers for Redcap
                            if i == 1.0:
                                temp_items[n] = '1'
                            elif i == 0.0:
                                temp_items[n] = '0'
                        temp_df = pd.DataFrame([temp_items], columns=wab_read_comm_headers)
                        single_test = pd.concat([single_test, temp_df], axis=1)
    else:
        missing_wab_reading.append(file)
    
    all_test_read = all_test_read.append(single_test)

#all_test = all_test.drop_duplicates(['Subject', 'Date'])
#all_test.to_csv('dataframe_output/wab_read_comm.csv', encoding='utf-8', index=False)
    
    

#all_test_comp_sent.to_csv('dataframe_output/wab_comp_sent.csv', encoding='utf-8', index=False)
#all_test_read.to_csv('dataframe_output/wab_read.csv', encoding='utf-8', index=False)

all_test = all_test_read.merge(all_test_comp_sent, on=['Subject', 'Date'])
all_test = all_test.drop_duplicates(['Subject', 'Date'])
all_test.to_csv('dataframe_output/wab_reading.csv', encoding='utf-8', index=False)
    
    