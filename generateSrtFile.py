#/usr/bin/python3
# Given a protrack log file + a mp4 file_name, generate a srt file

import os


def getFileName(fullPath):    
    path, baseName = os.path.split(fullPath)
    fileName,extension = os.path.splitext(baseName)
    return path, baseName, fileName, extension

def checkPEU(line):
    return "ture or false"

def getRawDataColumns(line):
    return "a list"

def main():
    protrackLogFullPath = '/data/gpueval/imageProcessing/peguo0/cowFace/PT.log/PT-200128-034738_modified.log'
    protrackLogPath, protrackLogBaseName, protrackLogFileName, protrackLogExtension = getFileName(protrackLogFullPath)

    with open(protrackLogFullPath) as fp:
        for line in fp:
            if checkPEU(line) == True:
                print(line)



if __name__ == '__main__':
    main()