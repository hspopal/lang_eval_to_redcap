import pandas as pd
import csv
import numpy as np
import re

import os, fnmatch


###############################################################################
##########################    New Version Updates   ###########################
###############################################################################
# Capture all subject lang files
# Skip spreadsheets that have errors for missing tabs, or ill formatted headers
# Create a seperate list for each error with failed subjects/files
###############################################################################


work_dir = '/Users/axs97/Desktop/lang_eval_to_redcap-alexs' 

os.chdir(work_dir)

def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

#lang_files = find('*.xls', work_dir + '/Patients/')
lang_files = [work_dir + '/Patients/LastNameA_F/Adamian_Daniel/010815/adamian_lang_010815.xls']

data = []

# cols will be used to build dataframe off of specific Redcap headers
cols = pd.read_csv(work_dir + '/redcap_headers.csv')


single_test = pd.DataFrame()
count = 0

missing_transcr = []

for file in lang_files:  # Iterate through every found excel file
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
    #single_test.ix[0, 'Subject'] = found
    
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names
    
    ######################    Language Transcription    #########################    
    if 'Lang transcriptions' in sprdshts:
        lang_trans = pd.read_excel(file, 'Lang transcriptions')
        headers = lang_trans.loc[3].tolist()
        headers[0] = 'item'
            
        lang_prompts = ['1. Describe a typical Sunday', 
        '2. Describe what you did for work, or, describe where you grew up, or, how did you meet your spouse?', 
        '3. WAB picnic scene', 
        '4. Sherman picture 1', 
        '5. Sherman picture 2', 
        '6. Brookshire picture sequences']
                
        lang_trans.columns = ['prompts', 'none', 'response']
        
        lang_items = lang_trans.index.tolist()
        for i in lang_items:
            #transcription = ['', '', '', '', '', '', '']
            trans_clear = lang_trans.fillna('')

            if ('1.' in trans_clear.loc[i]['response']) == True:
                response1 = lang_trans.at[i, 'response']
            else:
                response1 = ''

            if ('2.' in trans_clear.loc[i]['response']) == True:
                response2 = lang_trans.at[i, 'response']
            else:
                response2 = ''
                
            if ('3.' in trans_clear.loc[i]['response']) == True:
                response3 = lang_trans.at[i, 'response']
            else:
                response3 = ''
                
            if ('4.' in trans_clear.loc[i]['response']) == True:
                response4 = lang_trans.at[i, 'response']
            else:
                response4 = ''
                
            if ('5.' in trans_clear.loc[i]['response']) == True:
                response5 = lang_trans.at[i, 'response']
            else:
                response5 = ''
                                    
            if ('6.' in trans_clear.loc[i]['response']) == True:
                response6 = lang_trans.at[i, 'response']
            else:
                response6 = ''
                                
        transcription =  [response1, response2, response3, response4, response5, response6, '']

        trans_df = pd.DataFrame(data = [transcription], columns = [col for col in cols.columns if 'lang_transcr_' in col])

        single_test = pd.concat([single_test, trans_df], axis=1)
            
    else:
        missing_transcr.append(file)
