import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import random
from matplotlib.colors import ListedColormap
from plot_cowNumber import getEidDict
import csv
from videoLibs import decomposeFrameNamePts

startDate = datetime(2020,4,9)
endDate = datetime(2020,8,21)

black='#000000'
green='#6acc64'
red='#e74c3c'

mycolors=[black    # NO_FRAMR=0
          ,green   # NUMBER_OF_FRAMES=1
          ,red     # NUMBER_OF_FRAMES>1
         ]

def dateRange(date1, date2):
    dateList = []
    for n in range(int ((date2 - date1).days)+1):
        dateList.append(date1 + timedelta(n))
    # aaa = [datetime.strptime(day) for day in dateList]
    return dateList 

def getEidAppearedDays(eidListFile):
    eidDict = {}
    with open(eidListFile) as csvfile:
        csvReader = csv.reader(csvfile)
        for row in csvReader:
            eidFolderPath = row[0]  
            eid = os.path.basename(eidFolderPath)
            _,_,files = next(os.walk(eidFolderPath))
            days = [decomposeFrameNamePts(frame)['day'] for frame in files]
            eidDict[eid] = days
    return eidDict

def covertToSameLength(dictIn, dates):
    numOfDays = len(dates)
    dictOut = {}
    for eid, appearedDays in dictIn.items():
        dictOut[eid] = zerolistmaker(numOfDays)
        for day in appearedDays:
            index = dates.index(day)
            dictOut[eid][index] = dictOut[eid][index] + 1
    return dictOut

def zerolistmaker(n):
    listofzeros = [0] * n
    return listofzeros

def plot_heatmap(df, eidListFile):
    figHeight = len(df)*0.3
    cmap = ListedColormap(mycolors)
    sns.set(rc={'figure.figsize':(20,figHeight)})
    ax = sns.heatmap(df,cmap=cmap, linewidths=0.01, linecolor='#5d5d5d',cbar=False)
    title = os.path.basename(eidListFile).split('.')[0]
    ax.set(title = title)
    plt.savefig('heatmap_1369_'+ title.split('_')[-1] + '.png')

def eidListToDf(eidListFile):
    dates = [day.strftime("%Y%m%d") for day in dateRange(startDate,endDate)]
    eidAppearedDays = getEidAppearedDays(eidListFile)
    eidAppearedDays_sameLength = covertToSameLength(eidAppearedDays, dates)          
    df = pd.DataFrame(eidAppearedDays_sameLength,index = dates).transpose()
    df[df>2] = 2
    return df

def getFileList(filePath):
    aList = []
    with open(filePath) as csvFile:
        csvReader = csv.reader(csvFile)
        for row in csvReader:
            aList.append(row[0])
    return aList

def main():
    # For a single file:
    eidListFile = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowList_1369_sorted.txt'
    df = eidListToDf(eidListFile)
    plot_heatmap(df, eidListFile)

    # # For a batch:
    # eidFilesPath = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowList_files.txt'
    # eidFiles = getFileList(eidFilesPath)
    # for eidListFile in eidFiles:         
    #     df = eidListToDf(eidListFile)
    #     plot_heatmap(df, eidListFile)
    
    


if __name__ == '__main__':
    main()

