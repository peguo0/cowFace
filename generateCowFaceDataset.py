#/usr/bin/python3
#Give 1) a video, 2) a protrack log file, and 3) un-synced info; Generate a cow face dataset:
# | - eid1 - xxx.mp4.pts00341_000.x1_y1_x2_y2.bail_4.jpg
# | - eid2 - xxx.mp4.pts00349_000.x1_y1_x2_y2.bail_5.jpg
# | - ...

from generateSubtitle import getVideosMonthDateNTime, getLogChunk, getVideoStartTime, getVideoDuration, getVideoCorrespondingLogFile, convertProtrackLogToBailTable, assignStartTime, getBailTableCamera, TOTALBAILS
from videoLibs import getFrameNameFromMsec, getLicVideoFrame, getLicVideoFramePath
import shutil, os, cv2
import csv
import pdb

BAR_BLOCKED_BAILS = (15, 26, 10, 37, 53)
RATIO = 0.0 # to control the cow face position. range from 0.0-1.0; When RATIO change, BAR_BLOCKED_BAILS needs to be adjusted too. 
PAUSEDBAILTHRESHOLD = 13 # If bail duration is more than 13 seconds, it treated as a paused bail; we don't do anything with this bail. 
VIDEO_DURATION = 609000 # Each video is 609s(10m9s) long. 

# On Rampage:
logDir = '/data/imageProcessingNAS/farmVideos/metadata/8003993'
outputPath = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages'
outputSubFolder = 'extractedEids'
outputSubFolder_ruler = 'extractedFrames_ruler'
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

def drawRuler(img): 
    x1, y1 = 1500, 30
    w1, w2, w3, w4 = 300, 200, 150, 100
    h = 580
    divisions = 20
    line_thickness_top = 4
    line_thickness_mid = 2
    # draw top and bottom lines:
    x2, y2 = x1 + w1, y1
    x3, y3 = x1, y1 + h
    x4, y4 = x2, y3
    cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), thickness=line_thickness_top)
    cv2.line(img, (x3, y3), (x4, y4), (0, 0, 255), thickness=line_thickness_top)
    # draw middle lines:
    for i in range(1,divisions):
        if i == divisions/2:
            x_i = x1 + w2
            color = (0, 0, 255)
        else:
            if i % 2 == 0:
                x_i = x1 + w3
                color = (0, 255, 0)
            else:
                x_i = x1 + w4
                color = (255, 0 ,0)
        y_i = y1 + int(h/divisions*i)
        cv2.line(img, (x1, y_i), (x_i, y_i), color, thickness=line_thickness_mid)
    return img

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

def extractFrames(bailTable, videoFullPath, drawRulerFlag = False, specificBails = range(1,TOTALBAILS+1)):  
    for row in bailTable:
        if not row:
            continue
        if row['bailNumber'] not in specificBails:
            continue
        if row['syncedStartTime'] == 'NaN' or row['syncedEndTime'] == 'NaN':
            continue
        if row['bailNumber'] not in BAR_BLOCKED_BAILS and isPausedBail(row) == False:
            pts_msec = getPts(row, videoFullPath)                
            if pts_msec > 0 and pts_msec < VIDEO_DURATION:
                try:                                   
                    imgFn = getFrameNameFromMsec(os.path.basename(videoFullPath), pts_msec)
                    bufferedImagePath = getLicVideoFramePath(imgFn, videoDir=os.path.dirname(videoFullPath), coarseSeeking=True)
                    if drawRulerFlag == True:  
                        img = getLicVideoFrame(imgFn, videoDir=os.path.dirname(videoFullPath), coarseSeeking=True)                            
                        img = drawRuler(img)
                        cv2.imwrite(bufferedImagePath,img)
                except:
                    print('extract frame error: ', videoFullPath)
                    continue
                if drawRulerFlag == True:
                    saveToOneFolder(bufferedImagePath)
                else:
                    saveToEidFolders(row, bufferedImagePath)
              
def getPts(row, videoFullPath):
    videoStartTime = getVideoStartTime(videoFullPath)
    pts_start = round(row['syncedStartTime']-videoStartTime, 3)
    bailDuration = row['syncedEndTime'] - row['syncedStartTime']
    pts_movedTime = round(bailDuration*RATIO, 3)
    pts_msec = int((pts_start+pts_movedTime)*1000)
    return pts_msec

def saveToEidFolders(row, bufferedImagePath):
    if bufferedImagePath != 'NaN':            
        outputEidFolder = os.path.join(outputPath, outputSubFolder, row['eid'])            
        if not os.path.exists(outputEidFolder):
            os.makedirs(outputEidFolder)
            print('created folder: ' + outputEidFolder) 
        shutil.copy(bufferedImagePath, outputEidFolder)  

def saveToOneFolder(imagePath):
    imageFn = os.path.basename(imagePath)
    outputDir = os.path.join(outputPath, outputSubFolder_ruler)
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    shutil.copy(imagePath, outputDir)

def getVideoNLogNUnsync(csvFileFullPath, logDir):
    videoNLogNUnsyncTable = []
    with open(csvFileFullPath) as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',')
        header = next(csvReader)
        for row in csvReader:
                csv_row = {}
                csv_row['videoFullPath'] = row[1]
                csv_row['unsyncedSeconds'] = int(row[7])
                csv_row['logFileFullPaths'] = getVideoCorrespondingLogFile(csv_row['videoFullPath'], logDir)
                videoNLogNUnsyncTable.append(csv_row)
    return videoNLogNUnsyncTable

def getVideoNLogNUnsync_onlyVideo(csvFileFullPath, logDir, videoOffsetTable = 'NaN'):
    videoNLogNUnsyncTable = []
    with open(csvFileFullPath) as csvfile:
        csvReader = csv.reader(csvfile)
        for row in csvReader:
                csv_row = {}
                csv_row['videoFullPath'] = row[0]
                csv_row['logFileFullPaths'] = getVideoCorrespondingLogFile(csv_row['videoFullPath'], logDir)
                if videoOffsetTable == 'NaN':
                    csv_row['unsyncedSeconds'] = 0.0
                else:
                    _, videoDate, _ = getVideosMonthDateNTime(csv_row['videoFullPath'])
                    try:
                        csv_row['unsyncedSeconds'] = videoOffsetTable[videoDate]
                    except:
                        print('This video is not in the videoOffsetTable:', csv_row['videoFullPath'])                
                videoNLogNUnsyncTable.append(csv_row)
    return videoNLogNUnsyncTable

def generateOneVideoCowFace(videoNLogNUnsync, drawRulerFlag = False, specificBails = range(1,TOTALBAILS+1)):
    videoFullPath = videoNLogNUnsync['videoFullPath']
    unsyncedSeconds = videoNLogNUnsync['unsyncedSeconds']
    protrackLogFullPaths = videoNLogNUnsync['logFileFullPaths']   

    videoDuration = getVideoDuration(videoFullPath)
    bailTable_raw = convertProtrackLogToBailTable(protrackLogFullPaths)
    bailTable = assignStartTime(bailTable_raw)
    bailTable_camera = getBailTableCamera(bailTable, unsyncedSeconds)
    bailTable_camera_chunk = getLogChunk(bailTable_camera, videoDuration)

    printRejectedBails(bailTable_camera_chunk, videoFullPath)
    # Extract frames:
    extractFrames(bailTable_camera_chunk, videoFullPath, specificBails = specificBails, drawRulerFlag = drawRulerFlag) 
    print('All image saving finished.')

def main_oneVideo(logDir, drawRulerFlag = False, specificBails = range(1,TOTALBAILS+1)):    
    videoFullPath = '/data/imageProcessingNAS/farmVideos/videos_raw/8003993/202004/20200414/QBH-PlatFace1.shed8003993.20200414_143000.mp4' # normal
    # videoFullPath = '/data/imageProcessingNAS/farmVideos/videos_raw/8003993/202004/20200409/QBH-PlatFace1.shed8003993.20200409_141000.mp4' # abnormal: camera_chunk == camera

    logFileFullPaths = getVideoCorrespondingLogFile(videoFullPath, logDir)
    videoNLogNUnsync = {'videoFullPath': videoFullPath, 'unsyncedSeconds': 0.0, 'logFileFullPaths': logFileFullPaths}    
    # generateOneVideoCowFace(videoNLogNUnsync, specificBails = specificBails, drawRulerFlag = drawRulerFlag) # do every bail  
    generateOneVideoCowFace(videoNLogNUnsync, specificBails = [3, 5], drawRulerFlag = True) # do specific and and draw ruler
    
def main(): 
    # # Do one video:
    # main_oneVideo(logDir)

    # Rampage batch:
    csvFileFullPath = '/data/gpueval/imageProcessing/peguo0/cowFace/vidList/QBH-PlatFace1_20200215_20200821_after20200401_pm.vidList'
    videoOffsetTable = loadVideoOffsetTable(videoOffsetCsv)
    videoNLogNUnsyncTable = getVideoNLogNUnsync_onlyVideo(csvFileFullPath, logDir, videoOffsetTable = videoOffsetTable)
    for videoNLogNUnsync in videoNLogNUnsyncTable:
        generateOneVideoCowFace(videoNLogNUnsync)

if __name__ == '__main__':
    main()