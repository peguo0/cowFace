import os
import sys
sys.path.append('/data/gpueval/imageProcessing/peguo0/cowFace/')
from plot_cowNumber import getEidDict, eidPath

def getEidRange(eidDict, range_low, range_high):
    for eid, cowNumber in eidDict.items():
        if cowNumber >= range_low and cowNumber < range_high:
            print(os.path.join(eidPath, eid))

def main():
    eidListFile = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowList_1369.txt'    
    eidDict = getEidDict(eidListFile)
    getEidRange(eidDict, 80, 110)

if __name__ == '__main__':
    main()