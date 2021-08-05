import topRanking
import analysis
import imageLibs
#import blackCow
import numpy as np

mciDf=analysis.loadPkl("cowId.faceBennett.20200801-20200821_model_uniq_top1000.112_epoch200.fv.ranking.pkl")
# mciDf=analysis.loadPkl("cowId.faceBennett.20200801-20200821_model_uniq_top1000.222_epoch40.fv.ranking.pkl")
# mciDf=analysis.loadPkl("cowId.faceBennett.20200801-20200821_model_uniq_top1000.222.faceUp_epoch40.fv.ranking.pkl")
# mciDf=analysis.loadPkl("cowId.faceBennett.20200801-20200821_model_uniq_top1000.222.bodyDown_epoch40.fv.ranking.pkl")

badDf=mciDf[mciDf['rank']>0]

for path in badDf['path']:
    print(path)

