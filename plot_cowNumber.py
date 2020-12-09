import os
import csv
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import statistics 

eidPath = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_20200409-20200821_pm_116993'

def plot_histogram(listToPlot):               
    bins = range(0,200,10)
    plt.figure(1)
    plt.hist(listToPlot, bins = bins, facecolor='blue')
    plt.xlabel('Number of Frames')
    plt.ylabel('Number of Cows')
    # plt.show()
    plt.savefig('histogram_frameNumber_1369cow.png')

def printStat(aList):
    median = statistics.median(aList) 
    print('median = ', median)
    percentile_5 = np.percentile(aList, 5)
    percentile_95 = np.percentile(aList, 95)
    print('5-95 percentile = [', percentile_5, ', ', percentile_95, ']')

def getEidDict(eidListFile):
    eidDict = {}
    with open(eidListFile) as csvfile:
        csvReader = csv.reader(csvfile)
        for row in csvReader:
            eidFolderPath = row[0]  
            eid = os.path.basename(eidFolderPath)
            file_count = countFiles(eidFolderPath)
            eidDict[eid] = file_count
    return eidDict

def countFiles(folderPath):
    _, _, files = next(os.walk(folderPath))
    file_count = len(files)
    return file_count

def main():
    eidListFile = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowList_1369.txt'    
    eidDict = getEidDict(eidListFile)
    eidList = list(eidDict.values())    
    plot_histogram(eidList)
    printStat(eidList)

if __name__ == '__main__':
    main()