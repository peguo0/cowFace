#! /usr/bin/python3
# import os

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




