import pandas as pd
import csv
import numpy as np

import os
from datetime import datetime


# Must be connected to aphasia in order for scripts to capture data


work_dir = os.path.expanduser('~/Dropbox (Partners HealthCare)/Haroon/projects/lang_eval_to_redcap-alexs')
os.chdir(work_dir)


test_strings = ['bnt30', 'cowa', 'csbwpm', 'nat', 'pass', 'spelling', 'wab_commands', 'wab_reading', 'wab_repetition']
#test_strings = ['bnt30']
count = 0



##########################################################################
# Run script to capture all subject level data for each test
for test in test_strings:    
    print '\n\n\n\n\nrunning '+test+'...'
    os.system('python scripts/'+test+'.py file')
    

# import tests as dataframes
master = pd.read_csv(work_dir + '/master.csv', encoding='utf-8')  # Master list of all subjects from Redcap
bnt30 = pd.read_csv(work_dir + '/dataframe_output/bnt30.csv', encoding='utf-8')
cowa = pd.read_csv(work_dir + '/dataframe_output/cowa.csv', encoding='utf-8')
csbwpm = pd.read_csv(work_dir + '/dataframe_output/csbwpm.csv', encoding='utf-8')
nat = pd.read_csv(work_dir + '/dataframe_output/nat.csv', encoding='utf-8')
pass_ = pd.read_csv(work_dir + '/dataframe_output/pass.csv', encoding='utf-8')
spelling = pd.read_csv(work_dir + '/dataframe_output/spelling.csv', encoding='utf-8')
wab_commands = pd.read_csv(work_dir + '/dataframe_output/wab_comm.csv', encoding='utf-8')
#wab_comp_sent = pd.read_csv(work_dir + '/dataframe_output/wab_comp_sent.csv', encoding='utf-8')
wab_reading = pd.read_csv(work_dir + '/dataframe_output/wab_reading.csv', encoding='utf-8')
wab_repetition = pd.read_csv(work_dir + '/dataframe_output/wab_repetition.csv', encoding='utf-8')

test_list = [bnt30, cowa, csbwpm, nat, pass_, spelling, wab_commands, wab_reading, wab_repetition]
#test_list = [bnt30]



##########################################################################
# Assign Redcap IDs and event names for captured data
print '\n\n\n\n\nrunning ID and event name assignment...'

# Load Redcap Data
redcap_data = pd.read_csv(work_dir + '/redcap_export.csv')

# Filter redcap data by lang headers
#relv_cols = ['subject_id','redcap_event_name','name_first','name_last']
#for test in test_strings:
#    relv_cols = relv_cols + (filter(lambda k: test in k, redcap_data))
#redcap_data = redcap_data[relv_cols]
redcap_data['Subject'] = redcap_data['name_last'] + '_' + redcap_data['name_first']
redcap_data['Subject'] = redcap_data['Subject'].fillna("")

count = 0
relv_cols = []
event_num = 1

#match_test = pd.DataFrame()

for test in test_list:
    match_test = pd.DataFrame()
    if test_strings[count] == 'wab_comp_sent':
        date = 'wab_reading_date'
    else:
        date = test_strings[count]+'_date'
    relv_cols = []
    relv_cols = ['subject_id','redcap_event_name','name_first','name_last',date]
    test_columns = [str(e) for e in test.columns if e not in ('Date')]
    relv_cols = relv_cols + test_columns
    redcap_test_data = redcap_data[relv_cols]
    unique_subjs = test['Subject'].unique()
    
    
    
    for subj in unique_subjs:
        if redcap_test_data[redcap_test_data['Subject'].str.contains(str(subj))]['subject_id'].empty:
            continue
        redcap_id = redcap_test_data[redcap_test_data['Subject'].str.contains(str(subj))]['subject_id'].iloc[0]
        subj_redcap_data = redcap_test_data[redcap_test_data['subject_id'].str.contains(redcap_id)]
        subj_redcap_data = subj_redcap_data.loc[:, ~subj_redcap_data.columns.duplicated()]
        temp_size = np.shape(~subj_redcap_data[date].isnull())
        #if len(temp_size) > 1:
        #    subj_redcap_data = subj_redcap_data[~subj_redcap_data[date].isnull().iloc[:,1]]
        #else:
        #    subj_redcap_data = subj_redcap_data[~subj_redcap_data[date].isnull()]
        subj_redcap_data = subj_redcap_data[~subj_redcap_data[date].isnull()]
        subj_test_data = test[test['Subject'].str.contains(str(subj))]
        #subj_test_data['subject_id'] = subj_test_data['subject_id'].fillna("")
        if not redcap_test_data['subject_id'][redcap_test_data['Subject'] == subj].empty:
            subj_test_data['subject_id'] = redcap_test_data['subject_id'][redcap_test_data['Subject'] == subj].iloc[0]
        else:
            subj_test_data['subject_id'] = subj
        subj_test_data['redcap_event_name'] = ''
        total_num_events = len(subj_redcap_data)
        
        # Sort data by test date
        subj_test_data.sort_values(['Date'], ascending=True)
        
        for i in range(len(subj_test_data)):
            if '-' in str(subj_test_data['Date'].iloc[i])[:4] or '/' in str(subj_test_data['Date'].iloc[i])[:4]:
                test_date_reformat = datetime.strptime(subj_test_data['Date'].iloc[i], '%m/%d/%y').date().strftime('%Y-%m-%d')
            else:
                test_date_reformat = subj_test_data['Date'].iloc[i]
            #print list(subj_redcap_data[date])
            if subj_redcap_data.empty:
                if i == 0:
                    subj_test_data['redcap_event_name'] = 'static_arm_1'
                elif i > 0:
                    total_num_events = total_num_events + 2
                    subj_test_data['redcap_event_name'].iloc[i] = 'visit_'+str(int(total_num_events))+'_arm_1'
            elif str(test_date_reformat) in list(subj_redcap_data[date]):
                index = subj_redcap_data.index[subj_redcap_data[date] == test_date_reformat]
                subj_test_data['redcap_event_name'].iloc[i] = subj_redcap_data.loc[index[0]]['redcap_event_name']
                #total_num_events = total_num_events + 1
            else:
                total_num_events = total_num_events + 1
                subj_test_data['redcap_event_name'].iloc[i] = 'visit_'+str(int(total_num_events))+'_arm_1'
        
        subj_test_data[date] = subj_test_data['Date']
        
        match_test = match_test.append(subj_test_data)
    """
    match_test = pd.merge(master, test, on=['Subject', 'Date'], how='inner')
    
    match_test = match_test.drop_duplicates(['Subject', 'Date'])
    match_test = match_test.sort_index(by=['Subject', 'Date'], ascending=[True, True])
    if test_strings[count]+'_date' in match_test.columns:
        match_test = match_test.drop(test_strings[count]+'_date', 1)
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
    #redcap_df = pd.read_csv(work_dir + '/DickersonMasterEnrol_DATA_2017-12-06_1437.csv')
    
    # Create a column for IDs in Redcap df that match lang spreadsheet IDs (can just be first and last name)
    #redcap_df['Subject'] = redcap_df["name_last"].map(str) + '_' + redcap_df["name_first"]
      
            
    # Pull only subject_id and Subject (to match on). Then add subject_id and data to new df
    redcap_info = redcap_data[['subject_id','Subject']]
    
    
    # Match lang spreadsheets to Redcap
    match_final = pd.merge(redcap_info, match_test, on=['Subject'], how='inner')
    no_match = match_test[~match_test['Subject'].isin(match_final['Subject'])]
    #no_match.to_csv('redcap_format/no_match_'+test_strings[count]+'.csv', encoding='utf8')
    
    
    # Drop unnecessary columns for Redcap
    match_final = match_final.drop(['Event_Number','Subject'], axis=1)
    #keep_cols = [c for c in match_final.columns if c.lower() != 'Unnamed: ']
    match_final = match_final.loc[:, ~match_final.columns.str.contains('Unnamed:')]"""
    
    # Fix up columns
    match_final = match_test.drop(['Date','Subject'], axis=1)
    col_reorder = match_final.columns.tolist()
    col_reorder.remove('subject_id')
    col_reorder.remove('redcap_event_name')
    col_reorder.remove(date)
    col_reorder = ['subject_id','redcap_event_name',date]+[str(x) for x in col_reorder]
    match_final = match_final[col_reorder]
    
    # Weird formatting error, this fixes it, idk why
    match_final['subject_id'] = match_final['subject_id'].str.decode('iso-8859-1').str.encode('utf-8')

    
    match_final.to_csv('redcap_format/'+test_strings[count]+'_redcap.csv', encoding='utf8', index=False)
    count = count + 1
    
    
    ################################################
    # Check if capture data already exists in Redcap
    """all_redcap = pd.read_csv('redcap_export.csv')  # All data from Redcap
    match_test = pd.read_csv('redcap_format/'+test_strings[count]+'_redcap.csv')
    
    rel_cols = [col for col in all_redcap if col.startswith(test_strings[count])]
    rel_cols = ['subject_id','redcap_event_name'] + rel_cols
    rel_redcap = all_redcap[rel_cols]
    
    #if test_strings[count] == 'wab_comp_sent':
    #    match = rel_redcap.merge(match_test,on=['subject_id','redcap_event_name'])
    #    no_match = match_test[(~match_test['subject_id'].isin(match['subject_id']))]
    #else:
        #match = pd.concat([rel_redcap, match_test], axis=0, join='inner')
        #no_match = match_test[~match_test['subject_id'].isin(match['subject_id'])]
    date_col = [col for col in rel_redcap if col.endswith('date')]
    #match = rel_redcap.merge(match_test,on=['subject_id',date_col[-1]])
    match = pd.concat([rel_redcap, match_test], axis=0, join='inner')
    no_match = match_test[(~match_test['subject_id'].isin(match['subject_id']))]
    
    # Output new language data
    if no_match.empty == False:
        no_match.to_csv('redcap_format/new_data/'+test_strings[count]+'_redcap_new.csv', index=False)
    count = count + 1"""

