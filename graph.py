import pandas as pd
import csv
import numpy as np
import re
from datetime import datetime
import matplotlib.pyplot as plt

import os
import fnmatch

# Capture all subject lang files
# Skip spreadsheets that have errors for missing tabs, or ill formatted headers
# Create a seperate list for each error with failed subjects/files

work_dir = '/Users/axs97/Desktop/lang_eval_to_redcap-alexs'

os.chdir(work_dir)

bnt30 = pd.read_csv(work_dir + '/bnt30_graph.csv', encoding='utf-8')
lang_transcr = pd.read_csv(work_dir + '/lang_trans_graph.csv', encoding='utf-8')
wab_rep = pd.read_csv(work_dir + '/wab_rep_graph.csv', encoding='utf-8')
wab_read_comm = pd.read_csv(work_dir + '/wab_read_comm_graph.csv', encoding='utf-8')
wab_read_comp = pd.read_csv(work_dir + '/wab_read_comp_graph.csv', encoding='utf-8')
# wab_comm = pd.read_csv(work_dir + '/.csv', encoding='utf-8')
cowa = pd.read_csv(work_dir + '/cowa_graph.csv', encoding='utf-8')
writ_sample = pd.read_csv(work_dir + '/writ_sample_graph.csv', encoding='utf-8')
spelling = pd.read_csv(work_dir + '/spelling_graph.csv', encoding='utf-8')

bnt30_total = pd.read_csv(work_dir + '/total_bnt30_graph.csv', encoding='utf-8')
lang_total = pd.read_csv(work_dir + '/total_trans_graph.csv', encoding='utf-8')
wab_rep_total = pd.read_csv(work_dir + '/total_wab_rep_graph.csv', encoding='utf-8')
read_comm_total = pd.read_csv(work_dir + '/total_read_comm_graph.csv', encoding='utf-8')
read_comp_total = pd.read_csv(work_dir + '/total_read_comp_graph.csv', encoding='utf-8')
# wab_comm_total = pd.read_csv(work_dir + '/bnt30_graph.csv', encoding='utf-8')
cowa_total = pd.read_csv(work_dir + '/total_cowa_graph.csv', encoding='utf-8')
writ_total = pd.read_csv(work_dir + '/total_writ_sample_graph.csv', encoding='utf-8')
spelling_total = pd.read_csv(work_dir + '/total_spelling_graph.csv', encoding='utf-8')

total_graph = pd.DataFrame()
total_graph = total_graph.append(bnt30_total)
total_graph = total_graph.append(lang_total)
total_graph = total_graph.append(wab_rep_total)
total_graph = total_graph.append(read_comm_total)
total_graph = total_graph.append(read_comp_total)
# total_graph = total_graph.append(wab_comm_total)
total_graph = total_graph.append(cowa_total)
total_graph = total_graph.append(writ_total)
total_graph = total_graph.append(spelling_total)

total_graph = total_graph.set_index(['Test'])
total_graph.to_csv('total_graph.csv', encoding='utf-8')
ay = total_graph.plot(kind='bar', title='Total File Summary', rot=40, colors=['lightgreen', 'grey'], stacked=True)
plt.legend(loc='left', bbox_to_anchor=(1.0, 0.5))
ay.set_ylabel('Number of Files')
plt.show(total_graph)

full_graph = pd.DataFrame()
full_graph = full_graph.append(bnt30)
full_graph = full_graph.append(lang_transcr)
full_graph = full_graph.append(wab_rep)
full_graph = full_graph.append(wab_read_comm)
full_graph = full_graph.append(wab_read_comp)
# full_graph = full_graph.append(wab_comm)
full_graph = full_graph.append(cowa)
full_graph = full_graph.append(writ_sample)
full_graph = full_graph.append(spelling)

full_graph = full_graph.set_index(['Test'])
full_graph.to_csv('graph.csv', encoding='utf-8')
ax = full_graph.plot(kind='bar', title='Summary of Collected Data', rot=40, colors=['g','r','purple','y','orange','black'], stacked=True)
plt.legend(loc='left', bbox_to_anchor=(1.0, 0.5))
ax.set_ylabel('Percent')
ax.set_ylim((0, 105))
plt.show(full_graph)
