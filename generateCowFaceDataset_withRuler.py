#/usr/bin/python3
import cv2
from generateCowFaceDataset import main_oneVideo, logDir, getVideoNLogNUnsync_onlyVideo, generateOneVideoCowFace

def main_withRuler(): 
    # # Do one video:
    # main_oneVideo(logDir, specificBails = [3, 25], drawRulerFlag = True)

    # Batch processing for random videos:
    csvFileFullPath = '/data/gpueval/imageProcessing/peguo0/cowFace/QBH-PlatFace1_20200215_20200821_after20200401_pm_seed0_unique150_rest.vidList' 
    videoNLogNUnsyncTable = getVideoNLogNUnsync_onlyVideo(csvFileFullPath, logDir)
    for videoNLogNUnsync in videoNLogNUnsyncTable:
        generateOneVideoCowFace(videoNLogNUnsync, drawRulerFlag = True, specificBails = [3])


if __name__ == '__main__':
    main_withRuler()