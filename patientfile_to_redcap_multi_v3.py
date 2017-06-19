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


os.chdir('/Users/haroonpopal/Desktop/misc/lang_data_to_redcap')

def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

lang_files = find('*.xls', '/Users/haroonpopal/Desktop/misc/lang_data_to_redcap/Patients/')




data = []

# cols will be used to build dataframe off of specific Redcap headers
cols = pd.read_csv('/Users/haroonpopal/Desktop/misc/lang_data_to_redcap/redcap_headers.csv')


single_test = pd.DataFrame()
count = 0


missing_bnt30 = []
missing_wab_commands = []
missing_wab_repetition = []
missing_wab_reading = []

header_error_bnt30 = []
header_error_wab_reading = []


for file in lang_files:  # Iterate through every found excel file
    single_test = pd.DataFrame()
    
    # Find subject's name from file path
    single_test['Subject'] = []
    m = re.search('/Users/haroonpopal/Desktop/misc/lang_data_to_redcap/Patients/LastNameA_F/(.+?)/', file)
    if m:
        found = m.group(1)
    m = re.search('/Users/haroonpopal/Desktop/misc/lang_data_to_redcap/Patients/LastNameG_M/(.+?)/', file)
    if m:
        found = m.group(1)
    m = re.search('/Users/haroonpopal/Desktop/misc/lang_data_to_redcap/Patients/LastNameN_Z/(.+?)/', file)
    if m:
        found = m.group(1)
    single_test.ix[0, 'Subject'] = found    
    
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names
    
    ######################    Boston Naming Test 30    #########################    

os.system('bnt30.py')
#subprocess.call('bnt30.py')

    ##########################     WAB Commands     ############################    
    if 'WAB commands' in sprdshts:
        wab_com = pd.read_excel(file, 'WAB commands', skiprows=1)
        wab_com_notNaN = wab_com[~pd.isnull(wab_com['Unnamed: 0'])]
        wab_com_headers = ['wab_hand', 'wab_eyes', 'wab_point_chair', 
                        'wab_window_door', 'wab_pen_book', 'wab_book_with_pen', 
                        'wab_pen_with_book', 'wab_comb_with_pen', 
                        'wab_comb_with_book', 'wab_pen_book_give', 
                        'wab_comb_pen_turn_book']
        
        temp_df = pd.DataFrame([wab_com_notNaN['Score'].tolist()], 
                                columns=wab_com_headers)
        single_test = pd.concat([single_test, temp_df], axis=1)
        
    else:
        missing_wab_commands.append(file)
        
    
    #########################     WAB Repitition     ###########################    
    if 'WAB Repetition' in sprdshts:
        wab_rep = pd.read_excel(file, 'WAB Repetition', skiprows=1)
        wab_rep_notNaN = wab_rep[~pd.isnull(wab_rep['Unnamed: 0'])]
        wab_rep_headers = []
        for n in range(1,16):
            wab_rep_headers.append('wab_repetition_'+str(n))
            wab_rep_headers.append('wab_repetition_'+str(n)+'_vrbtm')
        
        temp_items = []
        wab_rep_notNaN['Verbatim response if incorrect'] = wab_rep_notNaN['Verbatim response if incorrect'].replace(np.nan, '', regex=True)
        for n in range(0,15):
            temp_items.append(wab_rep_notNaN['Score'][n])
            temp_items.append(wab_rep_notNaN['Verbatim response if incorrect'][n])
        
        temp_df = pd.DataFrame([temp_items], columns=wab_rep_headers)
        single_test = pd.concat([single_test, temp_df], axis=1)
    else:
        missing_wab_repetition.append(file)
    
    ##########################     WAB Reading     #############################    
    if 'WAB Reading' in sprdshts:
        wab_read = pd.read_excel(file, 'WAB Reading', skiprows=1)
        
        if wab_read.empty:
            missing_wab_reading.append(file)
        else:
            wab_read_comp = wab_read.iloc[0:8]
            wab_read_comp_headers = []
            for n in range(1,9):
                wab_read_comp_headers.append('wab_comp_'+str(n))
                wab_read_comp_headers.append('wab_comp_'+str(n)+'_response')
            temp_items = []
            if 'Score' in wab_read_comp:
                wab_read_comp['Patient response if incorrect'] = wab_read_comp['Patient response if incorrect'].replace(np.nan, '', regex=True)
                for n in range(0,8):
                    temp_items.append(wab_read_comp['Score'][n])
                    temp_items.append(wab_read_comp['Patient response if incorrect'][n])
                temp_df = pd.DataFrame([temp_items], columns=wab_read_comp_headers)
                single_test = pd.concat([single_test, temp_df], axis=1)
                
                wab_read_comm = pd.read_excel(file, 'WAB Reading', skiprows=15)
                wab_read_comm = wab_read_comm.iloc[0:6]
                wab_read_comm_headers = []
                for n in range(1,7):
                    wab_read_comm_headers.append('wab_read_comm_'+str(n)+'_read')
                    wab_read_comm_headers.append('wab_read_comm_'+str(n)+'_perf')
                temp_items = []
                for n in range(0,6):
                    temp_items.append(wab_read_comm['Reading score earned'][n])
                    temp_items.append(wab_read_comm['Perf score earned'][n])
                temp_df = pd.DataFrame([temp_items], columns=wab_read_comm_headers)
                single_test = pd.concat([single_test, temp_df], axis=1)
            else:
                header_error_wab_reading.append(file)
    else:
        missing_wab_reading.append(file)
    
    ############################################################################
    # Adding data from each file as a new row
    if count == 0:
        final = single_test
    else:
        final = final.append(single_test)
    count = count + 1











###############################################################################
# Exporting for Redcap import
final.to_csv('import_to_redcap.csv', encoding='utf-8')







###############################################################################
# Questions
## what do then numbers in column A represent? Item numbers?
## How can we get Redcap IDs for all subjects on aphasia?
## How can we get the correct event name? Use API to download all data and see what event should be next?
## Do all of the spreadsheets have the same template per test?
