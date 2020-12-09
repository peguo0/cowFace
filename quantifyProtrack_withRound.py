#/usr/bin/python3
import os, sys
from datetime import datetime
import numpy as np
from numpy import nanmedian, mean, divide
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import copy
from scipy import stats
import pdb 
# my own modules:
from generateSubtitle_withRound import loadTableError, checkPEU, assignRound, getRawData, convertProtrackLogToBailTable
from printStuff import *

TOTALBAILS = 54
BAILSHIFT = 30
PAUSED_THRESHOLD = 12

def quantifyOneProtrackLog(protrackLogFullPaths):                
    bailTable = convertProtrackLogToBailTable(protrackLogFullPaths) 
    bailTable = assignRound(bailTable)    
    bailBeeping = getBailBeeping(bailTable)

    bailDuration = getBailDuration(bailBeeping)  
    bailDuration_removePaused = removePausedBails(bailDuration)        
    bailDurationDiff_round = getBailDurationDiff(bailDuration_removePaused, 1, 0)    
    bailDurationDiff_30 = getBailDurationDiff(bailDuration_removePaused, 0, 30)
    return bailDuration, bailDuration_removePaused, bailDurationDiff_round, bailDurationDiff_30
    
def getBailBeeping(bailTable):
    totalRound = bailTable[-1]['round']
    bailBeeping = initializeEmptyDict(TOTALBAILS, totalRound)
    for eachBail in bailTable:
        currentRound = eachBail['round']
        currentBail = eachBail['bailNumber']
        bailBeeping[currentBail][currentRound-1] = eachBail['datetime']        
    return bailBeeping

# return an empty mmxnn(rowxcolumn) dictionary
def initializeEmptyDict(mm,nn):
    emptyDict = {}
    for row in range(1, mm+1):
        emptyDict[row] = ['NaN' for x in range(1,nn+1)] 
    return emptyDict

# given each bails EID reading time, returns each bails duation (in seconds).
def getBailDuration(bailBeeping):
    bailDuration = copy.deepcopy(bailBeeping)
    totalRound = len(bailBeeping[1])
    for bailNumber in bailBeeping:
        if bailNumber == 1:
            bailDuration[1][0] = 'NaN'
            for round in range(1,totalRound):
                if bailBeeping[1][round] != 'NaN' and bailBeeping[TOTALBAILS][round-1] != 'NaN':
                    bailDuration[1][round] = bailBeeping[1][round] - bailBeeping[TOTALBAILS][round-1]
                else:
                    bailDuration[1][round] = 'NaN'
        if bailNumber != 1:
            for round in range(0,totalRound):
                if bailBeeping[bailNumber][round] != 'NaN' and bailBeeping[bailNumber-1][round] != 'NaN':
                    bailDuration[bailNumber][round] = bailBeeping[bailNumber][round] - bailBeeping[bailNumber-1][round]
                else:
                    bailDuration[bailNumber][round] = 'NaN'                           
    return bailDuration

def removePausedBails(bailDuration):
    bailDuration_removePaused = copy.deepcopy(bailDuration)
    totalRound = len(bailDuration[1])
    for bailNumber in bailDuration:
        for round in range(0, totalRound):
            if bailDuration[bailNumber][round] != 'NaN' and bailDuration[bailNumber][round] > PAUSED_THRESHOLD:
                bailDuration_removePaused[bailNumber][round] = 'NaN'
                bailBefore_round, bailBefore_bailNumber = getComparedBail(round,bailNumber,0,1)
                bailDuration_removePaused[bailBefore_bailNumber][bailBefore_round] = 'NaN'
                bailAfter_round, bailAfter_bailNumber = getComparedBail(round,bailNumber,0,-1)
                bailDuration_removePaused[bailAfter_bailNumber][bailAfter_round] = 'NaN'
    return bailDuration_removePaused

# given each bails duration, target bail's round and bail shift; returns duration difference from the target bail. 
def getBailDurationDiff(bailDuration, roundShift, bailShift):
    assert bailShift < TOTALBAILS, "Please make sure bail shift is less than {}.".format(TOTALBAILS)
    totalRound = len(bailDuration[1])
    assert roundShift < totalRound, "Please make sure round shift is less than {}.".format(totalRound)

    bailDurationDiff = initializeEmptyDict(len(bailDuration),totalRound)

    for bailNumber in bailDuration:
        current_bail = bailNumber
        for round in range(1,totalRound+1):
            current_round = round            
            compared_round, compared_bail = getComparedBail(current_round, current_bail, roundShift, bailShift)
            if compared_round in range(1,totalRound+1) and compared_bail in range(1,TOTALBAILS+1):
                if bailDuration[current_bail][current_round-1] != 'NaN' and bailDuration[compared_bail][compared_round-1] != 'NaN':
                    bailDurationDiff[current_bail][current_round-1] = bailDuration[current_bail][current_round-1] - bailDuration[compared_bail][compared_round-1]  
    return bailDurationDiff

def getComparedBail(current_round, current_bail, roundShift, bailShift):
    assert current_bail > 0 and current_bail <= TOTALBAILS, 'Please make sure current bail is within the range of (0,{})'.format(TOTALBAILS)
    assert abs(bailShift) < TOTALBAILS, 'Please make sure bail shift is lower than total bail: {}.'.format(TOTALBAILS)
    if current_bail > bailShift:
        compared_round = current_round - roundShift
        compared_bail = current_bail - bailShift
        if compared_bail > TOTALBAILS:
            compared_bail = compared_bail-54
            compared_round = compared_round+1
    if current_bail <= bailShift:
        compared_round = current_round - 1 - roundShift
        compared_bail = current_bail + TOTALBAILS - bailShift             
    return compared_round, compared_bail

def getBoxPlot(dictTable):
    dictTable = replaceNAN(dictTable)
    listTable = list(dictTable.values()) # dict to list
    np_table = np.array(listTable)

    mask = ~np.isnan(np_table)
    filtered_data = [d[m] for d, m in zip(np_table, mask)]
    plt.boxplot(filtered_data)
    # plt.ylim(7.5,9.5)
    plt.grid(True)
    plt.show()

def replaceNAN(dictIn):
    for key, value in dictIn.items():
        dictIn[key] = [np.nan if x == 'NaN' else x for x in value]
    return dictIn

def getPValue(table_round, table_30):
    list_round = list(replaceNAN(table_round).values())
    list_30 = list(replaceNAN(table_30).values())
    np_round = np.array(list_round)
    np_30 = np.array(list_30)
    mask_round = ~np.isnan(np_round)
    filtered_round = [d[m] for d, m in zip(np_round, mask_round)]
    mask_30 = ~np.isnan(np_30)
    filtered_30 = [d[m] for d, m in zip(np_30, mask_30)]
    
    p_54 = {}
    for x in range(0,len(filtered_round)):
        _, p2 = stats.ttest_ind(filtered_round[x], filtered_30[x])
        p_54[x + 1] = p2
    print("p = ", p_54)
    return p_54
    
def plotPValue(p_54):
    lists = sorted(p_54.items()) 
    x, y = zip(*lists)
    plt.plot(x, y)
    plt.plot((0,54), (0.05,0.05))
    plt.show()     

def rescaleMilkings(protrackLogFullPaths):
    durationTable_acrossMilking = {}
    for protrackLogFullPath in protrackLogFullPaths:
        _, bailDuration_removePaused, _, _ = quantifyOneProtrackLog(protrackLogFullPath)
        bailDuration_removePaused = replaceNAN(bailDuration_removePaused)
        durationTable_acrossMilking[protrackLogFullPath] = {}
        durationTable_acrossMilking[protrackLogFullPath]['durationTable'] = bailDuration_removePaused
    durationTable_acrossMilking = getMedian(durationTable_acrossMilking)
    durationTable_acrossMilking = getRatio(durationTable_acrossMilking, protrackLogFullPaths)
    durationTable_acrossMilking = getRescaledTable(durationTable_acrossMilking, protrackLogFullPaths)       
    return durationTable_acrossMilking

def getMedian(durationTable_acrossMilking):
    for milking in durationTable_acrossMilking.values():        
        milking['median'] = [nanmedian(x) for x in milking['durationTable'].values()]
    return durationTable_acrossMilking

def getRatio(durationTable_acrossMilking, protrackLogFullPaths):
    for logFile, milking in durationTable_acrossMilking.items():
        if logFile == protrackLogFullPaths[0]:
            milking['ratio']  = 1.0
        else:  
            median_base = durationTable_acrossMilking[protrackLogFullPaths[0]]['median']
            median_current = milking['median']
            milking['ratio'] = mean([x/y for x,y in zip(median_base, median_current)])
    return durationTable_acrossMilking

def getRescaledTable(durationTable_acrossMilking, protrackLogFullPaths):
    for logFile, milking in durationTable_acrossMilking.items():
        milking['durationTable_rescaled'] = copy.deepcopy(milking['durationTable'])
        if logFile == protrackLogFullPaths[0]:
            continue
        else:  
            for round, duration in milking['durationTable_rescaled'].items():
                milking['durationTable_rescaled'][round] = list(np.array(duration) * milking['ratio'])
    return durationTable_acrossMilking

def combineMilking(durationTable_acrossMilking):
    durationTable_rescaled_combined = {}
    for milking in durationTable_acrossMilking.values():
        for round, duration in milking['durationTable_rescaled'].items():
            if round not in durationTable_rescaled_combined:
                durationTable_rescaled_combined[round] = duration
            else:
                durationTable_rescaled_combined[round] = durationTable_rescaled_combined[round] + duration
    return durationTable_rescaled_combined

def getWeight(durationTable_rescaled_combined):
    medianList = []
    for duration in durationTable_rescaled_combined.values():
        medianList.append(nanmedian(duration))
    weight = divide(medianList,medianList[0])
    print('bail weights are: ', weight)

def main_oneProtrackLog(protrackLogFullPaths):             
    bailDuration, bailDuration_removePaused, bailDurationDiff_round, bailDurationDiff_30 = quantifyOneProtrackLog(protrackLogFullPaths)    
    p_54 = getPValue(bailDurationDiff_round, bailDurationDiff_30)

    # Print and plot
    printBailDuration(bailDuration)
    printBailDuration_removedPaused(bailDuration_removePaused)
    printDurationDiff_round(bailDurationDiff_round)
    printDurationDiff_30(bailDurationDiff_30)
    getBoxPlot(bailDuration_removePaused)
    getBoxPlot(bailDurationDiff_round)
    getBoxPlot(bailDurationDiff_30)
    plotPValue(p_54)

def main_rescaledMilking(protrackLogFullPaths):
    durationTable_acrossMilking = rescaleMilkings(protrackLogFullPaths)
    durationTable_rescaled_combined = combineMilking(durationTable_acrossMilking)
    getWeight(durationTable_rescaled_combined)
    durationTable_rescaled_combined_round = getBailDurationDiff(durationTable_rescaled_combined, 1, 0)    
    durationTable_rescaled_combined_30 = getBailDurationDiff(durationTable_rescaled_combined, 0, 30)
    p_54 = getPValue(durationTable_rescaled_combined_round, durationTable_rescaled_combined_30)

    # Print and plot:
    printBailDuration_removedPaused(durationTable_rescaled_combined)
    printDurationDiff_round(durationTable_rescaled_combined_round)
    printDurationDiff_30(durationTable_rescaled_combined_30)
    getBoxPlot(durationTable_rescaled_combined)
    getBoxPlot(durationTable_rescaled_combined_round)
    getBoxPlot(durationTable_rescaled_combined_30) 
    plotPValue(p_54)

def main():           
    protrackLogFullPaths = '/home/peguo0/cowFace/PT.log/202003/20200304/PT-200304-054816.log'
    main_oneProtrackLog(protrackLogFullPaths)

    # ## Do combined duration boxplot
    # protrackLogFullPaths = [
    # '/home/peguo0/cowFace/PT.log/202003/20200304/PT-200304-054816.log',
    # '/home/peguo0/cowFace/PT.log/202002/20200218/PT-200218-030043.log',
    # '/home/peguo0/cowFace/PT.log/202002/20200215/PT-200215-123046.log',
    # '/home/peguo0/cowFace/PT.log/201912/20191211/PT-191211-041517.log',
    # '/home/peguo0/cowFace/PT.log/201912/20191201/PT-191201-041752.log',
    # '/home/peguo0/cowFace/PT.log/202003/20200301/PT-200301-123049.log',
    # '/home/peguo0/cowFace/PT.log/202001/20200122/PT-200122-041347.log',
    # '/home/peguo0/cowFace/PT.log/202001/20200128/PT-200128-123033.log',
    # '/home/peguo0/cowFace/PT.log/202004/20200410/PT-200410-045100.log',
    # '/home/peguo0/cowFace/PT.log/202004/20200414/PT-200414-123040.log',
    # ] 
    # main_rescaledMilking(protrackLogFullPaths)
 
if __name__ == '__main__':
    main()
