import os
import shutil, csv
import numpy as np
from PIL import Image

threshold_colorType = 100000
threshold_infrared = 30000 # Threshold for color and b/w image; it's set based on hist plot.  It was set as 4000. 

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

def createSynbolicLink(imagePath, outputFolder, eid):
    eidFolder = os.path.join(outputFolder, eid)
    if not os.path.exists(eidFolder):
        os.makedirs(eidFolder)
        print('created folder: ' + eidFolder)
    imageFn = os.path.basename(imagePath)       
    if not os.path.exists(os.path.join(eidFolder,imageFn)):
        os.symlink(imagePath, os.path.join(eidFolder, imageFn))

def genDataset(eidFolders, outputFolder_color, outputFolder_bw):
    with open(eidFolders) as csvfile:
        csvReader = csv.reader(csvfile)
        for row in csvReader:
            eidFolder = row[0]
            eid = os.path.basename(eidFolder)
            path, _, files = next(os.walk(eidFolder))
            for imageFn in files:
                imagePath = os.path.join(path, imageFn)
                imageType = getImageTypes(imagePath)
                if imageType == 'color':
                    createSynbolicLink(imagePath, outputFolder_color, eid)
                elif imageType == 'bw':
                    createSynbolicLink(imagePath, outputFolder_bw, eid)
                else:
                    print('Image is not color nor bw: ', imagePath)

def main():
    eidFolders = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowList_1369.txt'
    outputFolder_color = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_color'
    outputFolder_bw = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_bw'

    genDataset(eidFolders, outputFolder_color, outputFolder_bw)

if __name__ == '__main__':
    main()