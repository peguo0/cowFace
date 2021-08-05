#/usr/bin/python3
import analysis
import topRanking

cowListPath = '/data/gpueval/imageProcessing/peguo0/cowFace/analysis/cowList/cowList_991_black.txt'

def loadCowList(filePath):
    with open(filePath, 'r') as f:
        lines = [line.rstrip('\n') for line in f]
    return lines

def getNumberOfBlackCowImages(imgPaths, eids_blackCows):
    totalBlackCowImages = 0
    for imgPath in imgPaths:
        eid = analysis.getEid(imgPath)
        if eid in eids_blackCows:
            totalBlackCowImages = totalBlackCowImages + 1
    return totalBlackCowImages 

def stat_5NN(eids_blackCows):
    eitDict = analysis.loadPkl('cowId.faceBennett.20200801-20200821_model_top1000.222_epoch40_excludeBWP.fv.best100DistancePerImg.pkl')

    numTop=5
    excluded,errorTop=topRanking.errorTopN(eitDict,numTop)
    haveError=errorTop.loc[errorTop['errorCount']>0]

    imgPaths = haveError['imgPath'].values.tolist()
    totalBlackCowImages = getNumberOfBlackCowImages(imgPaths, eids_blackCows)
    print('For wrong inference images, number of black cow (5NN): ', totalBlackCowImages)

def stat_nearestCentroid(eids_blackCows):
    mciDf=analysis.loadPkl("cowId.faceBennett.20200801-20200821_model_top1000.222_epoch40_excludeBWP.fv.ranking.pkl")
    badDf=mciDf[mciDf['rank']>0]

    imgPaths = badDf['path'].values.tolist()
    totalBlackCowImages = getNumberOfBlackCowImages(imgPaths, eids_blackCows)
    print('For wrong inference images, number of black cow (Nearest Centroid): ', totalBlackCowImages)

def stat_all(eids_blackCows):
    fvPath = '/data/gpueval/imageProcessing/peguo0/cowFace/analysis/cowId.faceBennett.20200801-20200821_model_top1000.222_epoch40_excludeBWP.fv' # 991 cows
    # fvPath = 'cowId.faceBennett.20200409-20200731_top1000_model_top1000.222_epoch50.fv' # 1000 cows

    eidDict,dfDict = analysis.loadFv(fvPath)
    totalBlackCowImages = 0
    for eid,  content in eidDict.items():
        if eid in eids_blackCows:
            totalBlackCowImages = totalBlackCowImages + len(content['imgPath'])
    print('Total number of black cow images is: ', totalBlackCowImages)

def main():    
    eids_blackCows = loadCowList(cowListPath)

    stat_all(eids_blackCows)
    stat_5NN(eids_blackCows)
    stat_nearestCentroid(eids_blackCows)

if __name__ == '__main__':
    main()