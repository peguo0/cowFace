import cv2
import multiprocessing 
#import istartmap 
import os,sys 
import imageLibs 
from tqdm import tqdm
import fnmatch

# indir="cowId.rearBennet.20200801-20200820.pm.extractPos060"
indir="cowId.faceBennett.20200409-20200731_top1000"
# interp=cv2.INTER_LINEAR
interp=cv2.INTER_NEAREST
outdir=indir + ".112to222.nearest"
frontCrop="150,10,1650,910"

#*************************************************
#-- find files with given pattern 
#*************************************************
def find(pattern, path):
    if not isinstance(pattern,list):
        pattern = [pattern]
    result = []
                   
    # Path is actually a list of all paths. We just need to match the filename.
    if isinstance(path,list):
        for apath in path:
            name=os.path.basename(apath)
            for p in pattern:
                if fnmatch.fnmatch(name, p):
                    result.append(apath)
    
    # Doing os.walk ...
    else:
        for root, dirs, files in os.walk(path,followlinks=True):
            for name in files:
                for p in pattern:
                    if fnmatch.fnmatch(name, p):
                        result.append(os.path.join(root, name))
    return result


class Coordinator:
    def __init__(self,outDir,cropCoords,down=112,up=222,inter=cv2.INTER_NEAREST):
        self.cropCoords = cropCoords
        self.outDir=outDir
        self.downSize=(down,down)
        self.upSize=(up,up)
        self.inter=inter
        
    def multiThread(self,dayEid):
        return processOne(dayEid,self.outDir,self.cropCoords,self.downSize,self.upSize,self.inter)

def processOne(imgPath,outDir,cropCoords,downSize,upSize,inter):
    eid=os.path.basename(os.path.dirname(imgPath))
    fn=os.path.basename(imgPath)    
    finalDir=os.path.join(outDir,eid)
    os.makedirs(finalDir, exist_ok = True)
    outpath=os.path.join(finalDir,fn)
    cropped=imageLibs.cropCenter(imgPath,cropCoords)
    down = cv2.resize(cropped,downSize,interpolation=inter)
    up = cv2.resize(down,upSize)
    cv2.imwrite(outpath,up)

def run(inDir,outdir,cropCoords,down,up,inter):
    paths=find("*.png",inDir)
    coordObj = Coordinator(outdir,cropCoords,down,up,inter)
    pool = multiprocessing.Pool()
    outPaths = list(tqdm(pool.imap(coordObj.multiThread, paths), total=len(paths)))

if __name__ == "__main__":    
    run(indir,outdir,frontCrop,112,222,interp)