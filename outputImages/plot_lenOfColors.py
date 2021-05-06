import os
import shutil, csv
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import pickle

threshold_colorType = 100000
# threshold_infrared = 4000
threshold_infrared = 30000

def plot_histogram(listToPlot):               
    bins = range(0,threshold_colorType,1000)
    plt.figure(1)
    plt.hist(listToPlot, bins = bins, facecolor='blue')
    plt.xlabel('Color Length')
    plt.ylabel('Number of Images')
    # plt.show()
    plt.savefig('histogram_colorLength.png')

def getImageColorLength(imagePath):
    img = Image.open(imagePath)
    colors = img.getcolors(threshold_colorType) 
    if colors:
        return len(colors)
    else:
        return None

def genColorLength(eidFolders):
    imageColorLength = {}
    with open(eidFolders) as csvfile:
        csvReader = csv.reader(csvfile)
        for row in csvReader:
            eidFolder = row[0]
            path, _, files = next(os.walk(eidFolder))
            for imageFn in files:
                imagePath = os.path.join(path, imageFn)
                colorLength = getImageColorLength(imagePath)
                imageColorLength[imagePath] = colorLength
    return imageColorLength

def getLessThan30000(imageColorLength):
    for key,val in imageColorLength.items():
        if val < threshold_infrared:
            # print('Image: ', key, ' , color_length: ', val)
            print(key)

def loadFile(pickleFile, eidFolders):
    if os.path.isfile(pickleFile):
        with open(pickleFile, 'rb') as f:
            imageColorLength = pickle.load(f)
            f.close()
    else:
        imageColorLength = genColorLength(eidFolders)
        with open(pickleFile, 'wb') as f:
            pickle.dump(imageColorLength, f)
            f.close()
    return imageColorLength

def main():
    eidFolders = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowList_1369_color.txt'
    pickleFile = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowList_1369_color_colorLength.pkl'        
    imageColorLength = loadFile(pickleFile, eidFolders)    
    getLessThan30000(imageColorLength)
    # colorLength = list(imageColorLength.values())
    # colorLength = list(filter(None, colorLength))
    # plot_histogram(colorLength)

if __name__ == '__main__':
    main()