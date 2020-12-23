
#/usr/bin/python3
# Given a protrack log file + a mp4 file_name, generate a srt/ssa subtitle file

import os,sys
from datetime import datetime
import copy
import pdb

TOTALBAILS = 54
BAILSHIFT = 31
UNSYNC = 0.0
X_SSA=900
Y_TOP_SSA=200
Y_BOTTOM_SSA=800

def getAllFilesWithExtension(fileDir,extension):
    allFiles = []    
    for root, dirs, files in os.walk(fileDir):
        for file in sorted(files):
            if file.endswith(extension):
                fileFullPath = root + '/' + file
                allFiles.append(fileFullPath)
    return allFiles

# given a list of videos + the directory of all protrack log files ('/home/peguo0/cowFace/PT.log'); return each vidoe's Protrack log files (2 files of that day)
def getVideoNCorrespondingLogList(allVideoPaths, logDir):
    videoNCorrespondingLogList = []
    for videoFullPath in allVideoPaths:
        videoCorrespondingLogFile = getVideoCorrespondingLogFile(videoFullPath, logDir)
        videoNCorrespondingLogList.append([videoFullPath, videoCorrespondingLogFile])
    return videoNCorrespondingLogList

def getVideoCorrespondingLogFile(videoFullPath, logDir):
    videoMonth, videoDate, videoTime  = getVideosMonthDateNTime(videoFullPath)
    videoCorrespondingLogFile = getVideoCorrespondingLog(logDir, videoMonth, videoDate, videoTime)        
    return videoCorrespondingLogFile        

def getVideosMonthDateNTime(videoFullPath):
    _, _, fileName, _ = getFileName(videoFullPath)
    videoDateNTime = fileName.split('.')[2]
    videoDate = videoDateNTime.split('_')[0]
    videoMonth = videoDate[0:6]
    videoTime = videoDateNTime.split('_')[1]
    videoTime = datetime.strptime(videoTime,"%H%M%S").strftime("%H:%M:%S")
    return videoMonth, videoDate, videoTime

def getVideoCorrespondingLog(logDir, videoMonth, videoDate, videoTime):
    logDir = logDir + '/' + videoMonth + '/' + videoDate
    logList = getAllFilesWithExtension(logDir, '.log')    
    logList = filterPT(logList, 'PT')
    logList_halfDay = getLogHalfDay(logList, videoTime)
    return logList_halfDay

def filterPT(logList, startString):
    logList = [logFile for logFile in logList if os.path.split(logFile)[1].startswith(startString)]  
    return logList

def getLogHalfDay(logList, videoTime):
    logList_halfDay = []
    for logFile in logList:
        if getLogSession(logFile) == getSessionFromTime(videoTime):
            logList_halfDay.append(logFile)
    if logList_halfDay:
        return logList_halfDay
    else:
        return logList

def getLogSession(logFile):
    _,_,fileName,_ = getFileName(logFile)
    logTime = fileName.split('-')[2] 
    logTime = datetime.strptime(logTime,"%H%M%S").strftime("%H:%M:%S")
    session = getSessionFromTime(logTime)
    return session

def getSessionFromTime(aTime):
    h = int(aTime.split(':')[0])
    if h < 12:
        session = 'am'
    else:
        session = 'pm'
    return session

def getFileName(fullPath):    
    path, baseName = os.path.split(fullPath)
    fileName,extension = os.path.splitext(baseName)
    return path, baseName, fileName, extension

def convertProtrackLogToBailTable(protrackLogFullPaths):
    if type(protrackLogFullPaths) == str:
        protrackLogFullPaths = [protrackLogFullPaths]
    bailTable = []
    try: 
        for protrackLogFullPath in protrackLogFullPaths:        
            with open(protrackLogFullPath) as fp:
                for line in fp:
                    if checkPEU(line) == True:
                        row = getRawData(line)
                        bailTable.append(row)
    except:
        loadTableError()    
    print("Load table finished.")
    return bailTable  

def checkPEU(line):
    message = line.split()[2]
    firstLetter = message.split(',')[0]
    if firstLetter == 'P' or firstLetter == 'E' or firstLetter == 'U':
        return True
    else: 
        return False

def getRawData(line):   
    eachBail = {}
    dateNTime_line = line.split()[0] + line.split()[1]
    eachBail['endTime'] = datetime.timestamp(datetime.strptime(dateNTime_line, "%d/%m/%Y%H:%M:%S.%f"))
    message = line.split()[2]
    bailNumber = int(message.split(',')[1])
    status = message.split(',')[0]
    eid = message.split(',')[2]  
    if status == 'P':
        eid = message.split(',')[2] + line.split()[3].split(',')[0]
    if status =='U':
        eid = 'Unknown'
    if status == 'E':
        eid = 'Empty'
    eachBail['bailNumber'] = bailNumber
    eachBail['statusPEU'] = status
    eachBail['eid'] = eid
    return eachBail

def loadTableError():
    print("Load Talbe Error. Please check the Protrack log file.")
    raise

def assignStartTime(bailTable):
    for rowIndex, row in enumerate(bailTable):
        if rowIndex == 0:
            bailTable[rowIndex]['startTime'] = 'NaN'
        else:                        
            current_bail = row['bailNumber']
            compared_bail = getComparedBail(current_bail, 1)
            if bailTable[rowIndex-1]['bailNumber'] == compared_bail:
                row['startTime'] = bailTable[rowIndex-1]['endTime']
            else:
                row['startTime'] = 'NaN' 
    return bailTable

def getComparedBail(current_bail, bailShift):
# getComparedBail(31,1) -> 30; getComparedBail(31, -1)-> 32
    assert current_bail > 0 and current_bail <= TOTALBAILS, 'Please make sure current bail is within the range of (0,{})'.format(TOTALBAILS)
    assert abs(bailShift) < TOTALBAILS, 'Please make sure bail shift is lower than total bail: {}.'.format(TOTALBAILS)
    if current_bail > bailShift:
        compared_bail = current_bail - bailShift
        if compared_bail > TOTALBAILS:
            compared_bail = compared_bail-TOTALBAILS
    if current_bail <= bailShift:
        compared_bail = current_bail + TOTALBAILS - bailShift
    return compared_bail

def getBailTableCamera(bailTable, unsyncedSecond = UNSYNC):
    bailTable_camera = [{} for _ in range(len(bailTable))] # assign an empty bailTable_camera, with the same length as bailTable
    for rowIndex, row in enumerate(bailTable):
        if rowIndex < BAILSHIFT:
            continue # the first 30 rows are kept as empty dict
        else:
            current_bail = row['bailNumber']
            compared_bail = getComparedBail(current_bail, BAILSHIFT)
            if bailTable[rowIndex-BAILSHIFT]['bailNumber'] == compared_bail:
                bailTable_camera[rowIndex]['endTime'] = row['endTime']
                bailTable_camera[rowIndex]['startTime'] = row['startTime']
                bailTable_camera[rowIndex]['bailNumber'] = bailTable[rowIndex - BAILSHIFT]['bailNumber']
                bailTable_camera[rowIndex]['statusPEU'] = bailTable[rowIndex - BAILSHIFT]['statusPEU']
                bailTable_camera[rowIndex]['eid'] = bailTable[rowIndex - BAILSHIFT]['eid'] 
                bailTable_camera[rowIndex]['syncedEndTime'], bailTable_camera[rowIndex]['syncedStartTime'] = addUnsync(row['endTime'], row['startTime'], unsyncedSecond)
    return bailTable_camera

def addUnsync(endTime, startTime, unsyncedSecond):
    if endTime == 'NaN' or startTime == 'NaN':
        syncedEndTime = 'NaN'
        syncedStartTime = 'NaN'
    else:
        syncedEndTime = endTime + unsyncedSecond
        syncedStartTime = startTime + unsyncedSecond
    return syncedEndTime, syncedStartTime

def getVideoDuration(videoFullPath):    
    start_time = getVideoStartTime(videoFullPath)
    end_time = start_time + 600.0
    videoDuration = [start_time, end_time]
    return videoDuration

def getVideoStartTime(videoFullPath):
    _, _, fileName, _ = getFileName(videoFullPath)
    videoDateNTime = fileName.split('.')[2]
    videoStartTime = datetime.timestamp(datetime.strptime(videoDateNTime,"%Y%m%d_%H%M%S"))
    return videoStartTime

def getLogChunk(table, videoDuration):
    startIndex = endIndex = -1
    for rowIndex, row in enumerate(table):
        if row and row['syncedStartTime'] != 'NaN' and row['syncedEndTime'] != 'NaN':
            if row['syncedStartTime'] <= videoDuration[0] and row['syncedEndTime'] >= videoDuration[0]:
                startIndex = rowIndex
            if row['syncedStartTime'] <= videoDuration[1] and row['syncedEndTime'] >= videoDuration[1]:
                endIndex = rowIndex
    if startIndex == -1 or endIndex == -1:
        tableChunk = table
    else:
        tableChunk = table[startIndex:endIndex+1]  
    return tableChunk

def generateSrtFile(table, videoDuration, srtFullPath):
    srtFile = open(srtFullPath, 'w')
    count = 1
    for row in table:
        if row and row['syncedStartTime'] != 'NaN':
            if row['syncedStartTime'] >= videoDuration[0] and row['syncedStartTime']<=videoDuration[1]:
                writeOneBailToSrt(srtFile, count, videoDuration, row)
                count = count + 1
    srtFile.close()

def writeOneBailToSrt(srtFile, count, videoDuration, row):
    videoStartTime = videoDuration[0]
    sub_start = row['syncedStartTime'] - videoStartTime
    sub_end = sub_start + 2.0 # subtitle last for 2 seconds
    srtFile.write(str(count) + '\n')
    srtFile.write(convertToSrtSsaFormat(sub_start, 'srt') + ' --> ' + convertToSrtSsaFormat(sub_end, 'srt') + '\n')  
    subtitle = getSubtitle(row)
    srtFile.write(subtitle + '\n')
    srtFile.write('\n')

def getSubtitle(row):
    return 'Bail: ' + str(row['bailNumber']) + '; EID: ' + row['eid']

def convertToSrtSsaFormat(secs, subtitleFormat):
    # secs = 8.259(float), convert to 00:00:08,259
    hours = int(secs/3600)
    mins = int((secs - hours*3600) / 60)
    s = int(secs - hours*3600 - mins*60)
    if subtitleFormat == 'srt': 
        ms=round((secs -  hours*3600 - mins*60 - s)*1000)
        timeStamp = "{:02d}:{:02d}:{:02d},{:03d}".format(hours,mins,s,ms)
    if subtitleFormat == 'ssa':
        ms=round((secs -  hours*3600 - mins*60 - s)*100)
        timeStamp = "{:02d}:{:02d}:{:02d}.{:02d}".format(hours,mins,s,ms)
    return timeStamp

def generateSsaFile(table, videoDuration, ssaFullPath):
    ssaFile = open(ssaFullPath, 'w')
    ssaAddHeader(ssaFile)
    for row in table:
        if row and row['syncedStartTime'] != 'NaN':
            if row['syncedStartTime'] >= videoDuration[0] and row['syncedStartTime']<=videoDuration[1]:
                writeOneBailToSsa(ssaFile, videoDuration, row)
    ssaFile.close()
    
def writeOneBailToSsa(ssaFile, videoDuration, row):
    videoStartTime = videoDuration[0]
    sub_start = row['syncedStartTime'] - videoStartTime
    sub_end = row['syncedEndTime'] - videoStartTime   
    time_ssa_start_ssaFormat = convertToSrtSsaFormat(sub_start, 'ssa')
    time_ssa_end_ssaFormat = convertToSrtSsaFormat(sub_end, 'ssa')
    subtitle = getSubtitle(row)
        
    ssaFile.write("Dialogue: 0,{},{},Default,,0,0,0,,{{\\move({},{},{},{})}}{}\n".format(
            time_ssa_start_ssaFormat,
            time_ssa_end_ssaFormat,
            X_SSA,
            Y_TOP_SSA,
            X_SSA,
            Y_BOTTOM_SSA,
            subtitle))  
    if len(subtitle.split("EID: ")[1]) == 15:
        ssaFile.write("Dialogue: 0,{},{},boundingBox_bail,,0,0,0,,{{\\a5}}{{\\move(0,0,0,440)}}{{\\p1}}m 50 130 l 150 130{{\\p0}}\n".format(
            time_ssa_start_ssaFormat,
            time_ssa_end_ssaFormat))
        ssaFile.write("Dialogue: 0,{},{},grid,,0,0,0,,{{\\a5}}{{\\p1}}m 150 130 l 450 130 m 150 570 l 450 570 m 150 185 l 300 185 m 150 240 l 300 240 m 150 295 l 300 295 m 150 350 l 300 350 m 150 405 l 300 405 m 150 460 l 300 460 m 150 515 l 300 515 m 150 75 l 300 75 m 150 20 l 300 20 m 1300 65 l 1600 65 m 1300 575 l 1600 575{{\\p0}}\n".format(
            time_ssa_start_ssaFormat,
            time_ssa_end_ssaFormat))

def ssaAddHeader(f):
    f.write(r"""[Script Info]
Title: TrajectoryBuilderHeadless cow eid tracking. Version=1
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1294
PlayResY: 964

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,30,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: boundingBox,Arial,30,&HFFFFFFFF,&H000000FF,&H0000FF00,&HFF000000,0,0,0,0,100,100,0,0,1,5,2,2,0,0,0,1
Style: boundingBox_bail,Arial,30,&HFFFFFFFF,&H000000FF,&H00FF0000,&HFF000000,0,0,0,0,100,100,0,0,1,5,2,2,0,0,0,1
Style: grid, Arial,30,&HFFFFFFFF,&H000000FF,&H0000FFFF,&HFF000000,0,0,0,0,100,100,0,0,1,5,2,2,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")

def generateOneVideoSubtitle(videoNList):
    videoFullPath = videoNList[0]
    protrackLogFullPaths = videoNList[1] 

    videoPath, _, videoFileName, _ = getFileName(videoFullPath)
    videoDuration = getVideoDuration(videoFullPath)
    bailTable_raw = convertProtrackLogToBailTable(protrackLogFullPaths)
    bailTable = assignStartTime(bailTable_raw)
    bailTable_camera = getBailTableCamera(bailTable)
    bailTable_camera_chunk = getLogChunk(bailTable_camera, videoDuration) 

    # generate srt file based on video name and the table
    srtFullPath = videoPath + '/' + videoFileName + '.srt'        
    generateSrtFile(bailTable_camera_chunk, videoDuration, srtFullPath)
    print("srt file generated: ", srtFullPath)
    ssaFullPath = videoPath + '/' + videoFileName + '_gridNew.ssa'
    generateSsaFile(bailTable_camera_chunk, videoDuration, ssaFullPath)
    print("ssa file generated: ", ssaFullPath) ### sdf

def main_oneVideo():    
    videoFullPath = '/home/peguo0/cowFace/videos/202003/20200304/QBH-PlatFace1.shed8003993.20200304_063000.mp4'
    protrackLogFullPaths = ['/home/peguo0/cowFace/PT.log/202003/20200304/PT-200304-054816.log']                
    videoNList = [videoFullPath, protrackLogFullPaths]
    generateOneVideoSubtitle(videoNList)    

def main():           
    # main_oneVideo()
    
    # Batch processing:
    logDir = '/home/peguo0/cowFace/PT.log'
    allVideoPaths = getAllFilesWithExtension('/home/peguo0/cowFace/videos/202003', '.mp4') 
    videoNCorrespondingLogList = getVideoNCorrespondingLogList(allVideoPaths, logDir)  
    for videoNList in videoNCorrespondingLogList:
        generateOneVideoSubtitle(videoNList)
    
if __name__ == '__main__':
    main()