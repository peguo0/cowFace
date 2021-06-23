#!/usr/bin/env python3 

import imageLibs
import analysis
import os,sys
import cv2
from tqdm import tqdm


def genThumbnail(fvPath,numSample,outDir):
    eidDict,dfDict=analysis.loadFv(fvPath)
    if not os.path.isdir(outDir):
        os.makedirs(outDir)
    
    print("Output: {}".format(outDir))
    
    for cow in tqdm(eidDict):
        imgPaths=eidDict[cow]['imgPath']
        imgPaths=imgPaths[:numSample]

        img=imageLibs.mosaic(imgPaths,margin=5,color=(0,0,0),numCol=3,numRow=3,cropx0y0x1y1='0,0,1920,1080')
        
        fn="{}.png".format(cow)
        outpath=os.path.join(outDir,fn)

        cv2.imwrite(outpath,img)
        #print("{} generated.".format(outpath))


if __name__ == '__main__':
    # genThumbnail('sideDataset.20190401-20190430.fv',9,'blackCows')
    genThumbnail('cowId.faceBennett.20200801-20200821_model_top1000.222_epoch40_excludeBWP.fv',9,'blackCows')
    
