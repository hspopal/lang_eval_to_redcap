# -*- coding: utf-8 -*-
import pandas as pd
import csv
import numpy as np
import re

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
#lang_files = [work_dir + '/Patients/LastNameA_F/Adamian_Daniel/010815/adamian_lang_010815.xls']
#lang_files = [work_dir + '/Patients/LastNameA_F/Blake, Franklin Howard/022015/lang_FB.xls']

data = []

# cols will be used to build dataframe off of specific Redcap headers
cols = pd.read_csv(work_dir + '/redcap_headers.csv')

ID = pd.DataFrame()
count = 0

date_error = []

ID_error_firstname = []
ID_error_lastname = []
ID_error_date = []
ID_error = []

# Load Redcap csv as a dataframe

redcap_df = pd.read_csv(work_dir + '/DickersonMasterEnrol_DATA_2017-07-12_1344.csv')

# pull only relevant columns
# redcap_id, event, bnt30, wab, etc.

bnt30_col = []
lang_col = []
wab_rep_col = []

relevant_columns = ['subject_id', 'Subject', 'redcap_event_name', 'name_last']

redcap_relevant = redcap_df.iloc[:, 0:8]

# Create a column for IDs in Redcap df that match lang spreadsheet IDs
redcap_relevant['Subject'] = redcap_relevant["name_last"].map(str) + '_' + redcap_relevant["name_first"]

for file in lang_files:  # Iterate through every found excel file
    single_ID = pd.DataFrame()

    # Find subject's name from file path
    single_ID['Subject'] = []
    m = re.search(work_dir + '/Patients/LastNameA_F/(.+?)/', file)
    if m:
        found = m.group(1)
    m = re.search(work_dir + '/Patients/LastNameG_M/(.+?)/', file)
    if m:
        found = m.group(1)
    m = re.search(work_dir + '/Patients/LastNameN_Z/(.+?)/', file)
    if m:
        found = m.group(1)
    single_ID.ix[0, 'Subject'] = found
    
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
                            single_ID.ix[0, 'Date'] = ''
                        else:
                            date = datetime.strptime((match.group())[1:], '%m%d%y').date()
                            single_ID.ix[0, 'Date'] = str(date)
                    else:
                        date = datetime.strptime((match.group()), '%m.%d.%y').date()
                        single_ID.ix[0, 'Date'] = str(date)
                else:
                    date = datetime.strptime((match.group()), '%m_%d_%y').date()
                    single_ID.ix[0, 'Date'] = str(date)
            else:
                date = datetime.strptime((match.group())[:-4], '%m%d%y').date()
                single_ID.ix[0, 'Date'] = str(date)
        else:
            date = datetime.strptime((match.group())[:-1], '%m%d%y').date()
            single_ID.ix[0, 'Date'] = str(date)
    else:
        date = datetime.strptime((match.group())[1:-1], '%m%d%y').date()
        single_ID.ix[0, 'Date'] = str(date)
    
    if single_ID['Date'] is None:
        ID_error_date.append(file)
            
    ID = ID.append(single_ID)

ID['Subject'] = ID['Subject'].str.replace(', ', '_')

ID = ID.reset_index()
ID = ID.drop('index', axis=1)
ID['name_first'] = ID['Subject'].str.extract('.+?_(.*)', expand=True)
ID['First_Initial'] = ID['name_first'].astype(str).str[0]
ID['name_last'] = ID['Subject'].str.extract('(.*)_.+?', expand=True)

ID_lower = ID['First_Initial'] + (ID['name_last'].astype
                                  (str).str[:3]) + '_'
ID['ID'] = ID_lower.str.upper()

# Match Index: maps values from redcap[subject_id] based on values that match in redcap[name_last] and ID[name_last]

redcap_relevant.set_index('Subject',inplace=True)
redcap_relevant_map = redcap_relevant.iloc[:,0].to_dict()
ID['PatientID']=ID.Subject.map(redcap_relevant_map)

error = ID['PatientID'].isnull().sum()

ID.to_csv('PatientID.csv')
