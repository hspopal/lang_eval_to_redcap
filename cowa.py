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
redcap_cols = filter(lambda x: x.startswith('cowa_'), cols)
###############################################################################


#single_test = pd.DataFrame()

cowa_total = []
missing_cowa = []
cowa_letter_error = [] # header error
empty_cowa = []
date_error = []

cowa_df = pd.DataFrame()
all_test = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file
    
    if '/.' in file:  # If file is a hidden file, skip
        continue
        
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names    
    
    # COWA

    if 'COWA' in sprdshts:
        cowa_total.append(file)
        #cowa = pd.read_excel(file, 'COWA', skiprows=2)
        cowa = xl.parse('COWA', skiprows=2, index_col=None, na_values=['NA'])
        cowa_headers = cowa.loc[0].tolist()
        
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
        
        
        temp_df = cowa.dropna(axis=0, how='all')[:-5]

        if temp_df.empty:
            empty_cowa.append(file)
        else:
            #temp_df = cowa.dropna(axis=0, how='all')[:-5]
            
            temp_df = temp_df.replace(np.nan, '', regex=True)
            temp_df = temp_df.select_dtypes(['object'])
            for col in temp_df.columns[1:]:
                temp_df[col] = temp_df[col].str.replace(u'\N{REGISTERED SIGN}', '(repeated)')
                temp_df = temp_df.replace(np.nan, '', regex=True)
                for n in temp_df.index:
                    temp_df[col][n] = temp_df[col][n].replace(u'\u2019', "'")
            
            # find header error
            letter_error = []
            if 'F' not in temp_df.columns:
                letter_error.append('F')
            if 'A' not in temp_df.columns:
                letter_error.append('A')
            if 'S' not in temp_df.columns:
                letter_error.append('S')
            if 'animals' not in temp_df.columns:
                letter_error.append('animals')
            if 'vegetables' not in temp_df.columns:
                letter_error.append('vegetables')
            
            if len(letter_error) != 0:
                cowa_letter_error.append([file, letter_error])
            
            else:
                # make list of non-Nan items in each column
                """F = str(temp_df['F'].dropna().astype(str).tolist())[1:-1]
                A = str(temp_df['A'].dropna().astype(str).tolist())[1:-1]
                #overall_notes = raw_csb_wpm.iloc[:,10].astype(str).values  # this gets rid of the u'
                #overall_notes = filter(None, overall_notes)
                #csb_wpm['csbwpm_overall_notes'] = ", ".join(overall_notes)
                S = str(temp_df['S'].dropna().astype(str).tolist())[1:-1]
                animals = temp_df['animals'].dropna().astype(str).tolist()
                animals = [str(item) for item in animals]
                vegetables = temp_df['vegetables'].dropna().tolist()
                animals = [str(item) for item in vegetables]"""
                
                temp_df['F'].replace(u'', np.nan, inplace=True)
                single_test['cowa_f'] = ', '.join(temp_df['F'].dropna().astype(str).tolist())
                temp_df['A'].replace('', np.nan, inplace=True)
                single_test['cowa_a'] = ', '.join(temp_df['A'].dropna().astype(str).tolist())
                #overall_notes = raw_csb_wpm.iloc[:,10].astype(str).values  # this gets rid of the u'
                #overall_notes = filter(None, overall_notes)
                #csb_wpm['csbwpm_overall_notes'] = ", ".join(overall_notes)
                temp_df['S'].replace('', np.nan, inplace=True)
                single_test['cowa_s'] = ', '.join(temp_df['S'].dropna().astype(str).tolist())
                temp_df['animals'].replace('', np.nan, inplace=True)
                single_test['cowa_animals'] = ', '.join(temp_df['animals'].dropna().astype(str).tolist())
                temp_df['vegetables'].replace('', np.nan, inplace=True)
                single_test['cowa_veg'] = ', '.join(temp_df['vegetables'].dropna().astype(str).tolist())
                
                
                
                scores_df = cowa.dropna(axis=0, how='all')[-5:].reset_index()
                scores_df = scores_df.drop('index', axis=1)
                
                # using "total correct" instead of 'total words'
                single_test['cowa_f_total'] = scores_df['F'][0]
                single_test['cowa_f_intrusions'] = scores_df['F'][1]
                single_test['cowa_f_repetitions'] = scores_df['F'][2]
                single_test['cowa_a_total'] = scores_df['A'][0]
                single_test['cowa_a_intrusions'] = scores_df['A'][1]
                single_test['cowa_a_repetitions'] = scores_df['A'][2]
                single_test['cowa_s_total'] = scores_df['S'][0]
                single_test['cowa_s_intrusions'] = scores_df['S'][1]
                single_test['cowa_s_repetitions'] = scores_df['S'][2]
                single_test['cowa_animals_total'] = scores_df['animals'][0]
                single_test['cowa_animals_intrusions'] = scores_df['animals'][1]
                single_test['cowa_animals_repetitions'] = scores_df['animals'][2]
                single_test['cowa_veg_total'] = scores_df['vegetables'][0]
                single_test['cowa_veg_intrusions'] = scores_df['vegetables'][1]
                single_test['cowa_veg_repetitions'] = scores_df['vegetables'][2]
                
                #if file not in missing_cowa:
                #    complete = 'yes'
                #else:
                #    complete = 'no'
    
                #temp_list = [date, '', F, F_total, F_intr, F_rep,
                #            A, A_total, A_intr, A_rep,
                #            S, S_total, S_intr, S_rep,
                #            animals, ani_total, ani_intr, ani_rep,
                #            vegetables, veg_total, veg_intr, veg_rep, '', complete]
                #dict_keys = [col for col in cols.columns if 'cowa_' in col]
                # Define a dictionary to be used to create a dataframe
                #cowa_dict = {}
                #count = 0
                #for list in temp_list:
                #    cowa_dict{dict_keys[0]: temp_list[0]}
    
                # create df for test results of one file
                #cowa_df = pd.DataFrame([temp_list], columns=redcap_cols)
                #single_test = pd.concat([single_test, cowa_df], axis=1)
        all_test = all_test.append(single_test)
        
    else:
        missing_cowa.append(file)

    # add file data to growing df for all file data
    
all_test = all_test.drop_duplicates(['Subject', 'Date'])
#all_test = all_test.rename(columns={'cowa_date': 'Date'})
all_test.to_csv('dataframe_output/cowa.csv', encoding='utf-8', index=False)

# find size of errors
no_cowa = len(missing_cowa)
captured = (len(cowa_total))
correct = (len(cowa_total)-len(cowa_letter_error))
empty = len(empty_cowa)
letter_error = len(cowa_letter_error)

