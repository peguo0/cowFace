#/usr/bin/python3
import os
import pickle
import csv
from PIL import Image
threshold_colorType = 100000
threshold_LessThan10 = 6000
threshold_MoreThan245 = 600

def loadFile(pickleFile, colorImagesFile):
    if os.path.isfile(pickleFile):
        with open(pickleFile, 'rb') as f:
            imagesColors = pickle.load(f)
            f.close()
    else:
        imagesColors = getImagesColors(colorImagesFile)
        with open(pickleFile, 'wb') as f:
            pickle.dump(imagesColors, f)
            f.close()
    return imagesColors

def getImagesColors(colorImagesFile):
    imagesColors = {}
    with open(colorImagesFile, 'r') as csvFile:
        csvReader = csv.reader(csvFile)
        for row in csvReader:
            imagePath = row[0]
            img = Image.open(imagePath)
            colors = img.getcolors(threshold_colorType)
            imagesColors[imagePath] = colors
            print('Loading: ', imagePath)
    return imagesColors

def getPurpleImages(imagesColors):
    purpleImages = []
    for imagePath, colors in imagesColors.items():
        greenValues = getGreenValues(colors)
        greenLessThan10, greenMoreThan245 = sumGreens(greenValues)
        if greenLessThan10 > threshold_LessThan10 and greenMoreThan245 < threshold_MoreThan245:
            print('Purple image: ', imagePath)
            purpleImages.append(imagePath)
    return purpleImages

def getGreenValues(colors):
    greenValues = []
    for color in colors:
        green = color[1][1]
        greenValues.append(green)
    return greenValues

def sumGreens(greenValues):
    greenLessThan10 = 0
    greenMoreThan245 = 0
    for greenValue in greenValues:
        if greenValue < 10:
            greenLessThan10 = greenLessThan10 + 1
        elif greenValue > 245:
            greenMoreThan245 = greenMoreThan245 + 1
        else:
            continue
    return greenLessThan10, greenMoreThan245

def main():
    colorImagesFile = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_20200409-20200821_pm_116993_color_78226_test.txt'
    pickleFile = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_20200409-20200821_pm_116993_color_78226.pkl'        
    imagesColors = loadFile(pickleFile, colorImagesFile)   
    print('Loading Image Finished.') 
    getPurpleImages(imagesColors)

if __name__ == '__main__':
    main()