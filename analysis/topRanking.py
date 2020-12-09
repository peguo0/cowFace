#!/usr/bin/env python3 

from tqdm import tqdm
from matplotlib import pyplot as plt
import pandas as pd
import cv2
import math
import pickle
import analysis 
import multiprocessing
import time
import os,sys


def plotSomeError(errorTop,num,df,numTop, excludeList=[],cropx0y0x1y1=analysis.cropCoords):
    top=list(errorTop[:num]['imgPath'])
    final=None
    for img in top:
        others=list(df[img]['imgPath'])
        count=0
        resImg=None
        for cowPath in others:
            if cowPath in excludeList:
                continue            
            cowImg=analysis.cropCenter(cowPath,cropx0y0x1y1=cropx0y0x1y1)
            resImg=analysis.stitch(resImg,cowImg,False)
            count +=1
            if count >= numTop:
                break

        thisImg=analysis.cropCenter(img,cropx0y0x1y1=cropx0y0x1y1)
        resImg=analysis.stitch(thisImg,resImg,False,5,(255,255,255))

        final=analysis.stitch(final,resImg,True,5,(255,255,255))
    return final

def errorTopN(df,numTop,excludeList=[]):

    # We will remove case where cow have less than 5 images.
    eidCount=dict()
    for img in df:     
        if img in excludeList:
            continue   
        thisEid=analysis.getEid(img)
        if thisEid in eidCount:
            eidCount[thisEid] += 1
        else:
            eidCount[thisEid] = 0
    
    # Exclude cow
    excludeCow=[]
    for cow in eidCount:
        if eidCount[cow] < numTop:
            excludeCow.append(cow)
    
    print("{} cows have less than {} images. They are excluded.".format(len(excludeCow),numTop))

    res={'imgPath':[],'errorCount':[], 'numWrongCow':[],'maxOccurence':[]}
    for img in df:
        if img in excludeList:
            continue
        thisEid=analysis.getEid(img)

        if thisEid in excludeCow:
            continue
        
        w=df[img]
        #top=w[:numTop]
        #paths=top['imgPath']
        paths=w['imgPath']
        topEids=[]
        count=0
        for path in paths:
            if (path in excludeList):
                continue
            count += 1
            topEids.append(analysis.getEid(path))

            if count >= numTop:
                break
        
        wrongEids=dict()
        count=0
        for eid in topEids:
            if eid != thisEid:
                if eid not in wrongEids:
                    wrongEids[eid] = 1
                else:
                    wrongEids[eid] += 1                    
                count+=1
        res['imgPath'].append(img)
        res['errorCount'].append(count)
        res['numWrongCow'].append(len(wrongEids))
        if (len(wrongEids.values()) > 0):
            res['maxOccurence'].append(max(wrongEids.values()))
        else:
            res['maxOccurence'].append(0)
    
    df=pd.DataFrame(res)
    df=df.sort_values(by=['errorCount'],ascending=False).reset_index(drop=True)
    return excludeCow,df

class Container(object):
    pass

parallelParam=Container()

def rankOneImage(i):
    # unpacking parameters
    global parallelParam
    eidDict=parallelParam.eidDict
    eids=parallelParam.eids
    fvs=parallelParam.fvs 
    paths=parallelParam.paths

    eid=eids[i]
    fv=fvs[i]
    dfDict={'d2':[],'eid':[]}
    for cow in eidDict:
        target=eidDict[cow]['centroid']
        dfDict['d2'].append(analysis.distance2(fv,target))
        dfDict['eid'].append(cow)
    df=pd.DataFrame(dfDict)
    df=df.sort_values(by=['d2'],ascending=True).reset_index(drop=True)
    mismatch=[]
    for index, row in df.iterrows():
        if (row['eid'] == eid):
            return (paths[i],[index,mismatch])
        else:
            mismatch.append(row['eid'])


def ranking(eidDict,dfDict,numCPU=7):
    eidDict=analysis.computeClusterCentroid(eidDict)
    #res=dict()
    
    global parallelParam
    parallelParam.eidDict=eidDict
    parallelParam.eids = dfDict['eids']
    parallelParam.fvs=dfDict['fvs']
    parallelParam.paths=dfDict['paths']

    #pbar=tqdm(total=tot)
        
    numImg=len(parallelParam.eids)
    #numImg=20
    if numCPU > 0:
        pool = multiprocessing.Pool(numCPU)
    else:
        pool = multiprocessing.Pool()
    res = list(tqdm(pool.imap(rankOneImage, range(numImg)), total=numImg))

    mismatchDict=dict()
    final={'path':[],'rank':[]}
    for t in res :
        path=t[0]
        data=t[1]
        rank=data[0]
        mismatch=data[1]
        mismatchDict[path] = mismatch
        final['path'].append(path)
        final['rank'].append(rank)
    df=pd.DataFrame(final)
    return mismatchDict,df


def computeRanking(datasetFn,numCPU=0):
    eidDict,dfDict=analysis.loadFv(datasetFn) 
    mismatchDict,dfRanking=ranking(eidDict,dfDict,numCPU)
    #fn='ranking.pkl'
    fn="{}.ranking.pkl".format(datasetFn)
    analysis.savePkl(dfRanking,fn)
    #print("{} saved".format(fn))
    
    fn="{}.mismatch.pkl".format(datasetFn)
    analysis.savePkl(mismatchDict,fn)
    #print("{} saved".format(fn))


def main():
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(" Usage: {} <featurevector.fv>".format(sys.argv[0]))
        sys.exit(1)
    
    computeRanking(sys.argv[1])
