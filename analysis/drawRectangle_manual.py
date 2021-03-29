#/usr/bin/python3
import cv2
import os
import csv

patchColor = (0,0,0) # Patch color; Default: Black
blockedAreas = {'face': (200, 50, 900, 700), 'leg': (900, 50, 1600, 700), 'cow': (200, 50, 1600, 700)}

def main():
    imageList = '/data/gpueval/imageProcessing/peguo0/cowFace/analysis/cowList_inference.txt'
    outDir = '/data/gpueval/imageProcessing/peguo0/cowFace/analysis/cowId.faceBennett.20200801-20200821_faceNLegBlocked/'
    # topLeft = (blockedAreas['face'][0], blockedAreas['face'][1])
    # bottomRight = (blockedAreas['face'][2], blockedAreas['face'][3])
    topLeft = (blockedAreas['cow'][0], blockedAreas['cow'][1])
    bottomRight = (blockedAreas['cow'][2], blockedAreas['cow'][3])
    with open(imageList, 'r') as csvFile:
        csvReader = csv.reader(csvFile)
        for row in csvReader:
            try: 
                imagePath = row[0]                        
                imageFn = os.path.basename(imagePath)
                eid = os.path.basename(os.path.dirname(imagePath))

                img = cv2.imread(imagePath)
                imgBlocked = cv2.rectangle(img, topLeft, bottomRight, patchColor, -1)

                # Get output file name
                imgOutDir = outDir + eid
                if not os.path.exists(imgOutDir):
                    os.mkdir(imgOutDir)
                
                imgOutPath = os.path.join(imgOutDir, imageFn)
                print(imgOutPath)
                cv2.imwrite(imgOutPath, imgBlocked)   
            except Exception:
                print('This file has Error: {}'.format(row[0]))

if __name__ == '__main__':
    main()

