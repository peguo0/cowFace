#! /urs/bin/python3
import os
import shutil, csv
import numpy as np
from PIL import Image

threshold_colorType = 100000
threshold_infrared = 30000 # Threshold for color and b/w image; it's set based on hist plot.  

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

imagePath = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_20200409-20200821_pm_116993/982123475146853/QBH-PlatFace1.shed8003993.20200721_145000.mp4.pts00157_603.png' # does not have a len value
imagePath = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_20200801-20200821_pm_color_top100InTraining/982091001181323/QBH-PlatFace1.shed8003993.20200803_161000.mp4.pts00029_588.png' # b/w image, len(colors) = 4181
imagePath = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_20200409-20200821_pm_116993_color/982091001181323/QBH-PlatFace1.shed8003993.20200820_152000.mp4.pts00302_218.png' # color image, len(colors) = 69420
imagePath = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_20200409-20200821_pm_116993_bw/982123750661001/QBH-PlatFace1.shed8003993.20200813_154000.mp4.pts00292_288.png'# b/w image, len(colors) = 441
imagePath = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_20200801-20200821_pm_color/982000189576284/QBH-PlatFace1.shed8003993.20200820_150000.mp4.pts00307_958.png' # purple image, len(colors) = 87248
imageType = getImageTypes(imagePath)

print('aaa', imageType)