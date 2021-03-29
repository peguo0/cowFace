#/usr/bin/python3
import cv2
import os
import csv
import numpy as np

patchColor = (0,0,0) # Patch color; Default: Black
blockedAreas = {'face': (200, 50, 900, 700), 'bodyDown': (900, 50, 1600, 700), 
                'face_ellipse':((520, 375), (340, 240)), 'bodyDown_ellipse': ((1150, 375), (400, 240))
                }

imagePath = '/data/gpueval/imageProcessing/peguo0/cowFace/analysis/test_4Block/982000161226059/QBH-PlatFace1.shed8003993.20200803_152000.mp4.pts00395_069.png'
imagePath = '/data/gpueval/imageProcessing/peguo0/cowFace/analysis/test_4Block_polygon2/982000161226059/QBH-PlatFace1.shed8003993.20200806_142000.mp4.pts00189_249.png'
outDir = '/data/gpueval/imageProcessing/peguo0/cowFace/analysis/test_4Block_polygon2/'

def main():
    # imageList = '/data/gpueval/imageProcessing/peguo0/cowFace/analysis/cowList_inference.txt'
    
    img = cv2.imread(imagePath)

    # # draw rectangle:
    # topLeft = (blockedAreas['face'][0], blockedAreas['face'][1])
    # bottomRight = (blockedAreas['face'][2], blockedAreas['face'][3])    
    # imgBlocked = cv2.rectangle(img, topLeft, bottomRight, patchColor, -1)

    # # draw ellipse:
    # ellipse_center = blockedAreas['face_ellipse'][0]
    # ellipse_axes = blockedAreas['face_ellipse'][1]
    # imgBlocked = cv2.ellipse(img, ellipse_center, ellipse_axes, 0, 0,360, patchColor, -1)

    # draw polygon:
    lines_bodyDown = np.array([[880,170], [1550, 260], [1550, 370],[1170,370],[1170,460],[1550,460], [1550,560], [880, 640]])
    # lines_face = np.array([[210, 160], [860, 210], [860, 450],[210,630]])
    # imgBlocked = cv2.polylines(img, [lines_bodyDown], True, (255,255,0), 4)
    imgBlocked = cv2.fillPoly(img, [lines_bodyDown], 0)

    imgOutPath = outDir + 'aaa.png'
    cv2.imwrite(imgOutPath, imgBlocked)

if __name__ == '__main__':
    main()

