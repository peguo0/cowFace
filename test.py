#! /usr/bin/python3
import matplotlib.pyplot as plt
import seaborn as sns

def convertTrainLogToDict(trainLogPath):
    logDict = {}
    currentStat = {'epoch': None, 'train_acc': None, 'train_lossvalue': None, 'epoch_val': None, 'xNorm': None, 'val_acc': None}
    with open(trainLogPath) as fp:
        for line in fp:
            if 'Saving epoch' in line:
                currentStat['epoch'] = int(line.split()[-1])
                logDict = updateDict(logDict, currentStat)
            if 'Train-acc=' in line:
                currentStat['train_acc'] = float(line.split()[1].split('=')[1])
            if 'Train-lossvalue=' in line:
                currentStat['train_lossvalue'] = float(line.split()[1].split('=')[1])
            if 'lr-batch-epoch:' in line:
                currentStat['epoch_val'] = int(line.split()[3])
            if 'XNorm:' in line:
                currentStat['xNorm'] = float(line.split()[1])
            if 'Accuracy-Flip:' in line:
                currentStat['val_acc'] = float(line.split()[1].split('+-')[0])
    return logDict

def updateDict(logDict, currentStat):
    epoch = currentStat['epoch']
    epoch_val = currentStat['epoch_val']
    if epoch == epoch_val:   
        logDict[epoch] = {'train_acc': currentStat['train_acc'], 'train_lossvalue': currentStat['train_lossvalue'], 'xNorm': currentStat['xNorm'], 'val_acc': currentStat['val_acc']}
    else:
        logDict[epoch] = {'train_acc': currentStat['train_acc'], 'train_lossvalue': currentStat['train_lossvalue']}
    return logDict                 

def main():
    trainLogPath = '/data/gpueval/imageProcessing/peguo0/cowFace/models/cowId.faceBennett.20200401-20200731.color_top100.20201214.20201214/log'
    logDict = convertTrainLogToDict(trainLogPath)
    print('aaa', logDict)
    
if __name__ == '__main__':
    main()

# trainingLog = {1: {'train_acc': 0.01, 'train_lossvalue': 34},
#             2: {'train_acc': 0.09, 'train_lossvalue': 30},
#             3: {'train_acc': 0.19, 'train_lossvalue': 29},
#             4: {'train_acc': 0.32, 'train_lossvalue': 22},
#             5: {'train_acc': 0.55, 'train_lossvalue': 18, 'XNorm': 20.2, 'Accuracy_Flip': 0.80},
#             6: {'train_acc': 0.57, 'train_lossvalue': 17},
#             7: {'train_acc': 0.65, 'train_lossvalue': 15},
#             8: {'train_acc': 0.75, 'train_lossvalue': 12},
#             9: {'train_acc': 0.85, 'train_lossvalue': 6},
#             10: {'train_acc': 0.90, 'train_lossvalue': 3, 'XNorm': 8.54, 'Accuracy_Flip': 0.92}
# }