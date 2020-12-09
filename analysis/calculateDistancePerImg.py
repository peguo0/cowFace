#!/usr/bin/env python3 

import glob
import os,sys
import pandas as pd

from tqdm import tqdm

import analysis
import multiprocessing

imgPaths=[]
fvs=[]
indexMap=dict()
totImg=0
eids=[]

def calOneImg(index):
    res={'d2':[],'imgPath':[]}
    for i in range(totImg):
        if (i == index):
            continue
        res['d2'].append(analysis.distance2(fvs[index],fvs[i]))
        res['imgPath'].append(imgPaths[i])
    df=pd.DataFrame(res)
    df=df.sort_values(by=['d2']).reset_index(drop=True)
    df['index'] = df.index
    return df[:100]



# def save(obt,fn):
#     print('Saving to {} ...'.format(fn))
#     with open(fn, 'wb') as f:
#         pickle.dump(obt, f, pickle.HIGHEST_PROTOCOL)

# def load(fn):
#     with open(fn, 'rb') as f:
#         return pickle.load(f)

def loadData(fvFile):
    global imgPaths
    global fvs  
    global eids 
    global totImg
    
    eids=[]  
    imgPaths=[]
    fvs=[]   

    eidDict,dfDict=analysis.loadFv(fvFile)

    for eid in eidDict:
        eids.extend([eid]* len(eidDict[eid]['imgPath']))
        fvs.extend(eidDict[eid]['fvs'])
        imgPaths.extend(eidDict[eid]['imgPath'])

    totImg=len(eids)


def main(fvFile):
    global totImg

    print("Loading feature vectors data ...")
    loadData(fvFile)
    
    numImg=totImg
    pool = multiprocessing.Pool()
    dfs = list(tqdm(pool.imap(calOneImg, range(numImg)), total=numImg))

    res=dict()
    for i in range(numImg):
        res[imgPaths[i]] = dfs[i]        
    
    outfn="{}.best100DistancePerImg.pkl".format(fvFile)
    analysis.savePkl(res,outfn)

if __name__ == '__main__':
    #global imgPaths
    #global fvs
    #global indexMap
    if len(sys.argv) < 2:
        print(" Usage: {} <featurevector.fv>".format(sys.argv[0]))
        sys.exit(1)
    
    main(sys.argv[1])
    

    # loadData()

    # numCow=totImg
    # pool = multiprocessing.Pool(40)
    # dfs = list(tqdm(pool.imap(calOneImg, range(numCow)), total=numCow))

    # res=dict()
    # for i in range(numCow):
    #     res[imgPaths[i]] = dfs[i]        
    
    # save(res,'best100Distance.pkl')
    


    #calOneDistance(50)

    