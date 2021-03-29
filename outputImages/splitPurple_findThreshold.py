#/usr/bin/python3

import os
import pickle
import csv
from PIL import Image
from splitPurpleImage import getGreenValues
import matplotlib.pyplot as plt
import numpy as np

threshold_colorType = 100000
thresholds1 = (0, 10)
thresholds2 = (245, 256)

def getDistribution(imageList):
    distribution = []
    with open(imageList, 'r') as csvFile:
        csvReader = csv.reader(csvFile)
        for row in csvReader:
            imagePath = row[0]
            img = Image.open(imagePath)
            greenLessThan10 = getNumOfPixel(img, thresholds2)
            distribution.append(greenLessThan10)
    return distribution

def getNumOfPixel(image, thresholds):
    numOfPixels = 0
    colors = image.getcolors(threshold_colorType)
    greenValues = getGreenValues(colors)
    for greenValue in greenValues:
        if greenValue >= thresholds[0] and greenValue < thresholds[1]:
            numOfPixels = numOfPixels + 1
    return numOfPixels

def loadFile(pickleFile, colorImagesFile):
    if os.path.isfile(pickleFile):
        with open(pickleFile, 'rb') as f:
            distribution = pickle.load(f)
            f.close()
    else:
        distribution = getDistribution(colorImagesFile)
        with open(pickleFile, 'wb') as f:
            pickle.dump(distribution, f)
            f.close()
    return distribution

def plot_hist(distribution):
    plt.figure(1)
    plt.hist(distribution, bins = range(0,20000,100))
    plt.xlabel('Green_0-10')
    plt.ylabel('Number of Images')
    plt.savefig('histogram_green_245-255.png')

def main():
    colorImagesFile = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_20200409-20200821_pm_116993_color_78226.txt'
    pickleFile = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_20200409-20200821_pm_116993_color_78226_colorDistribution_green245-255.pkl'
    distribution = loadFile(pickleFile, colorImagesFile)
    # 99 percentile
    a = np.array(distribution)
    percentile_99 = np.percentile(a, 99.9)
    print(percentile_99)

    # # Plot histagram
    plot_hist(distribution)


if __name__ == '__main__':
    main()