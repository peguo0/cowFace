# Given 1) a folder that contains a bunch of eid folders, 2) start - end date; 3) output folder path 1 + 2;
# This script split images into 2 folders: if image between start-end date, save to folder 1; else, save to folder 2. 

#!/usr/bin/env python3

import os,sys
libDir=os.path.dirname(os.path.realpath(__file__)) # point to the folder contain this file
sys.path.append(libDir)
import csv
from datetime import datetime, timedelta
from splitColorNBwImages import createSynbolicLink

def getDayList(startDay=-7,endDay=0):
    # Filter day
    if (isinstance(endDay,int)):
        end=datetime.now() + timedelta(days=endDay)
    else:
        end=datetime.strptime(endDay,"%Y%m%d")
    if isinstance(startDay, int):
        start=end + timedelta(days=startDay)
    else:
        start=datetime.strptime(startDay,"%Y%m%d")

    curr=start
    dayList=[]
    while curr < end:
        dayList.append(curr.strftime("%Y%m%d"))
        curr += timedelta(days=1)
    return dayList

def genDataset(dayList,eidFolders,outDir_withinPeriod,outDir_outPeriod):
    with open(eidFolders) as csvfile:
        csvReader = csv.reader(csvfile)
        for row in csvReader:
            eidFolder = row[0]
            eid = os.path.basename(eidFolder)
            path, _, files = next(os.walk(eidFolder))
            for imageFn in files:
                imagePath = os.path.join(path, imageFn)
                imageDate = getImageDate(imageFn)
                if imageDate in dayList:
                    outputFolder = outDir_withinPeriod
                else:
                    outputFolder = outDir_outPeriod
                createSynbolicLink(imagePath, outputFolder, eid)

def getImageDate(imageFn):
    imageDate = imageFn.split('.')[2].split('_')[0]
    return imageDate

def main():
    eidFolders = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowList_1369_color.txt'
    dstart='20200409'
    dend='20200801'
    outDir_withinPeriod='/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_20200409-20200731_pm_color'
    outDir_outPeriod='/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_20200801-20200821_pm_color'

    dayList=getDayList(dstart,dend)
    genDataset(dayList,eidFolders,outDir_withinPeriod,outDir_outPeriod)

if __name__ == '__main__':
    main()