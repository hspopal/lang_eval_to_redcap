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
#lang_files = [work_dir +'/Patients/LastNameA_F/Adamian_Daniel/010815/adamian_lang_010815.xls']
#lang_files = [work_dir +'/Patients/LastNameA_F/Ahern_Timothy/060616/lang_eval_Ahern_060616.xls']
#lang_files = [work_dir +'/Patients/LastNameA_F/Ahern_Timothy/121415/lang_eval_TA_121415.xls']

data = []

# cols will be used to build dataframe off of specific Redcap headers
redcap_cols = pd.read_csv(work_dir + '/DickersonMasterEnrollment_ImportTemplate_2017-07-24.csv')

single_test = pd.DataFrame()
count = 0
date_error = []

writ_sample_total = []
missing_writ_sample = []
total_writ_error = [] # files that have responses with more than one prompt number (0)
sample_resp_numb_error = [] # response has no prompt number indication (59)
all_sample = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names

    writ_sample_error = []
        
    # Writing Sample
    if 'Writing samples' in sprdshts:
        writ_sample = pd.read_excel(file, 'Writing samples', header=None)
        writ_sample_total.append()
        print file
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
    
        if writ_sample.empty:
            missing_writ_sample.append(file)
        else:
            sample_items = writ_sample.index.tolist()

            if writ_sample[0][2:6].tolist() == [1, 2, 3, 4]: # delete prompts
                writ_sample[0][2:6] = np.nan
                writ_sample[1][2:6] = np.nan

            # make number values into string
            writ_clear = writ_sample
            writ_clear = writ_clear.dropna(axis=1, how='all')
            writ_clear.replace(to_replace=1, value='1',inplace=True)
            writ_clear.replace(to_replace=2, value='2',inplace=True)
            writ_clear.replace(to_replace=3, value='3',inplace=True)
            writ_clear.replace(to_replace=4, value='4',inplace=True)

            if writ_clear.empty:
                missing_writ_sample.append(file)

            else:
                if writ_clear.empty == False:
                    complete = 'yes'
                else:
                    complete = 'no'

                transcription = [date, '', '', '', '', '', '', '', complete]
            
                # search for series that contain string that start with prompt number(i.e. '1.')
                mask = np.column_stack(
                                       [writ_clear[col].str.startswith
                                        (r"1.", na=False) for
                                         col in writ_clear])
                response1 = writ_clear.loc[mask.any(axis=1)]
                if ('2.' or '3.' or '4.' or '5.' or '6.') in response1:
                    writ_sample_error.append('response1')

                mask = np.column_stack(
                                        [writ_clear[col].str.startswith
                                            (r"2.", na=False) for
                                            col in writ_clear])
                response2 = writ_clear.loc[mask.any(axis=1)]
                if ('1.' or '3.' or '4.' or '5.' or '6.') in response2:
                    writ_sample_error.append('response2')

                mask = np.column_stack(
                                        [writ_clear[col].str.startswith
                                            (r"3.", na=False) for
                                            col in writ_clear])
                response3 = writ_clear.loc[mask.any(axis=1)]
                if ('1.' or '2.' or '4.' or '5.' or '6.') in response3:
                    writ_sample_error.append('response3')

                mask = np.column_stack(
                                        [writ_clear[col].str.startswith
                                            (r"4.", na=False) for
                                            col in writ_clear])
                response4 = writ_clear.loc[mask.any(axis=1)]
                if ('1.' or '2.' or '3.' or '5.' or '6.') in response4:
                    writ_sample_error.append('response4')
                    
                mask = np.column_stack(
                                        [writ_clear[col].str.startswith
                                            (r"Notes: picnic", na=False) for
                                            col in writ_clear])
                note_picnic = writ_clear.loc[mask.any(axis=1)]
                transcription[6] = note_picnic.iloc[:, -1]
                
                mask = np.column_stack(
                                        [writ_clear[col].str.startswith
                                            (r"Notes: sent", na=False) for
                                            col in writ_clear])
                note_sent = writ_clear.loc[mask.any(axis=1)]
                transcription[4] = note_sent.iloc[:,-1]

                # define response variable as cell with prompt number string
                if '1.' in str(response1.iloc[:, 0]):
                    transcription[1] = response1.iloc[:, 0]
                if '2.' in str(response2.iloc[:, 0]):
                    transcription[2] = response2.iloc[:, 0]
                if '3.' in str(response3.iloc[:, 0]):
                    transcription[3] = response3.iloc[:, 0]
                if '4.' in str(response4.iloc[:, 0]):
                    transcription[5] = response4.iloc[:, 0]

                # collect files that have responses with two different prompt numbers
                if len(writ_sample_error) > 0:
                    total_writ_error.append([file, writ_sample_error])

                # compensate for error: transcriptions that don't have prompt number indicator but have '1' in previous cell
                if response1.empty and response2.empty and response3.empty and response4.empty:
                    for x in writ_clear.index:
                        if '1' in writ_clear.loc[x].tolist():
                            sample1 = writ_clear.loc[x].tolist()[1]
                            transcription[1] = sample1
                        if '2' in writ_clear.loc[x].tolist():
                            sample2 = writ_clear.loc[x].tolist()[1]
                            transcription[2] = sample2
                        if '3' in writ_clear.loc[x].tolist():
                            sample3 = writ_clear.loc[x].tolist()[1]
                            transcription[3] = sample3
                        if '4' in writ_clear.loc[x].tolist():
                            sample4 = writ_clear.loc[x].tolist()[1]
                            transcription[5] = sample4
                        
                if len(transcription[1])==0 and len(transcription[2])==0 and len(transcription[3])==0 and len(transcription[4])==0 and len(transcription[5])==0 and len(transcription[6])==0:
                    sample_resp_numb_error.append(file)

                # create dataframe with data from single patient file
                writ_df = pd.DataFrame(data=[transcription],
                                        columns=[col for col in
                                        redcap_cols.columns
                                        if 'writing_samp' in col])
                single_test = pd.concat([single_test, writ_df], axis=1)

    else:
        missing_writ_sample.append(file)

    all_sample = all_sample.append(single_test)
    all_sample = all_sample.drop_duplicates(['Subject', 'Date'])

all_sample.to_csv('writ_sample.csv', encoding='utf-8')

# find size of errors
no_writ_sample = len(missing_writ_sample)
captured = (len(writ_sample_total))
correct = (len(writ_sample_total)-len(sample_resp_numb_error)-len(total_writ_error))
numb_error = len(sample_resp_numb_error)
response_error = len(total_writ_error)

files = pd.Series([writ_sample_total, captured],
                  index=['No Writing Sample'+ ': ' +str(missing_writ_sample),
                         'Captured Data'+ ': ' +str(captured)], name='')

files_graph = files.plot.pie(title='Summary of Files: Writing Sample', autopct='%.2f%%', figsize=(6,6), fontsize=15, colors=['r', 'g'])
#plt.show(files_graph)

correct_data = pd.Series([correct, numb_error, total_writ_error],
                   index=['Correctly Captured'+ ': ' +str(correct),
                          'Numbering Error'+ ': ' +str(numb_error), 
                          'Response Error'+ ': ' +str(total_writ_error)], name='')

data_graph = correct_data.plot.pie(title='Breakdown of Captured Data: Writing Sample', autopct='%.2f%%', figsize=(6,6), fontsize=15, colors=['b', 'c', 'y'])
#plt.show(data_graph)
