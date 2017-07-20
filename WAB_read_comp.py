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
cols = pd.read_csv(work_dir + '/DickersonMasterEnrollment_ImportTemplate_2017-07-17.csv')

count = 0

missing_wab_reading = []
header_error_wab_reading = []
date_error = []

all_test = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file
    single_test = pd.DataFrame()
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names

    # WAB Reading Comprehension
    if 'WAB Reading' in sprdshts:
        wab_read = pd.read_excel(file, 'WAB Reading', skiprows=1)
        print file
        
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

        if wab_read.empty:
            missing_wab_reading.append(file)
        else:
            wab_read_comp = wab_read.iloc[0:8]
                
            wab_read_comp_headers = []
            for n in range(1, 9): # create header list
                wab_read_comp_headers.append('wab_comp_' + str(n))
                wab_read_comp_headers.append('wab_comp_' + str(n) + '_response')
                wab_read_comp_headers.append('wab_comp_' + str(n) + '_notes')
            temp_items = []
            if 'Score' in wab_read_comp: # get rid of Nan in each column
                wab_read_comp['Patient response if incorrect'] = wab_read_comp['Patient response if incorrect'].fillna('')
                wab_read_comp['Score'] = wab_read_comp['Score'].fillna('')
                wab_read_comp['Score for correct response'] = wab_read_comp['Score for correct response'].fillna('')
                wab_read_comp = wab_read_comp.dropna(axis=1, how='all')
                if len(wab_read_comp.columns) == 5: # create notes column if none
                    wab_read_comp['notes'] = ''
                
                for n in range(0, 8): # add score, response, and notes
                    temp_items.append(wab_read_comp['Score'][n])
                    temp_items.append(wab_read_comp['Patient response if incorrect'][n])
                    temp_items.append(wab_read_comp.iloc[:,5][n])
                
                # create dataframe with data from single patient file
                temp_df = pd.DataFrame([temp_items],
                                       columns=wab_read_comp_headers)
                single_test = pd.concat([single_test, temp_df], axis=1)
            
            else:
                header_error_wab_reading.append(file)
    else:
        missing_wab_reading.append(file)

    all_test = all_test.append(single_test)
    all_test = all_test.drop_duplicates(['Subject', 'Date'])
    
all_test.to_csv('WAB_read_comp.csv', encoding='utf-8')
