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
#lang_files = ['/Users/axs97/Desktop/lang_eval_to_redcap-alexs/Patients/LastNameN_Z/Zwigard_Frank/Zwigard_110612/zwigard_110612.xls']
#lang_files = ['/Users/axs97/Desktop/lang_eval_to_redcap-alexs/Patients/LastNameN_Z/Zwigard_Frank/Zwigard_022811/zwigard_lang_022811.xls']
#lang_files = ['/Users/axs97/Desktop/lang_eval_to_redcap-alexs/Patients/LastNameA_F/Dines_Sally/050415/lang_eval_SD_050415.xls']

data = []

# cols will be used to build dataframe off of specific Redcap headers
redcap_cols = pd.read_csv(work_dir + '/DickersonMasterEnrollment_ImportTemplate_2017-07-24.csv')

single_test = pd.DataFrame()
count = 0
date_error = []

missing_transcr = [] # 26 (Lang Trascription sheet exists but is empty)
missing_transcr_file = [] # 62 (file does not have 'lang trans')
transcription_total = [] # 231
total_response_error = [] # 0
transcr_resp_numb_error = [] # 82 (does not indicate prompt number)
response_keyword_error = []

all_trans = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names

    transcr_response_error = []
        
    # Language Transcription

    if 'Lang transcriptions' in sprdshts:
        lang_trans = pd.read_excel(file, 'Lang transcriptions', header=None)
        transcription_total.append(file)
    
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
        
        # find date searching through different types of formats
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
    
        if lang_trans.empty:
            missing_transcr.append(file)
        else:
            lang_items = lang_trans.index.tolist()

            trans_clear = lang_trans.fillna('')
            trans_clear = trans_clear.drop(trans_clear.columns[0], axis=1)

            if trans_clear.empty:
                missing_transcr.append(file)

            else:
                # search for cells that contain string that start with prompt number
                mask = np.column_stack(
                                        [trans_clear[col].str.startswith
                                            (r"1.", na=False) for
                                            col in trans_clear])
                response1 = trans_clear.loc[mask.any(axis=1)]
                if ('2.' or '3.' or '4.' or '5.' or '6.') in response1:
                    transcr_response_error.append('response1')

                mask = np.column_stack(
                                        [trans_clear[col].str.startswith
                                            (r"2.", na=False) for
                                            col in trans_clear])
                response2 = trans_clear.loc[mask.any(axis=1)]
                if ('1.' or '3.' or '4.' or '5.' or '6.') in response2:
                    transcr_response_error.append('response2')

                mask = np.column_stack(
                                        [trans_clear[col].str.startswith
                                            (r"3.", na=False) for
                                            col in trans_clear])
                response3 = trans_clear.loc[mask.any(axis=1)]
                if ('1.' or '2.' or '4.' or '5.' or '6.') in response3:
                    transcr_response_error.append('response3')

                mask = np.column_stack(
                                        [trans_clear[col].str.startswith
                                            (r"4.", na=False) for
                                            col in trans_clear])
                response4 = trans_clear.loc[mask.any(axis=1)]
                if ('1.' or '2.' or '3.' or '5.' or '6.') in response4:
                    transcr_response_error.append('response4')

                mask = np.column_stack(
                                        [trans_clear[col].str.startswith
                                            (r"5.", na=False) for
                                            col in trans_clear])
                response5 = trans_clear.loc[mask.any(axis=1)]
                if ('1.' or '2.' or '3.' or '4.' or '6.') in response5:
                    transcr_response_error.append('response5')

                mask = np.column_stack(
                                        [trans_clear[col].str.startswith
                                            (r"6.", na=False) for
                                            col in trans_clear])
                response6 = trans_clear.loc[mask.any(axis=1)]
                if ('1.' or '2.' or '3.' or '4.' or '5.') in response6:
                    transcr_response_error.append('response6')

                transcription = [date, '', '', '', '', '', '', '']
                if '1.' in str(response1.iloc[:, -1]):
                    transcription[1] = response1.iloc[:, -1]
                if '2.' in str(response2.iloc[:, -1]):
                    transcription[2] = response2.iloc[:, -1]
                if '3.' in str(response3.iloc[:, -1]):
                    transcription[3] = response3.iloc[:, -1]
                if '4.' in str(response4.iloc[:, -1]):
                    transcription[4] = response4.iloc[:, -1]
                if '5.' in str(response5.iloc[:, -1]):
                    transcription[5] = response5.iloc[:, -1]
                if '6.' in str(response6.iloc[:, -1]):
                    transcription[6] = response6.iloc[:, -1]
                
                if len(transcr_response_error) > 0:
                    total_response_error.append([file, transcr_response_error])
                
                if (len(transcription[1])==0 and
                        len(transcription[2])==0 and
                        len(transcription[3])==0 and
                        len(transcription[4])==0 and
                        len(transcription[5])==0 and
                        len(transcription[6])==0 and
                        len(transcription[7])==0):
                    trans_clear = lang_trans
                    trans_clear[0][1:7] = np.nan
                    trans_clear = lang_trans.fillna('')
                    
                    trans_clear = trans_clear.dropna(axis=1, how='all')
                    trans_clear.replace(to_replace=1, value='1',inplace=True)
                    trans_clear.replace(to_replace=2, value='2',inplace=True)
                    trans_clear.replace(to_replace=3, value='3',inplace=True)
                    trans_clear.replace(to_replace=4, value='4',inplace=True)
                    
                    for p in trans_clear.index:
                        if '1' in trans_clear.loc[p].tolist():
                            response1 = trans_clear.loc[p].tolist()[1]
                            transcription[1] = response1
                        if '2' in trans_clear.loc[p].tolist():
                            response2 = trans_clear.loc[p].tolist()[1]
                            transcription[2] = response2
                        if '3' in trans_clear.loc[p].tolist():
                            response3 = trans_clear.loc[p].tolist()[1]
                            transcription[3] = response3
                        if '4' in trans_clear.loc[p].tolist():
                            response4 = trans_clear.loc[p].tolist()[1]
                            transcription[4] = response4
                        if '5' in trans_clear.loc[p].tolist():
                            response5 = trans_clear.loc[p].tolist()[1]
                            transcription[5] = response5
                        if '6' in trans_clear.loc[p].tolist():
                            response6 = trans_clear.loc[p].tolist()[1]
                            transcription[6] = response6
                    
                    sunday = ['Sunday','grew up','husband','wife']
                    job = ['work', 'job']
                    picnic = ['WAB Picnic', 'fish', 'fishing', 'sail',
                              'sailing', 'kite', 'picnic', 'flag']
                    sherman1 = ['Sherman 1','beach','towel','swim','drown',
                                'towel', 'sun']
                    sherman2 = ['Sherman 2', 'Sherman Baseball Picture',
                                'window','broken','baseball','bat','newspaper',
                                'shoe','truck','toy']
                    brookshire = ['Cinderella','step sisters','cinderella','Brookshire',
                                  'Fairy', 'fairy', 'Prince Charming', 'Prince charming']
                    
                    if (len(transcription[1])==0 and
                            len(transcription[2])==0 and
                            len(transcription[3])==0 and
                            len(transcription[4])==0 and
                            len(transcription[5])==0 and
                            len(transcription[6])==0 and
                            len(transcription[7])==0):
                        trans_clear = trans_clear.replace('', np.nan).dropna(axis=0, how='all')
                        trans_clear = trans_clear.dropna(axis=1, how='all').reset_index()
                        trans_clear = trans_clear.fillna('')
                        trans_clear = trans_clear.iloc[:,1]
                        trans_list = trans_clear.tolist()
                        response_list = []
                        for x in trans_clear.index:
                            for q in sunday:
                                if q in trans_clear.iloc[x]:
                                    if 'Sunday' in response_list:
                                        break
                                    response_sun = trans_clear.iloc[x]
                                    response_list.append('Sunday')
                                    transcription[1] = response_sun
                            for r in job:
                                if r in trans_clear.iloc[x]:
                                    if 'Job' in response_list:
                                        break
                                    response_job = trans_clear.iloc[x]
                                    response_list.append('Job')
                                    transcription[2] = response_job
                            for s in picnic:
                                if s in trans_clear.iloc[x]:
                                    if 'Picnic' in response_list:
                                        break
                                    response_picnic = trans_clear.iloc[x]
                                    response_list.append('Picnic')
                                    transcription[3] = response_picnic
                            for t in sherman1:
                                if t in trans_clear.iloc[x]:
                                    if 'Sherman1' in response_list:
                                        break
                                    response_sher1 = trans_clear.iloc[x]
                                    response_list.append('Sherman1')
                                    transcription[4] = response_sher1
                            for u in sherman2:
                                if u in trans_clear.iloc[x]:
                                    if 'Sherman2' in response_list:
                                        break
                                    response_sher2 = trans_clear.iloc[x]
                                    response_list.append('Sherman2')
                                    transcription[5] = response_sher2
                            for v in brookshire:
                                if v in trans_clear.iloc[x]:
                                    if 'Brookshire' in response_list:
                                        break
                                    response_brook = trans_clear.iloc[x]
                                    response_list.append('Brookshire')
                                    transcription[6] = response_brook
                        
                        if len(trans_clear) != len(response_list):
                            response_keyword_error.append([file])
                        
                        if (len(transcription[1])==0 and
                            len(transcription[2])==0 and
                            len(transcription[3])==0 and
                            len(transcription[4])==0 and
                            len(transcription[5])==0 and
                            len(transcription[6])==0 and
                            len(transcription[7])==0):
                            transcr_resp_numb_error.append(file)
    
                trans_df = pd.DataFrame(data=[transcription],
                                        columns=[col for col in
                                        redcap_cols.columns
                                        if 'lang_transcr_' in col])
                single_test = pd.concat([single_test, trans_df], axis=1)

    else:
        missing_transcr_file.append(file)

    all_trans = all_trans.append(single_test)
    all_trans = all_trans.drop_duplicates(['Subject', 'Date'])
    
    transcr_patients = pd.DataFrame()
    transcr_patients = all_trans.groupby(all_trans['Subject'].tolist(),as_index=False).size() # 100 out of 126 total

all_trans.to_csv('Lang_trans_Final.csv', encoding='utf-8')

no_trans = len(missing_transcr_file)
captured = (len(transcription_total))
empty_trans = len(missing_transcr)
correct = (len(transcription_total)-len(missing_transcr)-len(transcr_resp_numb_error))
numb_error = len(transcr_resp_numb_error)

# Graph Total Errors
total_list = ['Test', 'Captured', 'File missing test']
total_data = ['Lang Transcription', captured, no_trans]
total_graph = pd.DataFrame(data=[total_data], columns=total_list)
total_graph = total_graph.set_index(['Test'])
total_graph.to_csv('total_trans_graph.csv', encoding='utf-8')

# Graph Percent Errors
col_list = ['Test', 'Correct', 'Empty test', 'Header error', 'Response numbering error', 'Column number error', 'Test length error']
col_data = ['Lang Transcription',correct,empty_trans,np.nan,numb_error,np.nan,np.nan]
graph = pd.DataFrame(data =[col_data], columns=col_list)
graph = graph.set_index(['Test'])
graph = graph.fillna(0)

percent_data = ['Lang Transcription']
for x in graph.iloc[0].tolist():
    percent = (float(x) / sum(graph.iloc[0])) * 100
    percent_data.append(percent)

lang_graph = pd.DataFrame(data=[percent_data], columns=col_list)
lang_graph = lang_graph.set_index(['Test'])
lang_graph = lang_graph.replace(0, np.nan)

lang_graph.to_csv('lang_trans_graph.csv', encoding='utf-8')

'''
files = pd.Series([no_trans, captured],
                  index=['No Lang Transcription'+ ': ' +str(no_trans),
                         'Captured Data'+ ': ' +str(captured)], name='')
files_graph = files.plot.pie(title='Summary of Files: Language Transcription', autopct='%.2f%%', figsize=(6,6), fontsize=15, colors=['r', 'g'])
#plt.show(files_graph)
correct_data = pd.Series([correct, numb_error, empty_trans],
                         index=['Captured Correctly'+ ': ' +str(correct),
                                'Response Numbering Error'+ ': ' +str(numb_error),
                                'Empty Trans Sheet'+ ': ' +str(empty_trans)], name='')
data_graph = correct_data.plot.pie(title='Breakdown of Captured Data: Lang Transcriptions', autopct='%.2f%%', figsize=(6,6), fontsize=15, colors=['b', 'c', 'y'])
#plt.show(data_graph)
'''
