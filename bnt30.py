import pandas as pd
import csv
import numpy as np
import re
from datetime import datetime
import matplotlib.pyplot as plt

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

data = []

# cols will be used to build dataframe off of specific Redcap headers
cols = pd.read_csv(work_dir + '/DickersonMasterEnrollment_ImportTemplate_2017-07-24.csv')

single_test = pd.DataFrame()
count = 0

date_error = []

total_files = []

bnt30_total = [] # 246
bnt30_script_error = [] # 0
missing_bnt30_file = [] # 47 (xls sheet does not have BNT30)
header_error_bnt30 = [] # 51 (typically 'if' is written 'of')

all_test = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file
    total_files.append(file)
    
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
                        temp_list[0] = 'Spontaneous'
                    elif bnt30_relevant.loc[i]['Correct w/sem cue (1,0)'] == 1:
                        temp_list[0] = 'Semantic cue'
                    elif bnt30_relevant.loc[i]['Correct w/ph cue (1,0)'] == 1:
                        temp_list[0] = 'Phonemic cue'
                    else:
                        temp_list[0] = 'Not named'

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

                    if bnt30_relevant.loc[i]['Correct w/mult '
                                             'choice (1,0)'] == 1:
                        temp_list[6] = 'Correct'
                    if bnt30_relevant.loc[i]['Correct w/mult '
                                             'choice (1,0)'] == 0:
                        temp_list[6] = 'Incorrect'
                        temp_list[7] = (bnt30_relevant.loc[i]
                                        ['Response if incorrect'])

                    # put data from single patient into a temporary df
                    temp_df = pd.DataFrame([temp_list],
                                           columns=[col for col in cols.columns
                                                    if 'bnt30' in col and
                                                    '_'+str(i) in col[-2:]])
                else:
                    if bnt30_relevant.loc[i]['Spont correct (1, 0)'] == 1:
                        temp_list[0] = 'Spontaneous'
                    elif bnt30_relevant.loc[i]['Correct w/sem cue (1,0)'] == 1:
                        temp_list[0] = 'Semantic cue'
                    elif bnt30_relevant.loc[i]['Correct w/ph cue (1,0)'] == 1:
                        temp_list[0] = 'Phonemic cue'
                    else:
                        temp_list[0] = 'Not named'

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

                    if bnt30_relevant.loc[i]['Correct w/mult '
                                             'choice (1,0)'] == 1:
                        temp_list[6] = 'Correct'

                    if bnt30_relevant.loc[i]['Correct w/mult '
                                             'choice (1,0)'] == 0:
                        temp_list[6] = 'Incorrect'
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
        else:
            header_error_bnt30.append([file, temp_head_errors])
    else:
        missing_bnt30_file.append(file)

    all_test = all_test.append(single_test)
    all_test = all_test.drop_duplicates(['Subject', 'Date'])

    bnt30_patients = pd.DataFrame()
    bnt30_patients = all_test.groupby(all_test['Subject'].tolist(),as_index=False).size() # 109 out of 126 total

all_test.to_csv('BNT30-Final.csv', encoding='utf-8')

# find size of errors
no_bnt30 = len(missing_bnt30_file)
captured = (len(bnt30_total))
correct = (len(bnt30_total)-len(header_error_bnt30))
header_error = len(header_error_bnt30)

'''
files = pd.Series([no_bnt30, captured],
                  index=['No BNT30'+ ': ' +str(no_bnt30),
                         'Captured Data'+ ': ' +str(captured)], name='')

files_graph = files.plot.pie(title='Summary of Files: BNT30', autopct='%.2f%%', figsize=(6,6), fontsize=15, colors=['r', 'g'])
#plt.show(files_graph)

correct_data = pd.Series([correct, header_error],
                   index=['Correctly Captured'+ ': ' +str(correct),
                          'Header Error'+ ': ' +str(header_error)], name='')

data_graph = correct_data.plot.pie(title='Breakdown of Captured Data: BNT30', autopct='%.2f%%', figsize=(6,6), fontsize=15, colors=['b', 'c'])
#plt.show(data_graph)
'''

graph = pd.DataFrame()
graph['Test'] = 'BNT30'
graph['Correct'] = correct
graph['File missing test'] = no_bnt30
graph['Empty test'] = np.nan
graph['Header error'] = header_error
graph['Response numbering error'] = np.nan
graph['Column number error'] = np.nan
graph['Test length error'] = np.nan

graph.to_csv('bnt30_graph.csv', encoding='utf-8')
