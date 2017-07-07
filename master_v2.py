import pandas as pd
import csv
import numpy as np
import re

import os
import fnmatch

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
#lang_files = [work_dir +
 #             '/Patients/LastNameA_F/Adamian_Daniel'
  #            '/010815/adamian_lang_010815.xls']

data = []

# cols will be used to build dataframe off of specific Redcap headers
#cols = pd.read_csv(work_dir + '/redcap_headers.csv')

count = 0
# single_test = pd.DataFrame()
# final = pd.DataFrame()

missing_bnt30 = []
header_error_bnt30 = []
temp_head_errors = []

missing_wab_commands = []
missing_wab_repetition = []
missing_wab_reading = []
header_error_wab_reading = []

missing_transcr = []
transcr_response_error = []

missing_cowa = []
missing_writ_sample = []
sample_error = []

missing_spelling = []
header_error_spelling = []

missing_ppt = []
header_error_ppt = []

missing_verb = []
verb_error = []

missing_nat = []

missing_aprax_screen = []

missing_csb_wpm = []

all_test = pd.DataFrame()

for file in lang_files:  # Iterate through every found excel file
    
    # save file as txt to read in bnt30_v2

    with open(work_dir + '/filepath.txt', 'w') as txt:
        txt.write(file)

    single_test = pd.DataFrame()
    final = pd.DataFrame()
        
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

    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names    
       
    # Boston Naming Test 30
    if 'BNT30' in sprdshts:
        os.system('python bnt30_v2.py file')
        header_error_bnt30.append(temp_head_errors)
        bnt30_test = pd.read_csv(work_dir + 'bnt30_test.csv')
        final = pd.concat([final, bnt30_test], axis=1)
    else:
        missing_bnt30.append(file)
    
    # Lang Transcriptions
    if 'Lang transcriptions' in sprdshts:
        os.system('python lang_transcr2.py file')
        lang_trans_test = pd.read_csv(work_dir + 'lang_trans_test.csv')
        final = pd.concat([final, lang_trans_test], axis=1)
        print file
    else:
        missing_transcr.append(file)

    # WAB Commands

    # os.system('WAB_command.py')

    # WAB Repitition
    
    if 'WAB Repetition' in sprdshts:
        os.system('python WAB_repitition.py file')
        wab_rep_test = pd.read_csv(work_dir + 'wab_rep_test.csv')
        final = pd.concat([final, wab_rep_test], axis=1, join='inner')
    else:
        missing_wab_repetition.append(file)
    
    # WAB Reading

    # os.system('WAB_read_comm.py')
    # os.system('WAB_read_comp.py')

    # Adding data from each file as a new row
    #if count == 0:
        #final = single_test
    #else:
        #final = final.append(single_test)
    #count = count + 1

    all_test = pd.concat([all_test, final], axis=0, ignore_index=True) 

# FOR EACH TEST, PUT RESULTS IN A 'SING TEST' LIST TYPE THING/DF, THEN COMBINE AT END INTO FINAL DF

# Exporting for Redcap import
all_test.to_csv('import_to_redcap.csv', encoding='utf-8')


# Questions
# what do then numbers in column A represent? Item numbers?
# How can we get Redcap IDs for all subjects on aphasia?
# How can we get the correct event name?
# Use API to download all data and see what event should be next?
# Do all of the spreadsheets have the same template per test?
