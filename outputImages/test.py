#! /usr/bin/python3
import os

# def createSynbolicLink(imagePath, outputFolder, eid):
#     eidFolder = os.path.join(outputFolder, eid)
#     if not os.path.exists(eidFolder):
#         os.makedirs(eidFolder)
#         print('created folder: ' + eidFolder)
#     imageFn = os.path.basename(imagePath)       
#     if not os.path.exists(os.path.join(eidFolder,imageFn)):
#         os.symlink(imagePath, os.path.join(eidFolder, imageFn))

# imagePath = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_20200409-20200821_pm_116993_color/982000159019323/QBH-PlatFace1.shed8003993.20200409_160000.mp4.pts00118_189.png'
# outputFolder = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/period_1'
# eid = '111'
# createSynbolicLink(imagePath, outputFolder, eid)

import os
import shutil, csv
import numpy as np
from PIL import Image

threshold_colorType = 100000
threshold_infrared = 4000

def getImageTypes(imagePath):
    img = Image.open(imagePath)
    colors = img.getcolors(threshold_colorType) 
    imageType = None
    try:
        if len(colors) > threshold_infrared:
            imageType = 'color'
        else:
            imageType = 'bw'
    except:
        print('Cannot get image length: ', imagePath)
    return imageType

imagePath = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_20200409-20200821_pm_116993/982123475146853/QBH-PlatFace1.shed8003993.20200721_145000.mp4.pts00157_603.png'
imageType = getImageTypes(imagePath)

print('aaa', imageType)
 