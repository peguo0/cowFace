#/usr/bin/python3
#Give 1) a video, 2) a protrack log file, and 3) un-synced info; Generate a cow face dataset:
# | - eid1 - xxx.mp4.pts00341_000.x1_y1_x2_y2.bail_4.jpg
# | - eid2 - xxx.mp4.pts00349_000.x1_y1_x2_y2.bail_5.jpg
# | - ...

from generateSubtitle import getVideosMonthDateNTime, getFileName, getLogChunk, getVideoStartTime, getVideoDuration, getVideoCorrespondingLogFile, convertProtrackLogToBailTable, assignStartTime, getBailTableCamera
from videoLibs_peng import extractFrameByPtmsec
import shutil, os
import csv
import pdb

BAR_BLOCKED_BAILS = (15, 26, 10, 37, 53)
X_START = 700
Y_START = 300
X_DISTANCE = 0
Y_DISTANCE = 600
WIDTH = 1100
HEIGHT = 900
RATIOS = [0.0] # [0.4, 0.8]
PAUSEDBAILTHRESHOLD = 13

videoOffsetCsv = '/data/gpueval/imageProcessing/peguo0/cowFace/stat-summary_cameraOffset_135videos_20200401-20200821.csv'

def loadVideoOffsetTable(videoOffsetCsv):
    videoOffsetTable = {} 
    with open(videoOffsetCsv) as csvfile:
        csvReader = csv.reader(csvfile)
        for row in csvReader:
            videoFullPath = row[0]
            videoOffsetValue = float(row[1])
            _, videoDate, _ = getVideosMonthDateNTime(videoFullPath)
            videoOffsetTable[videoDate] = videoOffsetValue
    return videoOffsetTable

def getTwoCornersCoordinate():
# using the global variables, it returns a list of bounding box [{x1,y1,x2,y2},...]
    twoCornersCoordinates = []    
    for ratio in RATIOS:
        x_middle = int(X_START + X_DISTANCE * ratio)
        y_middle = int(Y_START + Y_DISTANCE * ratio)
        x_topLeft = int(x_middle - WIDTH/2)
        x_topLeft = x_topLeft if x_topLeft > 0 else 0
        y_topLeft = int(y_middle - HEIGHT/2)
        y_topLeft = y_topLeft if y_topLeft >0 else 0
        x_bottomRight = int(x_middle + WIDTH/2)
        y_bottomRight = int(y_middle + HEIGHT/2)        
        temp = {'x_topLeft': x_topLeft, 'y_topLeft': y_topLeft, 'x_bottomRight': x_bottomRight, 'y_bottomRight': y_bottomRight}
        twoCornersCoordinates.append(temp)                
    print('bounding box position (x_topLeft, y_topLeft, x_bottomRight, y_bottomRight): ', twoCornersCoordinates)
    return twoCornersCoordinates

def printRejectedBails(bailTable, videoFullPath):
    barBlockedBails = []
    pausedBails = []
    for row in bailTable:
        if not row:
            continue
        if row['bailNumber'] in BAR_BLOCKED_BAILS:
            barBlockedBails.append(row['bailNumber'])
        if isPausedBail(row) == True:
            pausedBails.append(row['bailNumber'])
    print('Bar Blocked Bails for video \'{}\' is:  {}'.format(videoFullPath, barBlockedBails))
    print('Paused Bails for video \'{}\' is:       {}'.format(videoFullPath, pausedBails))

def isPausedBail(bail):
    if bail['syncedEndTime'] - bail['syncedStartTime'] >=  PAUSEDBAILTHRESHOLD:
        return True
    else:
        return False

def extractFrames(bailTable, videoFullPath, twoCornersCoordinates, outputPath):    
    for row in bailTable:
        if not row:
            continue
        # elif row['bailNumber'] not in [3]:
        #     continue
        elif row['syncedStartTime'] == 'NaN' or row['syncedEndTime'] == 'NaN':
            continue
        else:            
            if row['bailNumber'] not in BAR_BLOCKED_BAILS and isPausedBail(row) == False:
                pts_msec = getPts(row, videoFullPath)
                try:
                    buffered_image_path = extractFrameByPtmsec(videoFullPath, pts_msec, twoCornersCoordinates)
                except:
                    print('extract frame error: ',row['videoFullPath'])
                    buffered_image_path = 'NaN'
                print('extracted Frame: ', buffered_image_path)
                saveToEidFolders(row, outputPath, twoCornersCoordinates, buffered_image_path)

def getPts(row, videoFullPath):
    videoStartTime = getVideoStartTime(videoFullPath)
    pts_start = round(row['syncedStartTime']-videoStartTime, 3)
    bailDuration = row['syncedEndTime'] - row['syncedStartTime']
    pts_movedTime = [round(bailDuration*j, 3) for j in RATIOS]
    pts_msec = [int((pts_start+j)*1000) for j in pts_movedTime]
    return pts_msec

def saveToEidFolders(row, outputPath, twoCornersCoordinates, buffered_image_path):
    if buffered_image_path != 'NaN':            
        outputSubEidFolderPath = os.path.join(outputPath,row['eid'])            
        if not os.path.exists(outputSubEidFolderPath):
            os.makedirs(outputSubEidFolderPath)
            print('created folder: ' + outputSubEidFolderPath)            
        for j, imageFullPath in enumerate(buffered_image_path):                
            shutil.copy(imageFullPath, outputSubEidFolderPath)                
            oldImageFileFullName = os.path.basename(imageFullPath)  
            oldImageFullPath = os.path.join(outputSubEidFolderPath, oldImageFileFullName) 
            newImageFileName_firstPart, extension = os.path.splitext(oldImageFileFullName)
            # newImageFileName_addon = '.' + str(twoCornersCoordinates[j]['x_topLeft']) + '_' + str(twoCornersCoordinates[j]['y_topLeft']) + '_' + str(twoCornersCoordinates[j]['x_bottomRight']) + '_' + str(twoCornersCoordinates[j]['y_bottomRight']) + '.bail' + str(row['bailNumber'])
            newImageFileName_addon = '.bail' + str(row['bailNumber'])
            newImageFileFullName = newImageFileName_firstPart + newImageFileName_addon + extension 
            # newImageFullPath = os.path.join(outputSubEidFolderPath, newImageFileFullName) 
            newImageFullPath = os.path.join(outputSubEidFolderPath, oldImageFileFullName)
            os.rename(oldImageFullPath, newImageFullPath)

def getVideoNCorrespondingInfo(csvFileFullPath, logDir):
    videoNCorrespondingLogNUnsync = []
    with open(csvFileFullPath) as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',')
        header = next(csvReader)
        for row in csvReader:
                csv_row = {}
                csv_row['videoFullPath'] = row[1]
                csv_row['unsynced_seconds'] = int(row[7])
                csv_row['logFileFullPaths'] = getVideoCorrespondingLogFile(csv_row['videoFullPath'], logDir)
                videoNCorrespondingLogNUnsync.append(csv_row)
    return videoNCorrespondingLogNUnsync

def getVideoNCorrespondingInfo_onlyVideo(csvFileFullPath, logDir, videoOffsetTable = 'NaN'):
    videoNCorrespondingLogNUnsync = []
    with open(csvFileFullPath) as csvfile:
        csvReader = csv.reader(csvfile)
        for row in csvReader:
                csv_row = {}
                csv_row['videoFullPath'] = row[0]                
                csv_row['logFileFullPaths'] = getVideoCorrespondingLogFile(csv_row['videoFullPath'], logDir)
                if videoOffsetTable == 'NaN':
                    csv_row['unsynced_seconds'] = 0.0
                else:
                    _, videoDate, _ = getVideosMonthDateNTime(csv_row['videoFullPath'])
                    try:
                        csv_row['unsynced_seconds'] = videoOffsetTable[videoDate]
                    except:
                        print('This video is not in the videoOffsetTable:', csv_row['videoFullPath'])
                videoNCorrespondingLogNUnsync.append(csv_row)
    return videoNCorrespondingLogNUnsync

def generateOneVideoCowFace(videoNList, twoCornersCoordinates):
    outputPath = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages' 
    videoFullPath = videoNList['videoFullPath']
    unsynced_seconds = videoNList['unsynced_seconds']
    protrackLogFullPaths = videoNList['logFileFullPaths']   
    videoPath, _, videoFileName, _ = getFileName(videoFullPath)
    videoDuration = getVideoDuration(videoFullPath)
    bailTable_raw = convertProtrackLogToBailTable(protrackLogFullPaths)
    bailTable = assignStartTime(bailTable_raw)
    bailTable_camera = getBailTableCamera(bailTable, unsynced_seconds)
    bailTable_camera_chunk = getLogChunk(bailTable_camera, videoDuration)
    printRejectedBails(bailTable_camera_chunk, videoFullPath)
    # Extract frames:
    extractFrames(bailTable_camera_chunk, videoFullPath, twoCornersCoordinates, outputPath) 
    print('All image saving finished.')

# def main_oneVideo(logDir, twoCornersCoordinates):    
#     videoFullPath = '/home/peguo0/cowFace/videos/202003/20200304/QBH-PlatFace1.shed8003993.20200304_065000.mp4'
#     logFileFullPaths = getVideoCorrespondingLogFile(videoFullPath, logDir)
#     videoNList = {'videoFullPath': videoFullPath, 'unsynced_seconds': 0.0, 'logFileFullPaths': logFileFullPaths}    
#     generateOneVideoCowFace(videoNList, twoCornersCoordinates)
    
def main(): 
    logDir = '/data/imageProcessingNAS/farmVideos/metadata/8003993'
    twoCornersCoordinates = getTwoCornersCoordinate() # twoCornersCoordinates = [{'x_topLeft': 100, 'y_topLeft': 50, 'x_bottomRight': 1100, 'y_bottomRight':650}] 
    
    # # Do one video:
    # main_oneVideo(logDir, twoCornersCoordinates)
    
    # # Batch processing for 40 videos: 
    # csvFileFullPath = '/home/peguo0/cowFace/stat-summary_20200615.csv' 
    # videoNCorrespondingLogNUnsync = getVideoNCorrespondingInfo(csvFileFullPath, logDir)
    # #　print('aaa', videoNCorrespondingLogNUnsync)
    # for videoNList in videoNCorrespondingLogNUnsync:
    #     generateOneVideoCowFace(videoNList, twoCornersCoordinates)

    # Batch processing for multiple videos on rampage:
    # csvFileFullPath = '/data/gpueval/imageProcessing/peguo0/cowFace/QBH-PlatFace1_20200215_20200821_sample100_seed0.csv'
    csvFileFullPath = '/data/gpueval/imageProcessing/peguo0/cowFace/QBH-PlatFace1_20200215_20200821_after20200401_pm.vidList'
    videoOffsetTable = loadVideoOffsetTable(videoOffsetCsv)
    videoNCorrespondingLogNUnsync = getVideoNCorrespondingInfo_onlyVideo(csvFileFullPath, logDir, videoOffsetTable = videoOffsetTable)
    for videoNList in videoNCorrespondingLogNUnsync:
        try:
            generateOneVideoCowFace(videoNList, twoCornersCoordinates)
        except:
            print('this video cannot extract frame, or have no cow: ',  videoNList)

if __name__ == '__main__':
    main()