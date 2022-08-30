# -*- coding: utf-8 -*-
"""

Script to compute the ADV threshold from a Verasonics acquisition

Last revision : 2022.04.05

@author: Alexis.Vivien
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter
from tkinter import filedialog
import os
from os import listdir
from os.path import isfile, join

root = tkinter.Tk()
root.lift()
root.withdraw() #use to hide tkinter window

def search_for_file_path ():
    currdir = os.getcwd()
    tempdir = filedialog.askdirectory(parent=root, initialdir=currdir, title='Please select a directory')
    if len(tempdir) > 0:
        print ("You chose: %s" % tempdir)
    return tempdir



### LIST THE EXCEL FILES ###
file_path_variable = search_for_file_path()
sheet_name = 'Sheet 1'
files = [f for f in listdir(file_path_variable) if isfile(join(file_path_variable, f)) and f.endswith('.xls')]

### READ THE EXCEL FILES
for f in files:
    temp = pd.read_excel(file_path_variable + '/' + f)
    
### KEEPS ONLY THE TIME AND ECHO VALUES
col = temp.columns
temp = temp.drop(col[3:],axis = 1)
temp = temp.drop(range(19))
temp = temp.rename(columns={col[0]:'Time [s]', col[1]:'Echo (lin)', col[2]:'Blank'})
MM = temp.join(temp,rsuffix='_orig'); MM = MM.rename(columns={'Time [s]':'Time [s]', 'Echo (lin)':'Echo (lin)', 'Time [s]_orig':'MM50','Echo (lin)_orig':'MM100'})

### MOYENNES MOBILES
start = MM.index[0]
# MM['Echo (lin)'] = MM['Echo (lin)'] - MM['Blank']
MM['MM50'] = MM['Echo (lin)'].rolling(10,min_periods=1).mean()
MM['BKG'] = MM['Blank'].rolling(10,min_periods=1).mean()
MM['MM150'] = MM['Echo (lin)'].rolling(150).mean()
MM['MM200'] = MM['Echo (lin)'].rolling(200).mean()
MM = MM.fillna(0)

# ind1 = np.where(MM['MM50']>0)[0][0]
# # ind2 = np.argmin(MM['MM50'][ind1:])
# MM['MM50'][0:ind1] = MM['MM50'][0:ind1] + MM['MM50'][ind1+MM.index[0]]
 
### PLOTS

data = np.array(MM[['Time [s]','MM50']].dropna())
# data = 10*np.log10(data)
fig2, ax2 = plt.subplots()
ax2.plot(MM['Time [s]'], MM['Echo (lin)'],label='Standard Echo')
# ax2.plot(MM['Time [s]'], MM['MM50'],label='Echo mean 50')
# ax2.plot(MM['Time [s]'], data[:,1],label='5s rolling mean')
ax2.plot(MM['Time [s]'],MM['BKG'],label='Background mean')
ax2.set_yscale('log')
ax2.set_ylabel('Echo Power [au]')
ax2.set_xlabel('Time [s]')
ax2.legend(loc=0)

x,y = MM['Time [s]'], data[:,1]
# y = np.sort(y)
fig, ax3 = plt.subplots()
ax3.plot(x,np.gradient(y),label='5s rolling mean gradient')
ax3.set_yscale('linear')
ax2.set_ylabel('Echo Power gradient [au]')
ax3.set_xlabel('Time [s]')
ax3.legend(loc=0)

index_adv = np.where(MM['MM50']>2*MM['BKG'])[0][0:]
index_adv2 = np.where(np.gradient(y)>50000)[0][0:]

intersect = np.intersect1d(index_adv,index_adv2)
print(x[index_adv+MM.index[0]],x[intersect+MM.index[0]])





