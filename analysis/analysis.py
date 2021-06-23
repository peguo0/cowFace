#!/usr/bin/env python3 

import glob
import os,sys
import numpy as np 

from imageLibs import *

from sklearn import datasets
from sklearn.manifold import TSNE
from matplotlib import pyplot as plt
import pandas as pd

import seaborn as sns

from tqdm import tqdm
import cv2
import math
import pickle

cropCoords="170,250,1920,1034"
cropCoords="150,10,1650,910" # Peng - cow
# cropCoords="150,10,900,910" # Peng - faceUp
# cropCoords="900,10,1650,910" # Peng - bodyDown

# eidDict structure :
# eidDict[eid] = dict 
#   eid: the eid string
#   dict: a dict of : 
#     dict['imgPath'] : array of imgPath string
#     dict['fvs'] : array of fv vector corresponding to imgPath array
#


# # Those are the cow that changed their eid.
# eidMap={
#     '982000159018957':'982123714829369',
#     '982123479335814':'982123714829372',
#     '982123520571387':'982123714829374',
#     '982000189575899':'982123714829371'}
eidMap={
    "982123553042212" : "982123750660987",
    "982123714450303" : "982123750661001"
}
#eidMap={}
# # Those are images that are excluded from the analysis
# excludeImage =[
#     'sideDataset.20190401-20190831/982091014657402/shed8003993.20190415_172000.mp4.pts00115_866.png', # bleached
#     'sideDataset.20190401-20190831/982123531951989/shed8003993.20190414_144000.mp4.pts00462_733.png', # bad crop
#     'end'
# ]

# excludeImage = [
#     'topSide.20200801-20200820.pm.222/982123553042029/20200811_152000.png','sideDataset.20200801-20200820.pm/982123553042029/shed8003993.20200811_152000.mp4.pts00046_666.png',
#     'topSide.20200801-20200820.pm.222/982123714450308/20200814_151000.png','cowId.topDownBennett.20200801-20200820/982123714450308/QBH-PortalTopDow.shed8003993.20200814_151000.mp4.pts00126_721.png',
#     'topSide.20200801-20200820.pm.222/982123714450243/20200803_144000.png','cowId.topDownBennett.20200801-20200820/982123714450243/QBH-PortalTopDow.shed8003993.20200803_144000.mp4.pts00060_516.png',
#     'topSide.20200801-20200820.pm.222/982123518698409/20200812_142000.png',
#     'topSide.20200801-20200820.pm.222/982123533468200/20200819_151000.png',
#     'topSide.20200801-20200820.pm.222/982123714829351/20200810_145000.png',
#     'topSide.20200801-20200820.pm.222/982123553042012/20200806_143000.png',    
# ]
excludeImage = []
# def loadBlackCowDict():
#     fn='blackCow.annotation.txt'
#     f=open(fn,"r")  
#     res=dict()  
#     for lineNumber,line in enumerate(f):
#         arr=line.split(",")
#         eidStr=arr[0].split(".")[0]        
#         if (eidStr in eidMap):
#             eid=eidMap[eidStr]
#         else:
#             eid=eidStr
        
#         label=arr[5].strip()
#         if (label == '10000'):
#             status='black'
#         else:
#             status='NotBlack'
        
#         if (eid in res):
#             print("Warning: {} appear more than once in {}. Overwriting status ...".format(eid,fn))
        
#         res[eid] = status
#     return res



def statPerCow(eitDict, mciDf,numTop=5):
    data=dict()

    excluded=[]

    # Error in Top counting
    for img,d2df in eitDict.items():
        if img in excludeImage:
            excluded.append(img)
            continue
        eid=getEid(img)        
        if eid not in data:
            data[eid]={'numImg':0, 'eitCount':0,'mciCount':0, 'numImgCheck':0}

        data[eid]['numImg'] += 1
        imgs=list(d2df[:numTop]['imgPath'])
        errorCount=0
        for path in imgs:
            cow=getEid(path)
            if (cow != eid):
                errorCount += 1
        
        if (errorCount >0):
            data[eid]['eitCount'] += 1

    # Matching-cluster Index counting
    for index, row in mciDf.iterrows():
        if row['path'] in excludeImage:
            continue

        
        eid=getEid(row['path'])
        if (eid not in data):
            print("Eid {} not in data ?? ".format(eid))
            print(crashHere)

        data[eid]['numImgCheck'] += 1
        if (row['rank'] > 0):
            data[eid]['mciCount'] += 1

    #res={'eid':[],'numImg':[], 'eitCount':[],'mciCount':[],'blackCow':[],'eitPercent':[],'mciPercent':[]}
    res={'eid':[],'numImg':[], 'eitCount':[],'mciCount':[],'eitPercent':[],'mciPercent':[]}
    for key,value in data.items():
        if (value['numImgCheck'] != value['numImg']):
            print("WARNING: {} have different number of image: {} vs {} ??".format(key,value['numImg'],value['numImgCheck']))

        if value['numImg'] < numTop:
            continue

        res['eid'].append(key)
        res['numImg'].append(value['numImg'])
        res['eitCount'].append(value['eitCount'])
        res['mciCount'].append(value['mciCount'])
        #res['blackCow'].append(blackCowDict[key])
        res['eitPercent'].append(value['eitCount']/value['numImg']*100)
        res['mciPercent'].append(value['mciCount']/value['numImg']*100)

    print("{} img excluded.".format(len(excluded)))

    return excluded,pd.DataFrame(res)


def getEid(path):
    eid=path.split('/')[1]
    if (eid in eidMap):
        eid=eidMap[eid]
    return eid


def summaryData(dataDirPath):
    dirs=glob.glob(dataDirPath+"/*")

    cows=[]
    count=[]
    for dir in dirs:
        if not os.path.isdir(dir):
            continue
        imgs=[]
        imgs.extend(glob.glob(dir+"/*.jpg"))
        imgs.extend(glob.glob(dir+"/*.png"))
        eid=os.path.basename(dir)
        count.append(len(imgs))
        cows.append(eid)
        #trainStat.append([eid,len(jpgs)])
    
    print("Number of cow: {}".format(len(cows)))
    a=np.array(count)
    quantilesAt=[0,0.25,0.5,0.75,1]
    print("Quantile at {}".format(quantilesAt))
    q=np.quantile(a,quantilesAt)
    print(q)
    print("Total number of images: {}".format(sum(count)))
    plt.hist(count)
    plt.title("Number of image per cow")
    plt.xlabel("Number of image per cow")
    plt.ylabel("Number of cow")
    print()
    return (cows,count)
    #print(trainStat)

# # def trainStat():
# #     summaryData(trainDirPath)



def loadFv(fvPath,exclude=excludeImage,toInclude=None):
    with open(fvPath,"r") as f:
        lines = f.readlines()
    dfDict={'eids':[],'fvs':[],'paths':[]}
    eidDict=dict()
    for line in lines:
        line=line.strip()
        if line.startswith("#"):
            continue 
        arr=line.split(":")
        if (len(arr) != 2): 
            continue
        eidstr=arr[0]
        if (eidstr in exclude):
            continue 
        if toInclude is not None and eidstr not in toInclude:
            continue       
        eid=getEid(eidstr)
        fvstr=arr[1]
        fv=[float(x) for x in fvstr.split(",")]
        dfDict['eids'].append(eid)
        dfDict['fvs'].append(fv)
        dfDict['paths'].append(eidstr)
        
        if (eid not in eidDict):
            eidDict[eid] = {'imgPath':[], 'fvs':[]}
        eidDict[eid]['imgPath'].append(eidstr)
        eidDict[eid]['fvs'].append(fv)

    return (eidDict,dfDict)
    

# def toDict(eids,fvs):
#     res=dict()
#     for i in range(len(eids)):
#         eid=eids[i]
#         if eid not in res:
#             res[eid]={'fvs':[]}

#         res[eid]['fvs'].append(fvs[i])

#     return res


def selectTopCow(eidDict,top):
    #eidDict=toDict(eids,fvs)
    
    # Count them 
    eidVec=[]
    countVec=[]
    for eid in eidDict:
        eidVec.append(eid)
        countVec.append(len(eidDict[eid]['fvs']))
    
    # Sort 
    eidVec=np.array(eidVec)
    countVec=np.array(countVec)
    ind = np.argsort(countVec)[::-1]
    eidVec = eidVec[ind]

    eidTop=[]
    fvTop=[]

    for eid in eidVec[:top]:
        fv=eidDict[eid]['fvs']
        fvTop.extend(fv)
        eidTop.extend([eid]*len(fv))
    
    return eidTop,fvTop
   

def plotTSNE(eids,fvs,showLegend=True):

    X_embedded = TSNE(n_components=2).fit_transform(fvs)
    label=np.array(eids)
    plt.figure(figsize=(12, 10))
    for i, t in enumerate(set(eids)):
        #print("{} - {}".format(i,t))
        idx = label == t
        plt.scatter(X_embedded[idx, 0], X_embedded[idx, 1], label=t,alpha=0.7)  
    if showLegend:
        plt.legend(bbox_to_anchor=(1, 1))
    plt.show()

# def tsneCow(eidList,eidDict=None):    
#     if eidDict is None:
#         if (tsneCow.eidDict is None):
#             print("Loading fvs from disk ...")
#             eidDict,dfDict=loadFv("sideDataset.20190401-20190430.fv")
#             tsneCow.eidDict = eidDict
#         else:
#             eidDict = tsneCow.eidDict


#     eids=[]
#     fvs=[]
#     for cow in eidList:    
#         fvs.extend(eidDict[cow]['fvs'])
#         eids.extend([cow]*len(eidDict[cow]['fvs']))

#     print("Generating TSNE for {} data points".format(len(fvs)))
#     plotTSNE(eids,fvs)
    

# tsneCow.eidDict=None

def plotByEids(eidDict,eids):
    eidWorst=[]
    fvWorst=[]    
    for eid in eids:
        fv=eidDict[eid]['fvs']
        fvWorst.extend(fv)
        eidWorst.extend([eid]*len(fv))    
    plotTSNE(eidWorst,fvWorst)
    return eidWorst,fvWorst

def plotWorstCluster(eidDict,d2Table,numWorst):
    d2Table=d2Table.sort_values(by=['d2']).reset_index(drop=True)
    d2Table['index'] = d2Table.index

    w=d2Table.head(numWorst)
    cows=list(w['cowA'])
    cows.extend(list(w['cowB']))


    #Uniq
    cows=list(set(cows))

    eidWorst=[]
    fvWorst=[]
    #eidDict=toDict(eids,fvs)
    for eid in cows:
        fv=eidDict[eid]['fvs']
        fvWorst.extend(fv)
        eidWorst.extend([eid]*len(fv))
    
    plotTSNE(eidWorst,fvWorst)
    return w,eidWorst,fvWorst



def computeClusterCentroid(eidDict):
    #eidDict=toDict(eids,fvs)
    for cow in eidDict:
        arr = np.array(eidDict[cow]['fvs'])
        centroid = arr.mean(axis=0)
        eidDict[cow]['centroid']=centroid

    return eidDict

def distance2(e1, e2):
    e1=np.array(e1)
    e2=np.array(e2)
    d2 = np.sum(np.square(e1 - e2))
    # sim = np.dot(f1, f2.T)
    return d2

def computeDistancePairs(data):
    cows=list(data.keys())
    #cows=cows[:100]
    d2Table={'d2':[],'cowA':[],'cowB':[],
    #    'numImgCowA':[],
    #    'numImgCowB':[],
    #    'totImg':[]
    }

    pbar=tqdm(total=len(cows)*len(cows)/2)
    count=0

    for i in range(len(cows)-1):
        for j in range(i+1,len(cows)):
            cowA=cows[i]
            cowB=cows[j]
            d2=distance2(data[cowA]['centroid'],data[cowB]['centroid'])
            d2Table['d2'].append(d2)
            d2Table['cowA'].append(cowA)
            d2Table['cowB'].append(cowB)
            #numA=len(data[cowA]['fvs'])
            #numB=len(data[cowB]['fvs'])
            #d2Table['numImgCowA'].append(numA)
            #d2Table['numImgCowB'].append(numB)
            #d2Table['totImg'].append(numA+numB)
            # distances.append(d2)
            # d2Table.extend([d2,cowA,cowB])
            # src.append(cowA)
            # dest.append(cowB)
            pbar.update(1)
            count+=1
    pbar.close()

    return pd.DataFrame(d2Table)

def drawCows(eidDict,eids,imgPerCow,cropx0y0x1y1=cropCoords):
    img=None 
    for eid in eids:
        if eid not in eidDict:
            continue
        line=drawCowHori(eidDict,eid,imgPerCow,0,cropx0y0x1y1=cropx0y0x1y1)
        img=stitch(img,line,True,0)
    return img
    
def drawCowHori(eidDict,eid,numCow,margin=0,cropx0y0x1y1=cropCoords):
    cowList=eidDict[eid]['imgPath']
    img=None
    x0, y0, x1, y1 = map(int, cropx0y0x1y1.split(","))
    width=x1-x0
    height=y1-y0 
    for i in range(numCow):
        if i >= len(cowList) :
            imgA=np.zeros((height,width,3), np.uint8)
        else:
            imgA=cropCenter(cowList[i],cropx0y0x1y1=cropx0y0x1y1)
        img=stitch(img,imgA,False,margin)
    return img 

def drawPair(eidDict,eidA,eidB,numCow,oriVert=True,margin=0):

    cowAList=eidDict[eidA]['imgPath']
    cowBList=eidDict[eidB]['imgPath']
    cowAList.sort()
    cowBList.sort()
    img=None
    for i in range(numCow):
        if i >= len(cowAList) :
            imgA=np.zeros((784,1750,3), np.uint8)
        else:
            imgA=cropCenter(cowAList[i],cropx0y0x1y1=cropCoords)

        if i >= len(cowBList) :
            imgB=np.zeros((784,1750,3), np.uint8)
        else:
            imgB=cropCenter(cowBList[i],cropx0y0x1y1=cropCoords)

        pair=stitch(imgA,imgB,not oriVert,margin)
        #print("{} vs {}".format(cowAList[i],cowBList[i]))

        img=stitch(img,pair,oriVert,0)

    #plt.imshow(img)
    return img

# #def drawNearCows(eidDict,)

def showWorstPairs(eidDict,worstDf):
    numCol=3
    margin=10
    color=(255,255,255)
    numRow=math.ceil(len(worstDf)/numCol)
    fig, axs = plt.subplots(numRow,numCol,figsize=(18,30))

    for index, row in worstDf.iterrows():
        bgr=drawPair(eidDict,row['cowA'],row['cowB'],5)
        plotRow=int(index/numCol)
        plotCol=index % numCol 
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        axs[plotRow, plotCol].imshow(rgb)
        axs[plotRow, plotCol].set_title('d={:.3}'.format(row['d2']))
        axs[plotRow, plotCol].axis('off')
        #show(img,'d={}'.format(row['d2']))

    # Save the full figure...
    fn='worstCluster.png'
    fig.savefig(fn)
    print('{} generated'.format(os.path.realpath(fn)))


def showWorstPairsHori(eidDict,worstDf):
    numCol=3
    margin=10
    color=(255,255,255)
    numRow=math.ceil(len(worstDf))
    fig, axs = plt.subplots(numRow,figsize=(20,20),dpi=400)

    for index, row in worstDf.iterrows():
        bgr=drawPair(eidDict,row['cowA'],row['cowB'],5,oriVert=False)
        #plotRow=int(index/numCol)
        #plotCol=index % numCol 
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        axs[index].imshow(rgb)
        axs[index].set_title('d={:.3}'.format(row['d2']))
        axs[index].axis('off')
        #show(img,'d={}'.format(row['d2']))

    # Save the full figure...
    fn='worstCluster.png'
    fig.savefig(fn,bbox_inches='tight')
    print('{} generated'.format(os.path.realpath(fn)))


# def buildDistanceTable(eidDict):

#     # Flattern the eidDict
#     eids=[]
#     fvs=[]
#     imgPaths=[]

#     for eid in eidDict:
#         eids.extend([eid]* len(eidDict[eid]['imgPath']))
#         fvs.extend(eidDict[eid]['fvs'])
#         imgPaths.extend(eidDict[eid]['imgPath'])

#     # Calculate every pair distances ...
#     d2Dict=dict()
#     tot=int(len(eids)*len(eids)/2)
#     pbar = tqdm(total=tot)
#     counter=0

#     for i in range(len(eids)-1):
#         d2Table={'imgPath':[], 'd2': [], 'eid':[]}
#         for j in range(i+1,len(eids)): 
#             dest=imgPaths[j]           
#             d2=distance2(fvs[i],fvs[j])
#             d2Table['imgPath'].append(imgPaths[j])
#             d2Table['d2'].append(d2)
#             d2Table['eid'].append(eids[j])

#             # Add the symmetry :
#             if (dest not in d2Dict):
#                 d2Dict[dest] = pd.DataFrame({
#                     'imgPath':[imgPaths[i]],
#                     'd2':[d2],
#                     'eid':[eids[i]]
#                 })
#             else:
#                 d2Dict[dest] = d2Dict[dest].append({
#                     'imgPath':imgPaths[i],
#                     'd2':d2,
#                     'eid':eids[i]
#                 },ignore_index=True)
#             #counter += 1
#             pbar.update(1)
#         d2Dict[imgPaths[i]]=pd.DataFrame(d2Table)
#         #if (counter >= 1000):
#         #    break 
#     pbar.close()
#     return d2Dict


def savePkl(df,fn):
    print('Saving to {} ...'.format(fn))
    with open(fn, 'wb') as f:
        pickle.dump(df, f, pickle.HIGHEST_PROTOCOL)


def loadPkl(fn):
    with open(fn, 'rb') as f:
        return pickle.load(f)


def dfSort(df,byAttribute,ascending=True):
    return df.sort_values(by=[byAttribute],ascending=ascending).reset_index(drop=True)

# def calOneDistance(imgPaths,fvs,eids,indexMap,index):
#     i,j=indexMap[index]
#     d2=distance2(fvs[i],fvs[j])
#     return (imgPaths[i],imgPaths[j],d2)

# if __name__ == '__main__':
#     #trainStat()
#     #print()
#     #testStat()
#     #compare()
#     eidDict,eids,fvs=loadFv("sideDataset.20190401-20190430.fv") 
#     # img=drawPair(eidDict,'982000159018957','982123531951905',5,oriVert=True,margin=5)
#     # show(img,'d=2222')

#     indexMap=genMap(10)
#     calOneDistance(imgPaths,fvs,eids,indexMap,40)

  

#     # data=computeClusterCentroid(eids,fvs)
#     # d2Table=computeDistancePairs(data)
    
#     # worstDf,eidBad,fvBad=plotWorstCluster(eids,fvs,d2Table,10)

#     # showWorstPairs(worstDf)


#     d2All = buildDistanceTable(eidDict)
#     saveD2All(d2All)


