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
# lang_files = [work_dir + '/Patients/LastNameA_F/Adamian_Daniel/010815/adamian_lang_010815.xls']

data = []

# cols will be used to build dataframe off of specific Redcap headers
# cols = pd.read_csv(work_dir + '/redcap_headers.csv')
cols = pd.read_csv(work_dir + '/DickersonMasterEnrollment_ImportTemplate_2017-07-17.csv')

single_test = pd.DataFrame()
count = 0

missing_bnt30 = []
missing_wab_commands = []
missing_wab_repetition = []
missing_wab_reading = []

header_error_bnt30 = []
header_error_wab_reading = []

missing_transcr = []
transcr_response_error = []

cowa_total = []
missing_cowa = []
cowa_letter_error = []
date_error = []

cowa_df = pd.DataFrame()
all_test = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names    
    
    # COWA

    if 'COWA' in sprdshts:
        cowa_total.append(file)
        cowa = pd.read_excel(file, 'COWA', skiprows=2)
        cowa_headers = cowa.loc[0].tolist()
        
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
            date = str(date)
            single_test.ix[0, 'Date'] = str(date)

        if cowa.empty:
            missing_cowa.append(file)
        else:
            temp_df = cowa.dropna(axis=0, how='all')[:-5]
            
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
                F = str(temp_df['F'].dropna().tolist())[1:-1]
                A = str(temp_df['A'].dropna().tolist())[1:-1]
                S = str(temp_df['S'].dropna().tolist())[1:-1]
                animals = str(temp_df['animals'].dropna().tolist())[1:-1]
                vegetables = str(temp_df['vegetables'].dropna().tolist())[1:-1]
                
                scores_df = cowa.dropna(axis=0, how='all')[-5:].reset_index()
                scores_df = scores_df.drop('index', axis=1)
                
                # using "total correct" instead of 'total words'
                F_total = scores_df['F'][3]
                F_intr = scores_df['F'][1]
                F_rep = scores_df['F'][2]
                A_total = scores_df['A'][3]
                A_intr = scores_df['A'][1]
                A_rep = scores_df['A'][2]
                S_total = scores_df['S'][3]
                S_intr = scores_df['S'][1]
                S_rep = scores_df['S'][2]
                ani_total = scores_df['animals'][3]
                ani_intr = scores_df['animals'][1]
                ani_rep = scores_df['animals'][2]
                veg_total = scores_df['vegetables'][3]
                veg_intr = scores_df['vegetables'][1]
                veg_rep = scores_df['vegetables'][2]
                
                if file not in missing_cowa:
                    complete = 'yes'
                else:
                    complete = 'no'
    
                temp_list = [date, '', F, F_total, F_intr, F_rep,
                            A, A_total, A_intr, A_rep,
                            S, S_total, S_intr, S_rep,
                            animals, ani_total, ani_intr, ani_rep,
                            vegetables, veg_total, veg_intr, veg_rep, '', complete]
    
                cowa_df = pd.DataFrame([temp_list], columns=[col for col in cols.columns if 'cowa_' in col])
                single_test = pd.concat([single_test, cowa_df], axis=1)
        
    else:
        missing_cowa.append(file)

    all_test = all_test.append(single_test)
    all_test = all_test.drop_duplicates(['Subject', 'cowa_date'])
all_test.to_csv('COWA-final.csv', encoding='utf-8')
