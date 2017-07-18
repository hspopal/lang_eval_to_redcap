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
# cols = pd.read_csv(work_dir + '/redcap_headers.csv')
cols = pd.read_csv(work_dir + '/DickersonMasterEnrollment_ImportTemplate_2017-07-17.csv')

count = 0

date_error = []
missing_bnt30 = []
missing_wab_commands = []
missing_wab_repetition = []
missing_wab_reading = []

header_error_bnt30 = []
header_error_wab_reading = []

missing_transcr = []
transcr_response_error = []

all_test = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file
    single_test = pd.DataFrame()
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names

    # WAB Commands
    if 'WAB commands' in sprdshts:
        # Find subject's name from file path
        single_test['Subject'] = []
        print file
        
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

        wab_com = pd.read_excel(file, 'WAB commands', skiprows=1)
        wab_com_notNaN = wab_com[~pd.isnull(wab_com['Unnamed: 0'])] 
        if len(wab_com_notNaN.columns) < 5:
            wab_com_notNaN['notes'] = ''
        
        wab_com_headers = ['wab_commands_date', 'wab_hand', 'wab_hand_notes',
                           'wab_eyes', 'wab_eyes_notes', 'wab_point_chair', 'wab_point_chair_notes',
                           'wab_window_door', 'wab_window_door_notes', 'wab_pen_book', 'wab_pen_book_notes',
                           'wab_book_with_pen', 'wab_book_with_pen_notes',
                           'wab_pen_with_book', 'wab_pen_with_book_notes', 'wab_comb_with_pen', 'wab_comb_with_pen_notes',
                           'wab_comb_with_book', 'wab_comb_with_book_notes', 'wab_pen_book_give', 'wab_pen_book_give_notes',
                           'wab_comb_pen_turn_book', 'wab_comb_pen_turn_book_notes', 'wab_comm_gen_notes']
        
        temp_items = [date]
        for i in wab_com_notNaN.index:
            temp_items.append(wab_com_notNaN['Score'][i])
            temp_items.append(wab_com_notNaN.iloc[:,4][i])
        
        temp_items.append('')
        
        temp_df = pd.DataFrame([temp_items],
                               columns=wab_com_headers)
        single_test = pd.concat([single_test, temp_df], axis=1)

    else:
        missing_wab_commands.append(file)
    
    all_test = all_test.append(single_test)

all_test = all_test.drop_duplicates(['Subject', 'Date'])
all_test.to_csv('WAB_comm.csv', encoding='utf-8')
