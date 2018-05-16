import pandas as pd
import csv
import numpy as np
import re
import glob

import os
import fnmatch
from datetime import datetime

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
#redcap_cols = cols.columns.tolist()
redcap_cols = filter(lambda k: 'csbwpm' in k, cols)
###############################################################################


single_test = pd.DataFrame()
date_error = []
total_files = []

csb_wpm_total = []
csb_wpm_script_error = []
missing_csb_wpm_file = []

all_test = pd.DataFrame()
missing_data = pd.DataFrame()


for file in lang_files:  # Iterate through every found excel file    
    # Cambridge Semantic Battery - Word Picture Matching
    single_test = pd.DataFrame()
    csb_wpm = pd.DataFrame()
    
    if '/.' in file:  # If file is a hidden file, skip
        continue
    
    xl = pd.ExcelFile(file)
    sprdshts = xl.sheet_names  # see all sheet names
    
    if 'CSB Category Comp' in sprdshts or 'CSB WPM' in sprdshts:
        csb_wpm_total.append(file)
        raw_csb_wpm = pd.ExcelFile(file)
        if 'CSB Category Comp' in sprdshts:
            raw_csb_wpm = raw_csb_wpm.parse('CSB Category Comp', skiprows=15, index_col=None, na_values=['NA'])
        if 'CSB WPM' in sprdshts:
            raw_csb_wpm = raw_csb_wpm.parse('CSB WPM', skiprows=15, index_col=None, na_values=['NA'])
        raw_csb_wpm = raw_csb_wpm.replace(np.nan, '', regex=True)
        
        # Group column responses and notes
        items = raw_csb_wpm[::4]
        
        csb_wpm = pd.DataFrame(columns=redcap_cols)
        x = 2
        for n in range(1,9):
            csb_wpm['csbwpm'+str(n)+'_domestic'] = [raw_csb_wpm.iloc[1][n]]
            csb_wpm['csbwpm'+str(n)+'_foreign'] = [raw_csb_wpm.iloc[5][n]]
            csb_wpm['csbwpm'+str(n)+'_bird'] = [raw_csb_wpm.iloc[9][n]]
            csb_wpm['csbwpm'+str(n)+'_fruit'] = [raw_csb_wpm.iloc[13][n]]
            csb_wpm['csbwpm'+str(n)+'_veh'] = [raw_csb_wpm.iloc[17][n]]
            csb_wpm['csbwpm'+str(n)+'_largeitem'] = [raw_csb_wpm.iloc[21][n]]
            csb_wpm['csbwpm'+str(n)+'_handheld'] = [raw_csb_wpm.iloc[25][n]]
            csb_wpm['csbwpm'+str(n)+'_tool'] = [raw_csb_wpm.iloc[29][n]]
            
            csb_wpm['csbwpm'+str(n)+'_domestic'] = csb_wpm['csbwpm'+str(n)+'_domestic'].astype(str)
            csb_wpm['csbwpm'+str(n)+'_foreign'] = csb_wpm['csbwpm'+str(n)+'_foreign'].astype(str)
            csb_wpm['csbwpm'+str(n)+'_bird'] = csb_wpm['csbwpm'+str(n)+'_bird'].astype(str)
            csb_wpm['csbwpm'+str(n)+'_fruit'] = csb_wpm['csbwpm'+str(n)+'_fruit'].astype(str)
            csb_wpm['csbwpm'+str(n)+'_veh'] = csb_wpm['csbwpm'+str(n)+'_veh'].astype(str)
            csb_wpm['csbwpm'+str(n)+'_largeitem'] = csb_wpm['csbwpm'+str(n)+'_largeitem'].astype(str)
            csb_wpm['csbwpm'+str(n)+'_handheld'] = csb_wpm['csbwpm'+str(n)+'_handheld'].astype(str)
            csb_wpm['csbwpm'+str(n)+'_tool'] = csb_wpm['csbwpm'+str(n)+'_tool'].astype(str)
            
            for y in range(1,9):
                #print(csb_wpm['csbwpm_'+str(items.iloc[n-1,y])+'_error'])
                #print(str(raw_csb_wpm.iloc[x][y]))
                #print('-------------------')
                error_item = str(items.iloc[n-1,y])
                error_item = error_item.replace(" ", "")  # Remove characters to match redcap field name
                error_item = error_item.replace("ing", "")
                error_item = error_item.replace("rhinoceros", "rhino")
                error_item = error_item.replace("bicycle", "bike")
                csb_wpm['csbwpm_'+error_item+'_error'] = str(raw_csb_wpm.iloc[x][y])
            x = x + 4
            
            col_notes = raw_csb_wpm.iloc[31:,n].astype(str).values
            col_notes = filter(None, col_notes)
            csb_wpm['csbwpm_column'+str(n)+'_notes'] = ", ".join(col_notes)
        # Check results
        #print(csb_wpm.filter(regex='domestic'))
        
        # Grab all notes to the very right and add to overall notes section
        overall_notes = raw_csb_wpm.iloc[:,10].astype(str).values  # this gets rid of the u'
        overall_notes = filter(None, overall_notes)
        csb_wpm['csbwpm_overall_notes'] = ", ".join(overall_notes)
        
        
        
        if not csb_wpm.empty:
            single_test = pd.DataFrame()
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
        
            date = re.findall('\d\d\d\d\d\d+', file)
            #date = date[0]
            if not date:
                csb_wpm['Date'] = ''
            else:
                date = datetime.strptime(date[0], '%m%d%y')
                csb_wpm['Date'] = date.strftime('%Y-%m-%d')
            #single_test.ix[0, 'Date'] = date.strftime('%Y-%m-%d')
            single_test = pd.concat([csb_wpm, single_test], axis=1, join='inner')
            check_empty = single_test
            check_empty = single_test.replace('', np.nan)
            check_empty = check_empty.dropna(axis=1)
            if check_empty.drop(['Subject','Date'], axis=1).empty:
                missing_data = missing_data.append(single_test)
            elif (single_test['csbwpm_penguin_error'].iloc[0] == 'chicken') & (single_test['csbwpm_train_error'].iloc[0] == 'airplane'):
                if (check_empty.drop(['csbwpm_penguin_error','csbwpm_train_error','Subject','Date'], axis=1).empty):
                    missing_data = missing_data.append(single_test)
                else:
                    all_test = all_test.append(single_test)
            else:
                all_test = all_test.append(single_test)
        

    else:
        missing_csb_wpm_file.append(file)
   
    
    
all_test = all_test.drop_duplicates(['Subject', 'Date'])

csb_wpm_patients = pd.DataFrame()
csb_wpm_patients = all_test.groupby(all_test['Subject'].tolist(),as_index=False).size() # 109 out of 126 total

all_test.to_csv('dataframe_output/csbwpm.csv', encoding='utf-8', index = False)







##########################################################################
# Match Redcap IDs and Event Names
"""
master = pd.read_csv(work_dir + '/master.csv', encoding='utf-8')
csb_wpm = pd.read_csv(work_dir + '/dataframe_output/csb_wpm-Final.csv', encoding='utf-8')


match_test = pd.merge(master, csb_wpm, on=['Subject', 'Date'], how='inner')

match_test = match_test.drop_duplicates(['Subject', 'Date'])
match_test = match_test.sort_index(by=['Subject', 'Date'], ascending=[True, True])

# Create a placeholder column for the event number, or the nth test
match_test = match_test.reset_index(drop=True)
match_test['Event_Number'] = np.nan
match_test['Event_Number'] = match_test['Event_Number'].fillna(0)
match_test.ix[0,'Event_Number'] = 1
for r in range(1,len(match_test)):
    if match_test['Subject'].iloc[r] == match_test['Subject'].iloc[r-1]:
        match_test.ix[r,'Event_Number'] = int(match_test['Event_Number'].iloc[r-1]) + 1
    else:
        match_test.ix[r,'Event_Number'] = 1

# Create the event name
match_test['redcap_event_name'] = ""
match_test.ix[0,'redcap_event_name'] = 'static_arm_1'
for r in range(1,286):
    if match_test['Event_Number'].iloc[r] == 1:
        match_test.ix[r,'redcap_event_name'] = 'static_arm_1'
    else:
        match_test.ix[r,'redcap_event_name'] = 'visit_'+str(int(match_test['Event_Number'].iloc[r]))+'_arm_1'


match_test.to_csv('match_test.csv', encoding='utf-8')

# Manually edited subjects who will end up being in no_match


#match_test = pd.read_csv(work_dir + '/match_test_edited.csv')


# Load Redcap csv as a dataframe

redcap_df = pd.read_csv(work_dir + '/DickersonMasterEnrol_DATA_2017-12-06_1437.csv')

# Create a column for IDs in Redcap df that match lang spreadsheet IDs (can just be first and last name)

redcap_df['Subject'] = redcap_df["name_last"].map(str) + '_' + redcap_df["name_first"]


# pull only relevant columns
## redcap_id, event, bnt30, wab, etc.
"""

#def change_encode(data, cols):
#    for col in cols:
#        data[col] = data[col].str.decode('iso-8859-1').str.encode('utf-8')
#    return

#change_encode(match_final, match_final.columns)


