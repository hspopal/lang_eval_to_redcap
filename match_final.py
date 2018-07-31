import pandas as pd
import csv
import numpy as np
import re

import os
import fnmatch

#work_dir = '/Users/hsp13/Desktop/lang_eval_to_redcap-alexs'
work_dir = os.path.expanduser('~/Dropbox (Partners HealthCare)/Haroon/projects/lang_eval_to_redcap-alexs')
os.chdir(work_dir)

# import tests (bnt30, lang_trans)
master = pd.read_csv(work_dir + '/master.csv', encoding='utf-8')
bnt30 = pd.read_csv(work_dir + '/dataframe_output/bnt30.csv', encoding='utf-8')
cowa = pd.read_csv(work_dir + '/dataframe_output/cowa.csv', encoding='utf-8')
csbwpm = pd.read_csv(work_dir + '/dataframe_output/csb_wpm.csv', encoding='utf-8')
nat = pd.read_csv(work_dir + '/dataframe_output/nat.csv', encoding='utf-8')
pass_ = pd.read_csv(work_dir + '/dataframe_output/pass.csv', encoding='utf-8')
spelling = pd.read_csv(work_dir + '/dataframe_output/spelling.csv', encoding='utf-8')
wab_comm = pd.read_csv(work_dir + '/dataframe_output/wab_comm.csv', encoding='utf-8')
wab_comp_sent = pd.read_csv(work_dir + '/dataframe_output/wab_comp_sent.csv', encoding='utf-8')
wab_read_comm = pd.read_csv(work_dir + '/dataframe_output/wab_read_comm.csv', encoding='utf-8')
wab_repetition = pd.read_csv(work_dir + '/dataframe_output/wab_repetition.csv', encoding='utf-8')

test_list = [bnt30, cowa, csbwpm, nat, pass_, spelling, wab_comm, wab_comp_sent, wab_read_comm, wab_repetition]
test_strings = ['bnt30', 'cowa', 'csbwpm', 'nat', 'pass_', 'spelling', 'wab_comm', 'wab_comp_sent', 'wab_read_comm', 'wab_repetition']
count = 0


for test in test_list:
    match_test = pd.merge(master, test, on=['Subject', 'Date'], how='inner')
    
    match_test = match_test.drop_duplicates(['Subject', 'Date'])
    match_test = match_test.sort_index(by=['Subject', 'Date'], ascending=[True, True])
    if test_strings[0]+'_date' in match_test.columns:
        match_test = match_test.drop(test_strings[0]+'_date', 1)
    match_test = match_test.rename(columns={'Date': test_strings[count]+'_date'})
    
    # Remove tests with no data
    match_test = match_test.dropna(thresh=4)
    
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
    for r in range(1,len(match_test)):
        if match_test['Event_Number'].iloc[r] == 1:
            match_test.ix[r,'redcap_event_name'] = 'static_arm_1'
        else:
            match_test.ix[r,'redcap_event_name'] = 'visit_'+str(int(match_test['Event_Number'].iloc[r]))+'_arm_1'
    
    
    # Load Redcap csv as a dataframe
    redcap_df = pd.read_csv(work_dir + '/DickersonMasterEnrol_DATA_2017-12-06_1437.csv')
    
    # Create a column for IDs in Redcap df that match lang spreadsheet IDs (can just be first and last name)
    redcap_df['Subject'] = redcap_df["name_last"].map(str) + '_' + redcap_df["name_first"]
      
            
    # Pull only subject_id and Subject (to match on). Then add subject_id and data to new df
    redcap_info = redcap_df[['subject_id','Subject']]
    
    
    # Match lang spreadsheets to Redcap
    match_final = pd.merge(redcap_info, match_test, on=['Subject'], how='inner')
    no_match = match_test[~match_test['Subject'].isin(match_final['Subject'])]
    #no_match.to_csv('redcap_format/no_match_'+test_strings[count]+'.csv', encoding='utf8')
    
    
    # Drop unnecessary columns for Redcap
    match_final = match_final.drop(['Event_Number','Subject'], axis=1)
    #keep_cols = [c for c in match_final.columns if c.lower() != 'Unnamed: ']
    match_final = match_final.loc[:, ~match_final.columns.str.contains('Unnamed:')]
    
    # Weird formatting error, this fixes it, idk why
    match_final['subject_id'] = match_final['subject_id'].str.decode('iso-8859-1').str.encode('utf-8')

    
    match_final.to_csv('redcap_format/'+test_strings[count]+'_redcap.csv', encoding='utf8', index=False)
    count = count + 1


