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

wab_read_total = []
missing_wab_reading = [] # file doesnt have wab reading (2)
missing_read_comm = [] # the wab reading sheet doesnt have command test (3)
wab_reading_comm_head_error = [] # the columns are incorrectly named (2)
date_error = []

header_error_wab_reading = []

all_test = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file
    single_test = pd.DataFrame()
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names
    
    if 'WAB Reading' in sprdshts:
        wab_read = pd.read_excel(file, 'WAB Reading', skiprows=1)
        print file
        wab_read_total.append(file)
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
            wab_read_comm = pd.read_excel(file, 'WAB Reading', skiprows=15)
            wab_read_comm = wab_read_comm.iloc[0:6]
            if wab_read_comm.empty:
                missing_read_comm.append(file)
            else:
                if len(wab_read_comm.columns) == 6:
                    wab_read_comm['Unnamed: 6'] = ''
                else:
                    wab_read_comm_headers = []
                    for n in range(1, 7): # create header list
                        wab_read_comm_headers.append('wab_read_comm_'+str(n)+'_read')
                        wab_read_comm_headers.append('wab_read_comm_'+str(n)+'_perf')
                        wab_read_comm_headers.append('wab_read_comm_'+str(n)+'_notes')
                    temp_items = []
                    if wab_read_comm.columns[2] != 'Reading score earned':
                        wab_reading_comm_head_error.append(file)
                    elif wab_read_comm.columns[4] != 'Perf score earned':
                        wab_reading_comm_head_error.append(file)
                    else:
                        for n in range(0, 6): 
                            temp_items.append(wab_read_comm['Reading score earned'][n])
                            temp_items.append(wab_read_comm['Perf score earned'][n])
                            temp_items.append(wab_read_comm.iloc[:,6][n])
                        temp_df = pd.DataFrame([temp_items], columns=wab_read_comm_headers)
                        single_test = pd.concat([single_test, temp_df], axis=1)
    else:
        header_error_wab_reading.append(file)
    
    all_test = all_test.append(single_test)

all_test = all_test.drop_duplicates(['Subject', 'Date'])
all_test.to_csv('WAB_read_comm.csv', encoding='utf-8')
