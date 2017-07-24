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
wab_read_comp = pd.read_csv(work_dir + '/wab_read_comp.csv', encoding='utf-8')
# wab_comm = pd.read_csv(work_dir + '/.csv', encoding='utf-8')
cowa = pd.read_csv(work_dir + '/cowa_graph.csv', encoding='utf-8')
writ_sample = pd.read_csv(work_dir + '/writ_sample_graph.csv', encoding='utf-8')
spelling = pd.read_csv(work_dir + '/spelling_graph.csv', encoding='utf-8')

graph = pd.DataFrame()
graph = graph.append(bnt30)
graph = graph.append(lang_transcr)
graph = graph.append(wab_rep)
graph = graph.append(wab_read_comm)
graph = graph.append(wab_read_comp)
# graph = graph.append(wab_comm)
graph = graph.append(cowa)
graph = graph.append(writ_sample)
graph = graph.append(spelling)
graph.to_csv('graph.csv', encoding='utf-8')

graph.plot(kind='bar', stacked=True)
plt.show(graph)
