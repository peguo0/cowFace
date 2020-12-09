#
# Author: hieu.trinh@lic.co.nz, mhtrinh@gmail.com
# 
# This lib contain a bunch of generic function around video loading and frame
# extraction
# 
#


import os,cv2,sys
import av

#: Path to where are all the videos.
videoSrcDir="/data/imageProcessingNAS/farmVideos/videos_raw"

#: Buffer Folder : structured folder containing once extracted frame
bufferFolder="/data/temp/extractedFrames/all/allImages"
bufferFolder='/home/peguo0/cowFace/outputImages/extractedFrames/' # Peng
bufferFolder='/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/extractedFrames' # Peng

currentVideoPath=""
currentFrame=-1
videoLoader=None

# This dictionary is used as buffer of already processed video during a given session
frameToPtsTable=dict()


#*************************************************
#-- 
#************************************************* 
def getLicVideoFrame(imgPath, saveToBufferFolder=True, videoDir="."):      
    """
    Same as getLicVideoFramePath but instead of a path, return an image in opencv2 format. 
    Or None when error occured
    """
    path=getLicVideoFramePath(imgPath,saveToBufferFolder,videoDir)
    if len(path) < 1:
        return None
    
    return cv2.imread(path)
    

#*************************************************
#-- 
#*************************************************
def getLicVideoFramePath(imgPath, saveToBufferFolder=True, videoDir="."):
    """    
    Return the path to the png of requested frame. Can be "" if error occured during the frame extraction
    This function will check if the png exists in given videoDir
    Otherwise check the buffer folder.
    Otherwise extract the frame from video and save it to buffer folder, by calling getFrameByPtmsec
    
    """
    if (os.path.isfile(imgPath)):
        return imgPath
    
    # Try from videoDir:    
    fn=os.path.basename(imgPath)
    path=os.path.join(videoDir,fn)
    if (os.path.isfile(path)):
        return path
    
    # Try bufferFolder:
    if not "shed" in fn:
        fn = "shed8003993." + fn
    bufferPath=os.path.join(bufferFolder,fn)
    if (os.path.isfile(bufferPath)):
        return bufferPath
    
    # Try extract the frame:
    return getFrameByPtmsec(imgPath)




#*************************************************
#-- 
#*************************************************
def getFrameNameFromMsec(videoFn,msec):
    """
    Return the frame name given video fn and ptmsec
    """
    sec=int(msec/1000)
    leftMsec=msec-sec*1000
    fn="{}.pts{:05d}_{:03d}.png".format(videoFn,sec,leftMsec)
    return fn
    
#*************************************************
#-- 
#*************************************************
def getPtsFromFrameName(frameName):    
    global frameToPtsTable
    fn=os.path.basename(frameName)
    prop=decomposeFrameName(fn)
    videoFn=prop['videoFn']
    videoPath=getVideoPath(videoFn)
    
    
    # Load the new video to our dict if it is a new video
    if (videoPath not in frameToPtsTable):
        videoDec = VideoDecoder(videoPath)
        frame=videoDec.getNextFrame()
        frameCounter=1
        tab=dict()
        
        while frame is not None:
            pts=videoDec.ptmsec
            tab[frameCounter] = pts
            frame=videoDec.getNextFrame()
            frameCounter = frameCounter+1
            
        frameToPtsTable[videoPath]=tab


    

    tab=frameToPtsTable[videoPath]
    frameNum=int(prop['frame'])
    if (frameNum in tab):
        return tab[frameNum]
    else:
        print("ERROR: cannot find frame "+str(frameNum)+" in " + videoPath)
        return ""
    
    
#*************************************************
#-- 
#*************************************************
def decomposeFrameNamePts(imgPath):
    """    
    Given a frame name with correct format ([xxxx.]shed#######.######_######.mp4.pts#####_###.png), this function
    
    will extract the component into a dictionary and return it. 
    
    The dict contain : dayTime, videoFn, shed, msec, day, yearMonth, time
    """
    fn=os.path.basename(imgPath)
    if not "shed" in fn:
        fn = "shed8003993." + fn
    
    fields=fn.split(".")
    if (len(fields) < 5):
        print("ERROR: Un-expected filenaming. Expecting format:  [xxxx.]shed#######.######_######.mp4.pts#####_###.png  Got : "+fn)
        return None
   
    pngIndex=len(fields)-1
    ptsIndex=pngIndex-1
    mp4Index=pngIndex-2
    dayTimeIndex=pngIndex-3
    shedIndex=pngIndex-4
    
    dayTime=fields[dayTimeIndex]
    videoFn=".".join(fields[:ptsIndex])
    shed=fields[shedIndex][4:]
    
    if not fields[ptsIndex].startswith("pts") :
        print("ERROR: Un-expected filenaming. Expecting format:  [xxxx.]shed#######.######_######.mp4.pts#####_###.png  Got : "+fn)
        return None
    
    secArr=fields[ptsIndex][4:].split("_")
    sec=int(secArr[0])
    micro=int(secArr[1])
    msec=sec*1000+micro
    
    dt=dayTime.split("_")
    if (len(dt) != 2):
        print("ERROR: Failed to extract day time from: "+fn)
        return ""
    day=dt[0]
    time=dt[1]
    yearMonth=day[:6]
    
    out=dict()
    out['dayTime'] = dayTime
    out['videoFn'] = videoFn
    out['shed'] = shed
    out['msec'] = msec
    out['day'] = day
    out['yearMonth'] = yearMonth
    out['time'] = time
    
    return out



def extractFrameByPtmsec(videoFnOrPath,ptsList,twoCornersCoordinates): # Peng
    """
    Extract all frame of given pts list to LIC buffer folder
    Return the path list of extracted image.
    Please make sure those pts come from the given video or it will failed to failed to extract and raise ValueError
    """
    res=[]
    if not os.path.isfile(videoFnOrPath):
        path=getVideoPath(videoFnOrPath)
    else:
        path=videoFnOrPath
    
    if not os.path.isfile(path):
        print("ERROR: failed to load the video {}".format(videoFnOrPath))
        return []
    
    videoFn=os.path.basename(path)
    decoder=VideoDecoder(path)
    twoCornersCoordinatesIndex = 0 # Peng 
    for pts in ptsList:
        if pts > 0: # Peng
            imgFn=getFrameNameFromMsec(videoFn,pts)
            imgPath=os.path.join(bufferFolder,imgFn)
            if os.path.isfile(imgPath):
                res.append(imgPath)
                continue
            
            # img=decoder.getFrameByPtmsec(pts,coarseSeeking=False)    
            img=decoder.getFrameByPtmsec(pts,coarseSeeking=True) # Peng
            # cv2.rectangle(img,(twoCornersCoordinates[twoCornersCoordinatesIndex]['x_topLeft'],twoCornersCoordinates[twoCornersCoordinatesIndex]['y_topLeft']),(twoCornersCoordinates[twoCornersCoordinatesIndex]['x_bottomRight'],twoCornersCoordinates[twoCornersCoordinatesIndex]['y_bottomRight']),(0,255,0),2) # Peng
            # img = drawRuler(img)
            cv2.imwrite(imgPath,img)
            res.append(imgPath)  
            twoCornersCoordinatesIndex = twoCornersCoordinatesIndex + 1  # Peng 
    return res

def drawRuler(img): #Peng
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

#*************************************************
#-- 
#*************************************************
def getFrameByPtmsec(imgPath,saveTo="", videoDir=""):
    """
    Given frame name, this function generate the png save to given path

    Default given path is in in the buffer folder.
    
    Return the path to where the frame is saved
    
    videoDir: where to look for the video. If empty, it will look into predefine LIC video 
    storage structure.
    """

    print(imgPath)
    nameDict=decomposeFrameNamePts(imgPath)

    if (nameDict is None):
        return ""
    
    msec=int(nameDict['msec'])   
    videoFn=nameDict['videoFn']
    videoPath=getVideoPath(videoFn,videoDir)
    video=VideoDecoder(videoPath)
    
    img=video.getFrameByPtmsec(msec,coarseSeeking=False)
    
    
    # Save to buffer folder
    if (len(saveTo) < 1):        
        fn=os.path.basename(imgPath)
        outpath=os.path.join(bufferFolder,fn)        
    else:
        outpath=saveTo
    
    cv2.imwrite(outpath,img);
    
    return outpath

    
#*************************************************
#-- 
#*************************************************
def extractFrameToLicBuffer(frameFn):    
    """
    Given frame name, this function generate the png save the buffer folder and return the fill path to the frame
    If the frame already exists in the buffer folder, it will not extracted from the video but just the
    fill file path is returned
    """
    
    # To be safe, we do a basename ...
    frameFn=os.path.basename(frameFn)
    
    outpath=os.path.join(bufferFolder,frameFn)  
    
    if (os.path.isfile(outpath)):
        return outpath
    
    
    nameDict=decomposeFrameNamePts(frameFn)

    if (nameDict is None):
        return ""
    
    msec=int(nameDict['msec'])   
    videoFn=nameDict['videoFn']
    videoPath=getVideoPath(videoFn)
    video=VideoDecoder(videoPath)
    
    img=video.getFrameByPtmsec(msec,coarseSeeking=False)
        
    # Save to buffer folder
    cv2.imwrite(outpath,img);
    
    return outpath
    
    
#*************************************************
#-- 
#*************************************************
def getVideoPath(videoFn,videoDir=""):
    nameDict=decomposeFrameNamePts(videoFn+".pts00000_000.png")
    if (nameDict is None):
        return ""
    
    videoFn=nameDict['videoFn']
    shed=nameDict['shed']
    day=nameDict['day']
    yearMonth=nameDict['yearMonth']
        
    if len(videoDir) > 0:
        videoPath = os.path.join(videoDir,videoFn)
    else:
        videoPath=os.path.join(videoSrcDir,shed,yearMonth,day,videoFn)
    return videoPath

    

#*************************************************
#-- 
#*************************************************
def rewindVideo(videoPath):
    """
    Helper function : rewind the current video
    """    
    global currentFrame
    global currentVideoPath
    global videoLoader
    
    if (videoLoader is not None):
        videoLoader.release()
    videoLoader = cv2.VideoCapture(videoPath)
    currentFrame=0
    currentVideoPath=videoPath


            
#*************************************************
#-- Class responsible for decoding video
#*************************************************
class VideoDecoder():
    """
    Handy class that load a video and can seek by pts
    """
    def __init__(self,videoPath,preloadPts=True):
        self.backwardSeekStepMsec = 100
        self.ptsList=[]
        self.videoPath=videoPath
        self.rewind()
        if (preloadPts):
            self.doPreloadPts()            
            
    """
    Rewind the video.
    Currently we do lazy way: re-open the whole file !
    """
    def rewind(self):
        self.file = None
        self.stream = None
        self.frame = None
        self.ptmsec = None
        self.pts_seen = False
        self.set_file(self.videoPath)        
        
    """
    Preload pts available in the video
    """
    def doPreloadPts(self):
        if (self.videoPath is None):
            return

        # Try to load from pts file
        ptsFilePath=self.videoPath + ".pts"
        realPathPts=os.path.realpath(self.videoPath) + ".pts"
        for path in [ptsFilePath,realPathPts]:
            if (os.path.isfile(path)):
                try:
                    with open(path,"r") as f:
                        for line in f:
                            self.ptsList.append(int(line))
                    break
                except:
                    print("ERROR: failed to read pts file {}".format(path))
        
        # No pts loaded from file. We will create one.
        if len(self.ptsList) < 1 :
        
            # Load the pts table and write it
            for frame in self.next_frame():
                self.ptsList.append(self.ptmsec)
            
            # Rewind
            self.rewind()
            
            # Try to save the list
            try:
                with open(realPathPts,"w") as f:
                    for ptmsec in self.ptsList:
                        f.write(str(ptmsec)+"\n")
            except:
                print("Warning: failed to save the pts list to {}".format(realPathPts))
        
    """ 
    Return the next frame ptmsec using the ptsList
    fromPts: refrence pts from which we try to find the next. The reference pts do not need to exist in the video.
    Return -1 when end of file or when pts list failed to load.
    """
    def getNextFramePtmsec(self,fromPts):
        if (len(self.ptsList) < 1):
            return -1
       
        for ptmsec in self.ptsList:
            if ptmsec > fromPts:
                return ptmsec
            
        return -1
        
        
    # Set which video to load
    def set_file(self, path):
        self.file = av.open(path)
        for s in self.file.streams:
            if s.type == 'video':
                self.stream=s
                break;
        if self.stream is None:
            print("Failed to find a video stream in the given video")
            return          


    # Internal function: go to next frame in the stream
    def next_frame(self):
        try:            
            for packet in self.file.demux(self.stream):
                for frame in packet.decode():
                    ptsec = frame.pts * self.stream.time_base                                
                    self.ptmsec=int(ptsec*1000)                
                    self.frame=frame.to_ndarray(format='bgr24')
                    yield self.frame
        except:
            return None
            
            
    def getNextFrame(self):
        """ 
        Return the next frame.
        Return None at end of file
        """
        try :
            frame=next(self.next_frame())
            return frame
        except:
            return None
        
        
    def seekToMsec(self,msec):
        seek_pts = int(msec/1000 / self.stream.time_base)        
        self.stream.seek(seek_pts)

    def getFrameByPtmsec(self,target_msec,coarseSeeking=False):
        """
        Get a frame given a pts
        """
        with av.logging.Capture() as logs:  # This catch all ffmpeg message into logs
            
            if target_msec < 0:
                target_msec = 0
            seekMarginMsec=1
            seekMsec=target_msec
            self.seekToMsec(seekMsec)
            next(self.next_frame())
            

            # While overseeking : we back step
            while self.ptmsec > target_msec + seekMarginMsec:
                seekMsec -= self.backwardSeekStepMsec
                self.seekToMsec(seekMsec)
                next(self.next_frame())
            
            # Go foward until we reach our target
            while (self.ptmsec < target_msec - seekMarginMsec):
                next(self.next_frame())
            
            if (coarseSeeking):
                return self.frame
            
            # We passed our target
            if (self.ptmsec - target_msec > seekMarginMsec):
                raise ValueError("seeking failed %d" % target_msec)
        
        return self.frame


def getVideoFrame(imgPath,saveToBufferFolder=True, videoDir=""): 
    """
    DECAPRECATED !! This function only work with our old frame number system. You should use 
    
    Given frame name, this function generate the png and return the path to that png.
    
    The png is by default store in the buffer folder (define by a constant in this module).
    
    If saveToBufferFolder is False, the png is saved to /dev/shm/tmpFrame.png    
    
    
    """
    print("WARNING: usage of getVideoFrame is deprecated !!!")
    global currentFrame
    global currentVideoPath
    global videoLoader
    
    nameDict=decomposeFrameName(imgPath)

    if (nameDict is None):
        return ""
    
    frame=int(nameDict['frame'])
    
    videoPath=getVideoPath(imgPath,videoDir)
    
    if (videoPath != currentVideoPath):
        rewindVideo(videoPath)
        
    if (currentFrame > frame-1):
        rewindVideo(videoPath)
        
    while (currentFrame <= frame-1):
        success, image = videoLoader.read()
        if (success):
            currentFrame += 1
        else:
            print("ERROR: failed to get frame "+str(frame)+" from "+videoPath)
            return ""
    
    if (currentFrame != frame):
        printf("ERROR: un-expected code reached !")
        return ""
    
    
    # Save to buffer folder
    if (saveToBufferFolder):        
        fn=os.path.basename(imgPath)
        outpath=os.path.join(bufferFolder,fn)        
    else:
        # We just save to /dev/shm
        outpath="/dev/shm/tmpFrame.png"
        cv2.imwrite(outpath,image);
    
    return outpath
                           


#*************************************************
#-- 
#*************************************************
def decomposeFrameName(frameName):
    """
    DECAPRECATED. We don't use frame number anymore. Replaced by decomposeFrameNamePts
    Given a frame name with correct format ([xxxx.]shed#######.######_######.mp4.#####.png), this function
    will extract the component into a dictionary and return it. 
    The dict contain : dayTime, videoFn, shed, frame, day, yearMonth, time
    """
    print("WARNING: decomposeFrameName is DECAPRECATED. We don't use frame number anymore")
    
    fn=os.path.basename(frameName)
    if not "shed" in fn:
        fn = "shed8003993." + fn
    
    fields=fn.split(".")
    if (len(fields) < 5):
        print("ERROR: Un-expected filenaming. Expecting format:  [xxxx.]shed#######.######_######.mp4.#####.png  Got : "+fn)
        return None
   
    pngIndex=len(fields)-1
    frameIndex=pngIndex-1
    mp4Index=pngIndex-2
    dayTimeIndex=pngIndex-3
    shedIndex=pngIndex-4
    
    dayTime=fields[dayTimeIndex]
    videoFn=".".join(fields[:frameIndex])
    shed=fields[shedIndex][4:]
    frame=int(fields[frameIndex])
    
    dt=dayTime.split("_")
    if (len(dt) != 2):
        print("ERROR: Failed to extract day time from: "+fn)
        return ""
    day=dt[0]
    time=dt[1]
    yearMonth=day[:6]
    
    out=dict()
    out['dayTime'] = dayTime
    out['videoFn'] = videoFn
    out['shed'] = shed
    out['frame'] = frame
    out['day'] = day
    out['yearMonth'] = yearMonth
    out['time'] = time
    
    return out
