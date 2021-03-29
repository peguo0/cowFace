import topRanking
import analysis
import imageLibs
#import blackCow
import numpy as np

mciDf=analysis.loadPkl("cowId.faceBennett.20200801-20200821_model_top1000.222_epoch50.fv.ranking.pkl")
mciDf=analysis.loadPkl("cowId.faceBennett.20200801-20200821_model_top1000_epoch200.fv.ranking.pkl")
status=[]
for index, row in mciDf.iterrows():
    eid=analysis.getEid(row['path'])
    #status.append(blackCow.isBlackCow(bmap,eid))
#mciDf['isBlack']=status
badDf=mciDf[mciDf['rank']>0]
goodDf=mciDf[mciDf['rank']==0]
numImg=len(mciDf)
nBad=len(badDf)

badDf=analysis.dfSort(badDf,'rank',ascending=False)
for index, row in badDf.iterrows():
    print(row.path)



# img=imageLibs.mosaic(badDf[:50]['path'],numCol=5,margin=5,cropx0y0x1y1=analysis.cropCoords)
# analysis.show(img,'')
