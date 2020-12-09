
import cv2
import math
import numpy as np 
from matplotlib import pyplot as plt

def stitch(img1,img2,vertically,margin=0,colorBGR=(0,0,0)):
    if img1 is None:
        return img2
    if img2 is None:
        return img1

    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]



    #create empty matrix
    if (vertically):
        res = np.zeros((h1+margin+h2, w1,3), np.uint8)
        res[:,:]=colorBGR

        if (w1 > w2):
            tmp=np.zeros((h2, w1,3), np.uint8)
            tmp[:,:]=colorBGR
            tmp[:h2,:w2] = img2
            img2=tmp
            h2, w2 = img2.shape[:2]
        elif (w2 > w1):
            tmp=np.zeros((h1, w2,3), np.uint8)
            tmp[:,:]=colorBGR
            tmp[:h1,:w1] = img1
            img1=tmp
            h1, w1 = img1.shape[:2]

        res[:h1, :w1, :3] = img1
        res[h1+margin:h1+margin+h2, :w1, :3] = img2
    else:
        res = np.zeros((h1, w1+margin+w2,3), np.uint8)
        res[:,:]=colorBGR
        res[:h1, :w1, :3] = img1
        res[:h1, w1+margin:w1+margin+w2, :3] = img2    
    return res

def cropCenter(imgPath,cropx0y0x1y1='480,250,930,530'):
    if isinstance(imgPath,str):
        bgr=cv2.imread(imgPath)
    else:
        bgr=imgPath

    if len(cropx0y0x1y1) < 1:
        return bgr

    x0, y0, x1, y1 = map(int, cropx0y0x1y1.split(","))
    bgr = bgr[y0:y1, x0:x1, :]
    return bgr

def show(bgr,title=""):
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(20,20))
    plt.imshow(rgb)
    plt.title(title)
    plt.axis('off')
    plt.show()

 
def showImg(path,title="",cropx0y0x1y1='480,250,930,530'):
    img=cropCenter(path,cropx0y0x1y1=cropx0y0x1y1)
    show(img,title)
    return img

def mosaic(imgPaths,margin=0,color=(0,0,0),numCol=0,numRow=0,cropx0y0x1y1='480,250,930,530'):
    # Work out the number of col, row
    numImg=len(imgPaths)
    if (numCol < 1  and numRow < 1):
        numCol=math.ceil(math.sqrt(numImg))
    elif numCol < 1:
        numCol=round(numImg / numRow)

    col=0
    resImg=None
    rowImg=None
    for i in range(numImg):
                    
        img=cropCenter(imgPaths[i],cropx0y0x1y1)
        rowImg = stitch(rowImg,img,vertically=False,margin=margin,colorBGR=color)

        col += 1
        if col >= numCol :
            resImg = stitch(resImg,rowImg,vertically=True,margin=margin,colorBGR=color)
            rowImg=None
            col=0
    if rowImg is not None:
        resImg = stitch(resImg,rowImg,vertically=True,margin=margin,colorBGR=color)
        
    return resImg


def rescale(imgPath,scaleX,scaleY):
    """
    Rescale an opencv image. 
    imgPath : can be a path or a openCV image/mat
    """
    if isinstance(imgPath,str):
        img=cv2.imread(imgPath)
    else:
        img=imgPath
    
    width = int(img.shape[1] * scaleX)
    height = int(img.shape[0] * scaleY) 
    dim = (width, height)        
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_LINEAR)
    return resized


def fitImageInto(img,width,height,keepRatio=True,fillBGR=None):
    if isinstance(img,str):
        img=cv2.imread(img)
    
    fx = width/img.shape[1]
    fy = height/img.shape[0]

    if keepRatio:
        f=min([fx,fy])
        fx=f
        fy=f 
    
    newWidth=round(fx * img.shape[1])
    newHeight=round(fy * img.shape[0])

    res = np.zeros((height,width,3), np.uint8)
    if not fillBGR is None:        
        res[:,:]=fillBGR

        wStart=round((width-newWidth)/2)
        wEnd=wStart + newWidth

        hStart=round((height-newHeight)/2)
        hEnd=hStart + newHeight

        dest=res[hStart:hEnd,wStart:wEnd,:3]
        res[hStart:hEnd,wStart:wEnd,:3]=cv2.resize(img, (newWidth,newHeight),interpolation = cv2.INTER_LINEAR)
        return res
    else:
        res=cv2.resize(img, (newWidth,newHeight),interpolation = cv2.INTER_LINEAR)
        return res
