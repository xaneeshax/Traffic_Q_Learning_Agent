#!/usr/bin/env python
# coding: utf-8

# In[10]:


import pandas as pd
from PyPDF2 import PdfReader


# In[9]:


route_file = pd.read_xml('7a.rou.xml')
route_file


# In[60]:


reader = PdfReader("Parker, Forsyth, Huntington.pdf")
demand = reader.pages[0]
demand_text = demand.extract_text()
demand_text = demand_text.replace('U ‐Turn', 'U-Turn')
demand_text = demand_text.replace('\n', ' ')
demand_text


# In[61]:


ind_2048 = demand_text.index('2048')
demand_text = demand_text[:ind_2048 + 4]
demand_text


# In[64]:


lines = demand_text.split()#[20:]
lines_int = []
issue = 0
for line in lines:
    try:
        line = int(line)
        if (line > 2164):
            line_0 = int(line / 100)
            line_1 = line % 100
            lines_int.append(line_0)
            lines_int.append(line_1)
        else:
            lines_int.append(line)
    except:
        continue
lines_int


# In[65]:


len(lines_int)


# In[76]:


line_len = 21
line_index = 0
lines_clean = []
cur_line = []
for line in lines_int:
    if (line_index % line_len == 0 and len(cur_line) > 0):
        lines_clean.append(cur_line)
        cur_line = []
    cur_line.append(line)
    line_index += 1
lines_clean.append(cur_line)
lines_clean


# In[79]:


dict_data = {'Forsyth Right': [], 'Forsyth Thru': [], 'Forsyth Left': [], 'Forsyth UTurn': [], 'Forsyth Total': [],
       'Huntington from E Right': [], 'Huntington from E Thru': [], 'Huntington from E Left': [],
        'Huntington from E UTurn': [], 'Huntington from E Total': [],
        'Parker Right': [], 'Parker Thru': [], 'Parker Left': [], 'Parker UTurn': [], 'Parker Total': [],
        'Huntington from W Right': [], 'Huntington from W Thru': [], 'Huntington from W Left': [],
        'Huntington from W UTurn': [], 'Huntington from W Total': [], 'Total': []}
dict_data


# In[107]:


for row in lines_clean:
    dict_data['Forsyth Right'].append(row[0])
    dict_data['Forsyth Thru'].append(row[1])
    dict_data['Forsyth Left'].append(row[2])
    dict_data['Forsyth UTurn'].append(row[3])
    dict_data['Forsyth Total'].append(row[4])
    dict_data['Huntington from E Right'].append(row[5])
    dict_data['Huntington from E Thru'].append(row[6])
    dict_data['Huntington from E Left'].append(row[7])
    dict_data['Huntington from E UTurn'].append(row[8])
    dict_data['Huntington from E Total'].append(row[9])
    dict_data['Parker Right'].append(row[10])
    dict_data['Parker Thru'].append(row[11])
    dict_data['Parker Left'].append(row[12])
    dict_data['Parker UTurn'].append(row[13])
    dict_data['Parker Total'].append(row[14])
    dict_data['Huntington from W Right'].append(row[15])
    dict_data['Huntington from W Thru'].append(row[16])
    dict_data['Huntington from W Left'].append(row[17])
    dict_data['Huntington from W UTurn'].append(row[18])
    dict_data['Huntington from W Total'].append(row[19])
    dict_data['Total'].append(row[20])
df_data = pd.DataFrame(dict_data, columns = dict_data.keys())
df_data


# In[108]:


hr = 7
mins = 0
am = 'am'
secs = 0
total = False
for row in range(len(df_data)):
    if (total):
        df_data.at[row, 'Time'] = str(hr-1) + str(am) + ' total'
        df_data.at[row, 'TimePoint (s from sim start)'] = None
        total = False
    else:
        df_data.at[row, 'Time'] = str(hr) + ':' + str(mins) + str(am)
        df_data.at[row, 'TimePoint (s from sim start)'] = secs
        secs += 900
        mins += 15
        if (mins == 60):
            total = True
            hr += 1
            mins = 0
        if (hr == 13):
            hr = 1
            am = 'pm'
df_data


# In[110]:


df_filtered = df_data[~df_data['Time'].map(lambda x: 'total' in x)]
df_filtered


# In[111]:


df_final = df_filtered.set_index(['Time', 'TimePoint (s from sim start)'])
df_final


# In[112]:


df_final.head(15)


# In[113]:


df_final.to_csv('Intersection Data to Table.csv')


# In[ ]:




