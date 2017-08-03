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

test_list = pd.DataFrame()
count = 0
date_error = []

for file in lang_files:  # Iterate through every found excel file
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names 
    single_list = ['','','no','no','no','no','no','no','no','no','no']
    tests = ['Subject', 'Date', 'BNT30','Lang Transcription','WAB Repetition', 'WAB Read Comm', 'WAB Read Comp', 'WAB Comm', 'COWA', 'Spelling', 'Writing Samples']

    # Find subject's name from file path
    m = re.search(work_dir + '/Patients/LastNameA_F/(.+?)/', file)
    if m:
        found = m.group(1)
    m = re.search(work_dir + '/Patients/LastNameG_M/(.+?)/', file)
    if m:
        found = m.group(1)
    m = re.search(work_dir + '/Patients/LastNameN_Z/(.+?)/', file)
    if m:
        found = m.group(1)
    single_list[0] = found
    
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
                            single_list[1] = ''
                        else:
                            date = datetime.strptime((match.group())[1:], '%m%d%y').date()
                            single_list[1] = str(date)
                    else:
                        date = datetime.strptime((match.group()), '%m.%d.%y').date()
                        single_list[1] = str(date)
                else:
                    date = datetime.strptime((match.group()), '%m_%d_%y').date()
                    single_list[1] = str(date)
            else:
                date = datetime.strptime((match.group())[:-4], '%m%d%y').date()
                single_list[1] = str(date)
        else:
            date = datetime.strptime((match.group())[:-1], '%m%d%y').date()
            single_list[1] = str(date)
    else:
        date = datetime.strptime((match.group())[1:-1], '%m%d%y').date()
        single_list[1] = str(date)
        
    if 'BNT30' in sprdshts:
        single_list[2] = 'yes'
    if 'Lang transcriptions' in sprdshts:
        single_list[3] = 'yes'
    if 'WAB Repetition' in sprdshts:
        single_list[4] = 'yes'
    if 'WAB Reading' in sprdshts:
        single_list[5] = 'yes'
        single_list[6] = 'yes'
    if 'WAB commands' in sprdshts:
        single_list[7] = 'yes'
    if 'COWA' in sprdshts:
        single_list[8] = 'yes'
    if 'Spelling' in sprdshts:
        single_list[9] = 'yes'
    if 'Writing samples' in sprdshts:
        single_list[10] = 'yes'
    
    single_test = pd.DataFrame([single_list], columns=tests)
    
    test_list = test_list.append(single_test)

test_list = test_list.sort_index(by=['Subject', 'Date'], ascending=[True, True])
test_list = test_list.replace('yes', '')
test_list.to_csv('test_list.csv', encoding='utf-8')
