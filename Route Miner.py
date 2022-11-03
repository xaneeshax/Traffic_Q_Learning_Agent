#!/usr/bin/env python
# coding: utf-8

# In[5]:


import pandas as pd
from PyPDF2 import PdfReader


# In[16]:


route_file = pd.read_xml('7a.rou.xml')
route_file


# In[17]:


reader = PdfReader("Parker, Forsyth, Huntington.pdf")
demand = reader.pages[0]
demand_text = demand.extract_text()
demand_text = demand_text.replace('U ‐Turn', 'U-Turn')
demand_text = demand_text.replace('\n', ' ')
demand_text


# In[18]:


ind_2048 = demand_text.index('2048')
demand_text = demand_text[:ind_2048 + 4]
demand_text


# In[19]:


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


# In[20]:


len(lines_int)


# In[21]:


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


# In[50]:


dict_data = {'Forsyth Right': [], 'Forsyth Thru': [], 'Forsyth Left': [], 'Forsyth UTurn': [], 'Forsyth Total': [],
       'Huntington from E Right': [], 'Huntington from E Thru': [], 'Huntington from E Left': [],
        'Huntington from E UTurn': [], 'Huntington from E Total': [],
        'Parker Right': [], 'Parker Thru': [], 'Parker Left': [], 'Parker UTurn': [], 'Parker Total': [],
        'Huntington from W Right': [], 'Huntington from W Thru': [], 'Huntington from W Left': [],
        'Huntington from W UTurn': [], 'Huntington from W Total': [], 'Total': []}
dict_data


# In[51]:


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


# In[52]:


hr = 7
mins = 0
am = 'am'
secs = 0
total = False
for row in range(len(df_data)):
    if (total):
        df_data.at[row, 'Time'] = str(hr-1) + str(am) + ' total'
        df_data.at[row, 'TimePoint (s from sim start)'] = None
        df_data.at[row, 'StrName'] = str(hr-1) + str(am) + 'Total'
        total = False
    elif mins == 0:
        df_data.at[row, 'Time'] = str(hr) + str(am)
        df_data.at[row, 'TimePoint (s from sim start)'] = secs
        df_data.at[row, 'StrName'] = str(hr) + str(am)
        secs += 900
        mins += 15
        if (mins == 60):
            total = True
            hr += 1
            mins = 0
        if (hr == 13):
            hr = 1
            am = 'pm'
    else:
        df_data.at[row, 'Time'] = str(hr) + ':' + str(mins) + str(am)
        df_data.at[row, 'TimePoint (s from sim start)'] = secs
        df_data.at[row, 'StrName'] = str(hr) + str(mins) + str(am)
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


# In[53]:


df_filtered = df_data[~df_data['Time'].map(lambda x: 'total' in x)]
df_filtered


# In[54]:


df_final = df_filtered.set_index(['Time', 'TimePoint (s from sim start)', 'StrName'])
df_final


# In[55]:


df_final.head(15)


# In[56]:


df_final.to_csv('Intersection Data to Table.csv')


# In[59]:


final_dict = df_final.reset_index().to_dict(orient = 'index')
final_dict


# In[71]:


def print_row(row_num):
    data = final_dict[row_num]
    # ForsythRight
    string = '<flow id="ForsythRight'
    string += str(data['StrName'])
    string += '" begin="'
    string += str(data['TimePoint (s from sim start)'])
    string += '" departLane="random" departSpeed="avg" arrivalLane="current" from="426843745#0" to="798289594#3" end="'
    string += str(data['TimePoint (s from sim start)'] + 900)
    string += '" number="'
    string += str(data['Forsyth Right'])
    string += '"/>\n'
    # ForsythThru
    string += '<flow id="ForsythThru'
    string += str(data['StrName'])
    string += '" begin="'
    string += str(data['TimePoint (s from sim start)'])
    string += '" departLane="random" departSpeed="avg" arrivalLane="current" from="426843745#0" to="-8644213#9" end="'
    string += str(data['TimePoint (s from sim start)'] + 900)
    string += '" number="'
    string += str(data['Forsyth Thru'])
    string += '"/>\n'
    # ForsythLeft
    string += '<flow id="ForsythLeft'
    string += str(data['StrName'])
    string += '" begin="'
    string += str(data['TimePoint (s from sim start)'])
    string += '" departLane="random" departSpeed="avg" arrivalLane="current" from="426843745#0" to="102519704#0" end="'
    string += str(data['TimePoint (s from sim start)'] + 900)
    string += '" number="'
    string += str(data['Forsyth Left'])
    string += '"/>\n'
    # ForsythUTurn
    string += '<flow id="ForsythUTurn'
    string += str(data['StrName'])
    string += '" begin="'
    string += str(data['TimePoint (s from sim start)'])
    string += '" departLane="random" departSpeed="avg" arrivalLane="current" from="426843745#0" to="426843743" end="'
    string += str(data['TimePoint (s from sim start)'] + 900)
    string += '" number="'
    string += str(data['Forsyth UTurn'])
    string += '"/>\n'
    # HuntFromERight
    string += '<flow id="HuntFromERight'
    string += str(data['StrName'])
    string += '" begin="'
    string += str(data['TimePoint (s from sim start)'])
    string += '" departLane="random" departSpeed="avg" arrivalLane="current" from="798289594#0" to="426843743" end="'
    string += str(data['TimePoint (s from sim start)'] + 900)
    string += '" number="'
    string += str(data['Huntington from E Right'])
    string += '"/>\n'
    # HuntFromEThru
    string += '<flow id="HuntFromEThru'
    string += str(data['StrName'])
    string += '" begin="'
    string += str(data['TimePoint (s from sim start)'])
    string += '" departLane="random" departSpeed="avg" arrivalLane="current" from="798289594#0" to="798289594#3" end="'
    string += str(data['TimePoint (s from sim start)'] + 900)
    string += '" number="'
    string += str(data['Huntington from E Thru'])
    string += '"/>\n'
    # HuntFromELeft
    string += '<flow id="HuntFromELeft'
    string += str(data['StrName'])
    string += '" begin="'
    string += str(data['TimePoint (s from sim start)'])
    string += '" departLane="random" departSpeed="avg" arrivalLane="current" from="798289594#0" to="-8644213#9" end="'
    string += str(data['TimePoint (s from sim start)'] + 900)
    string += '" number="'
    string += str(data['Huntington from E Left'])
    string += '"/>\n'
    # HuntFromEUTurn
    string += '<flow id="HuntFromEUTurn'
    string += str(data['StrName'])
    string += '" begin="'
    string += str(data['TimePoint (s from sim start)'])
    string += '" departLane="random" departSpeed="avg" arrivalLane="current" from="798289594#0" to="102519704#0" end="'
    string += str(data['TimePoint (s from sim start)'] + 900)
    string += '" number="'
    string += str(data['Huntington from E UTurn'])
    string += '"/>\n'
    # ParkerRight
    string += '<flow id="ParkerRight'
    string += str(data['StrName'])
    string += '" begin="'
    string += str(data['TimePoint (s from sim start)'])
    string += '" departLane="random" departSpeed="avg" arrivalLane="current" from="8644213#8" to="102519704#0" end="'
    string += str(data['TimePoint (s from sim start)'] + 900)
    string += '" number="'
    string += str(data['Parker Right'])
    string += '"/>\n'
    # ParkerThru
    string += '<flow id="ParkerThru'
    string += str(data['StrName'])
    string += '" begin="'
    string += str(data['TimePoint (s from sim start)'])
    string += '" departLane="random" departSpeed="avg" arrivalLane="current" from="8644213#8" to="426843743" end="'
    string += str(data['TimePoint (s from sim start)'] + 900)
    string += '" number="'
    string += str(data['Parker Thru'])
    string += '"/>\n'
    # ParkerLeft
    string += '<flow id="ParkerLeft'
    string += str(data['StrName'])
    string += '" begin="'
    string += str(data['TimePoint (s from sim start)'])
    string += '" departLane="random" departSpeed="avg" arrivalLane="current" from="8644213#8" to="798289594#3" end="'
    string += str(data['TimePoint (s from sim start)'] + 900)
    string += '" number="'
    string += str(data['Parker Left'])
    string += '"/>\n'
    # ParkerUTurn
    string += '<flow id="ParkerUTurn'
    string += str(data['StrName'])
    string += '" begin="'
    string += str(data['TimePoint (s from sim start)'])
    string += '" departLane="random" departSpeed="avg" arrivalLane="current" from="8644213#8" to="-8644213#9" end="'
    string += str(data['TimePoint (s from sim start)'] + 900)
    string += '" number="'
    string += str(data['Parker UTurn'])
    string += '"/>\n'
    # HuntFromWRight
    string += '<flow id="HuntFromWRight'
    string += str(data['StrName'])
    string += '" begin="'
    string += str(data['TimePoint (s from sim start)'])
    string += '" departLane="random" departSpeed="avg" arrivalLane="current" from="426493699#0" to="-8644213#9" end="'
    string += str(data['TimePoint (s from sim start)'] + 900)
    string += '" number="'
    string += str(data['Huntington from W Right'])
    string += '"/>\n'
    # HuntFromWThru
    string += '<flow id="HuntFromWThru'
    string += str(data['StrName'])
    string += '" begin="'
    string += str(data['TimePoint (s from sim start)'])
    string += '" departLane="random" departSpeed="avg" arrivalLane="current" from="426493699#0" to="102519704#0" end="'
    string += str(data['TimePoint (s from sim start)'] + 900)
    string += '" number="'
    string += str(data['Huntington from W Thru'])
    string += '"/>\n'
    # HuntFromWLeft
    string += '<flow id="HuntFromWLeft'
    string += str(data['StrName'])
    string += '" begin="'
    string += str(data['TimePoint (s from sim start)'])
    string += '" departLane="random" departSpeed="avg" arrivalLane="current" from="426493699#0" to="426843743" end="'
    string += str(data['TimePoint (s from sim start)'] + 900)
    string += '" number="'
    string += str(data['Huntington from W Left'])
    string += '"/>\n'
    # HuntFromWUTurn
    string += '<flow id="HuntFromWUTurn'
    string += str(data['StrName'])
    string += '" begin="'
    string += str(data['TimePoint (s from sim start)'])
    string += '" departLane="random" departSpeed="avg" arrivalLane="current" from="426493699#0" to="798289594#3" end="'
    string += str(data['TimePoint (s from sim start)'] + 900)
    string += '" number="'
    string += str(data['Huntington from W UTurn'])
    string += '"/>'
    print(string)


# In[74]:


# Copy and paste output into xml file
for row in range(len(final_dict)):
    print_row(row)


# In[ ]:




