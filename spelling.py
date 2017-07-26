import pandas as pd
import csv
import numpy as np
import re

import os
import fnmatch
from datetime import datetime
import matplotlib.pyplot as plt

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
#lang_files = [work_dir + '/Patients/LastNameA_F/Adamian_Daniel/010815/adamian_lang_010815.xls']

data = []

# cols will be used to build dataframe off of specific Redcap headers
cols = pd.read_csv(work_dir + '/DickersonMasterEnrollment_ImportTemplate_2017-07-24.csv')

count = 0

spelling_total = [] # 177
empty_spelling = []
missing_spelling = [] # xls doesnt have spelling sheet (166)
spelling_error = [] # too few columns (4)
spelling_column_error = [] # too many columns (possibly old test or too many notes) (4)
spelling_length_error = [] # not enough or too many words tested (1)
header_error_spelling = [] 
date_error = []

all_test = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file
    single_test = pd.DataFrame()
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names
    
    if 'Spelling' in sprdshts:
        print file
        spelling_total.append(file)
        spelling = pd.read_excel(file, 'Spelling')
        
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
            'words',
            'correct/incorrect (0/1)',
            'response if incorrect'
            ]

        temp_head_errors = []

        if spelling.empty:
            empty_spelling.append(file)
            complete = 'no'
        else:
            # drop Nan columns and rows to bring notes right after data and create consistancy
            spelling_clear = spelling.dropna(axis=1, how='all')
            spelling_clear = spelling_clear.dropna(axis=0, how='all')
            if len(spelling_clear.columns) > 4:
                    spelling_column_error.append(file)
            else:
                # reset index to create more consistancy and get limit df to data (not totals/percentages)
                spelling_clear = spelling_clear.iloc[1:].reset_index()
                spelling_clear = spelling_clear.drop('index', axis=1)
                spelling_clear = spelling_clear.iloc[:12]
                if len(spelling_clear.columns) < 3:
                    spelling_error.append(file)
                else:
                    if len(spelling_clear.columns) > 3:
                        relevant_headers = ['words', 'correct/incorrect (0/1)','response if incorrect', 'notes']
                        spelling_clear.columns = relevant_headers
                    else:
                        # add 'notes' column if none
                        spelling_clear.columns = relevant_headers
                        spelling_clear['notes'] = ''
                    spelling_items = spelling_clear.index.tolist()
                    if len(spelling_items) != 12:
                        spelling_length_error.append(file)
                    else:
                        complete = 'yes'
                        
                        full_list = ['', date]
            
                        # create list of data that includes correct/incorrect, incorrect response, and notes
                        for i in spelling_items:
                            if spelling_clear.loc[i]['correct/incorrect (0/1)'] == 1:
                                full_list.append('correct')
                                full_list.append('')
                                full_list.append(spelling_clear.loc[i]['notes'])
                            elif spelling_clear.loc[i]['correct/incorrect (0/1)'] == 0:
                                full_list.append('incorrect')
                                full_list.append(spelling_clear.loc[i]['response if incorrect'])
                                full_list.append(spelling_clear.loc[i]['notes'])
                            else:
                                full_list.append('none')
                                full_list.append('')
                                full_list.append(spelling_clear.loc[i]['notes'])
            
                        full_list.append('')
                        full_list.append(complete)
                        
                        # create df with data from single patient file
                        spelling_df = pd.DataFrame([full_list],
                                                    columns=[col for col in cols.columns
                                                    if 'spelling' in col])
                        single_test = pd.concat([single_test, spelling_df], axis=1)
    else:
        missing_spelling.append(file)

    all_test = all_test.append(single_test)

all_test = all_test.drop_duplicates(['Subject', 'Date'])
all_test.to_csv('spelling-Final.csv', encoding='utf-8')

# find size of errors
no_spelling = len(missing_spelling)
captured = (len(spelling_total))
empty = len(empty_spelling)
correct = (len(spelling_total)-len(spelling_column_error)-len(spelling_error)-len(spelling_length_error)-len(empty_spelling))
many_columns_error = len(spelling_column_error)
few_columns_error = len(spelling_error)
test_length_error = len(spelling_length_error)

# Graph Total Errors
total_list = ['Test', 'Captured', 'File missing test']
total_data = ['Spelling', captured, no_spelling]
total_graph = pd.DataFrame(data=[total_data], columns=total_list)
total_graph = total_graph.set_index(['Test'])
total_graph.to_csv('total_spelling_graph.csv', encoding='utf-8')

# Graph Percent Errors
col_list = ['Test', 'Correct', 'Empty test', 'Header error', 'Response numbering error', 'Column number error', 'Test length error']
col_data = ['Spelling',correct,empty,np.nan,np.nan,many_columns_error + few_columns_error,test_length_error]
graph = pd.DataFrame(data =[col_data], columns=col_list)
graph = graph.set_index(['Test'])
graph = graph.fillna(0)

percent_data = ['Spelling']
for x in graph.iloc[0].tolist():
    percent = (float(x) / sum(graph.iloc[0])) * 100
    percent_data.append(percent)

spell_graph = pd.DataFrame(data=[percent_data], columns=col_list)
spell_graph = spell_graph.set_index(['Test'])
spell_graph = spell_graph.replace(0, np.nan)

spell_graph.to_csv('spelling_graph.csv', encoding='utf-8')

'''
files = pd.Series([no_spelling, captured],
                  index=['No Spelling'+ ': ' +str(no_spelling),
                         'Captured Data'+ ': ' +str(captured)], name='')
files_graph = files.plot.pie(title='Summary of Files: Spelling', autopct='%.2f%%', figsize=(6,6), fontsize=15, colors=['r', 'g'])
#plt.show(files_graph)
correct_data = pd.Series([correct, many_columns_error, few_columns_error, test_length_error],
                   index=['Correctly Captured'+ ': ' +str(correct),
                          'Too Many Columns'+ ': ' +str(many_columns_error),
                          'Too Few Columns'+ ': ' +str(few_columns_error),
                          'Test Length Error'+ ': ' +str(test_length_error)], name='')
data_graph = correct_data.plot.pie(title='Breakdown of Captured Data: Spelling', autopct='%.2f%%', figsize=(6,6), fontsize=15, colors=['b', 'c', 'y', 'p'])
#plt.show(data_graph)
'''
