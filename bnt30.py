# -*- coding: utf-8 -*-
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
#redcap_cols = cols.columns.tolist()
redcap_cols = filter(lambda k: 'bnt30' in k, cols)
###############################################################################

single_test = pd.DataFrame()
date_error = []
total_files = []

bnt30_total = []
bnt30_script_error = []
missing_bnt30_file = []
header_error_bnt30 = []

all_test = pd.DataFrame()

###############################################################################


for file in lang_files:  # Iterate through every found excel file
    total_files.append(file)
    
    if '/.' in file:  # If file is a hidden file, skip
        continue
    
    # Boston Naming Test 30
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names
    
    if 'BNT30' in sprdshts:
        bnt30_total.append(file)
        bnt30 = pd.read_excel(file, 'BNT30')
        headers = bnt30.loc[3].tolist()
        if headers[1] != 'Object':
            headers = bnt30.loc[4].tolist()
            if headers[1] != 'Object':
                headers = bnt30.loc[5].tolist()
        headers[0] = 'item'
        
        # to compensate for header error
        if 'Verbatim response of incorrect' in headers:
            headers[3] = 'Verbatim response if incorrect'
        if 'Verbatim response' in headers:
            headers[3] = 'Verbatim response if incorrect'
        if 'Latency' in headers:
            headers.remove('Latency')
            bnt30 = bnt30.drop(bnt30.columns[3], axis=1)
        if 'Spont gesture if given (1,0)' in headers:
            headers[4] = 'Spont gesture if given (1, 0)'
        if 'Spont gesture if given (1, 0)' not in headers:
            spont_col = ['', '', '', 'Spont gesture if given (1, 0)']
            headers.insert(4, 'Spont gesture if given (1, 0)')
            bnt30.insert(4, 'spont', '')
            bnt30.spont[3] = 'Spont gesture if given (1, 0)'
        if 'Correct w/stim cue (1,0)' in headers:
            headers[5] = 'Correct w/sem cue (1,0)'
        if 'Verbatim response of incorrect after stim cue' in headers:
            headers[6] = 'Verbatim response if incorrect after stim cue'
        if 'Verbatim response of incorrect after ph cue' in headers:
            headers[8] = 'Verbatim response if incorrect after ph cue'
        if 'Verbatim response of incorrect after ortho cue' in headers:
            headers[8] = 'Verbatim response if incorrect after ph cue'
        if 'Response if incorrect' not in headers:
            headers.append('Response if incorrect')
            bnt30['Response if incorrect'] = np.nan

        single_test = pd.DataFrame()
    
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
        
        relevant_headers = [
            'Spont correct (1, 0)',
            'Verbatim response if incorrect',
            'Spont gesture if given (1, 0)',
            'Correct w/sem cue (1,0)',
            'Verbatim response if incorrect after stim cue',
            'Correct w/ph cue (1,0)',
            'Verbatim response if incorrect after ph cue',
            'Correct w/mult choice (1,0)',
            'Response if incorrect'
            ]

        temp_head_errors = []

        for head in relevant_headers:
            if head in headers:
                continue
            else:
                temp_head_errors.append(head)
        if not temp_head_errors: # start dataframe at beginning of dataset
            bnt30_notNaN = bnt30[~pd.isnull(bnt30['Boston Naming Test'])]
            bnt30_only_items = bnt30_notNaN[pd.isnull(bnt30
                                                      ['Boston Naming Test']
                                                      .str.isnumeric())]
            bnt30_only_items.columns = headers

            bnt30_relevant = bnt30_only_items[[
                'Spont correct (1, 0)',
                'Verbatim response if incorrect',
                'Spont gesture if given (1, 0)',
                'Correct w/sem cue (1,0)',
                'Verbatim response if incorrect after stim cue',
                'Correct w/ph cue (1,0)',
                'Verbatim response if incorrect after ph cue',
                'Correct w/mult choice (1,0)',
                'Mult choice prompts',
                'Response if incorrect'
                ]]

            bnt30_relevant = bnt30_relevant.set_index(bnt30_only_items['item'])
            bnt30_relevant.insert(5, 'notes', "")

            items = bnt30_relevant.index.tolist()
            for i in items: # iterate through all words and indicate responses
                temp_list = ['', '', '', '', '', '', '', '']
                if i < 10:
                    # replace first value with correct string
                    test = 'bnt30_response_' + str(i)
                    if bnt30_relevant.loc[i]['Spont correct (1, 0)'] == 1:
                        temp_list[0] = '1'  # Spontaneous
                    elif bnt30_relevant.loc[i]['Correct w/sem cue (1,0)'] == 1:
                        temp_list[0] = '2'  # Semantic cue
                    elif bnt30_relevant.loc[i]['Correct w/ph cue (1,0)'] == 1:
                        temp_list[0] = '3'  # Phonemic cue
                    else:
                        temp_list[0] = '4'  # Not named

                    if bnt30_relevant.loc[i]['Spont correct (1, 0)'] == 0:
                        temp_list[1] = (bnt30_relevant.loc[i]
                                        ['Verbatim response if incorrect'])
                        temp_list[2] = (bnt30_relevant.loc[i]
                                        ['Spont gesture if given (1, 0)'])

                    if bnt30_relevant.loc[i]['Correct w/sem cue (1,0)'] == 0:
                        temp_list[3] = (bnt30_relevant.loc[i]
                                        ['Verbatim response if '
                                         'incorrect after stim cue'])

                    if bnt30_relevant.loc[i]['Correct w/ph cue (1,0)'] == 0:
                        temp_list[4] = (bnt30_relevant.loc[i]
                                        ['Verbatim response '
                                         'if incorrect after ph cue'])

                    #if bnt30_relevant.loc[i]['Correct w/mult '
                    #                         'choice (1,0)'] == 1:
                    #    temp_list[6] = 'Correct'
                    if bnt30_relevant.loc[i]['Correct w/mult '
                                             'choice (1,0)'] == 0:
                        temp_list[6] = '2'
                        temp_list[7] = (bnt30_relevant.loc[i]
                                        ['Response if incorrect'])

                    # put data from single patient into a temporary df
                    temp_df = pd.DataFrame([temp_list],
                                           columns=[col for col in cols.columns
                                                    if 'bnt30' in col and
                                                    '_'+str(i) in col[-2:]])
                else:
                    if bnt30_relevant.loc[i]['Spont correct (1, 0)'] == 1:
                        temp_list[0] = '1'  # Spontaneous
                    elif bnt30_relevant.loc[i]['Correct w/sem cue (1,0)'] == 1:
                        temp_list[0] = '2'  # Semantic cue
                    elif bnt30_relevant.loc[i]['Correct w/ph cue (1,0)'] == 1:
                        temp_list[0] = '3'  # Phonemic cue
                    else:
                        temp_list[0] = '4'  # Not named

                    if bnt30_relevant.loc[i]['Spont correct (1, 0)'] == 0:
                        temp_list[1] = (bnt30_relevant.loc[i]
                                        ['Verbatim response if incorrect'])
                        temp_list[2] = (bnt30_relevant.loc[i]
                                        ['Spont gesture if given (1, 0)'])

                    if bnt30_relevant.loc[i]['Correct w/sem cue (1,0)'] == 0:
                        temp_list[3] = (bnt30_relevant.loc[i]
                                        ['Verbatim response if '
                                         'incorrect after stim cue'])

                    if bnt30_relevant.loc[i]['Correct w/ph cue (1,0)'] == 0:
                        temp_list[4] = (bnt30_relevant.loc[i]
                                        ['Verbatim response '
                                         'if incorrect after ph cue'])

                    #if bnt30_relevant.loc[i]['Correct w/mult '
                    #                         'choice (1,0)'] == 1:
                    #    temp_list[6] = 'Correct'

                    if bnt30_relevant.loc[i]['Correct w/mult '
                                             'choice (1,0)'] == 0:
                        temp_list[6] = '2'
                        temp_list[7] = (bnt30_relevant.loc[i]
                                        ['Response if incorrect'])

                    # put data from single test word into a temporary df
                    temp_df = pd.DataFrame([temp_list],
                                            columns=[col for col in
                                                    cols.columns if 'bnt30' in
                                                    col and '_' + str(i)
                                                    in col])

                # add data from word to growing df of all words in test
                single_test = pd.concat([single_test, temp_df], axis=1)
                if len(single_test.columns) < 3:
                    bnt30_script_error.append(file)
        #for col in single_test.columns:
        #    single_test[col] = single_test[col].str.replace('â€¦', '...')
        else:
            header_error_bnt30.append([file, temp_head_errors])
        single_test.replace({'â€¦': '...'}, regex=True)
        
        # Replace text reponses with numeric for Redcap
        filter_cols = [col for col in single_test if col.startswith('bnt30_response_')]

        
    else:
        missing_bnt30_file.append(file)

    if 'bnt30_response_1' not in single_test.columns or single_test['bnt30_response_1'].empty:
        bnt30_script_error.append(file)
    else:
        all_test = all_test.append(single_test)
    all_test = all_test.drop_duplicates(['Subject', 'Date'])

    bnt30_patients = pd.DataFrame()
    bnt30_patients = all_test.groupby(all_test['Subject'].tolist(),as_index=False).size() # 109 out of 126 total


#all_test = all_test.str.replace('â€¦', '...')
all_test.to_csv('dataframe_output/bnt30.csv', encoding='utf-8', index=False)
#all_test.to_csv('dataframe_output/BNT30-Final.csv', index=False)

