from splitPurple_findThreshold import loadFile
import csv
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

def main():
    colorImagesFile = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_20200409-20200821_pm_116993_color_78226.txt'
    pickleFile = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_20200409-20200821_pm_116993_color_78226_colorDistribution_green0-10.pkl'
    distribution = loadFile(pickleFile, colorImagesFile)
    imagePixels = [(index, item) for index, item in enumerate(distribution) if item > 3726]

    imageList = []
    with open(colorImagesFile, 'r') as csvFile:
        csvReader = csv.reader(csvFile)
        for row in csvReader:
            imagePath = row[0]
            imageList.append(imagePath)
    # get purple > 3726
    for index, pixels in imagePixels:
        print(imageList[index], pixels)

    # boxplot purple and b/w:
    purpleImages, bwImages = [], []
    for i in distribution:
        (purpleImages if i > 5500 else bwImages).append(i)
    data = [purpleImages, bwImages]
    plt.boxplot(data)
    plt.ylabel("Number of pixels")
    plt.savefig('boxplot_green0-10.png')

    t, p = ttest_ind(purpleImages, bwImages, equal_var = False)
    print('P value: ', p)
    print(ttest_ind(purpleImages, bwImages, equal_var = False))

if __name__ == '__main__':
    main()