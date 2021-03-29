#! /usr/bin/python3

import os
import matplotlib.pyplot as plt

def logDictToList_train(trainingLog):
    epochs = list(trainingLog.keys())
    train_acc =[i['train_acc'] for i in trainingLog.values()]
    train_lossvalue =[i['train_lossvalue'] for i in trainingLog.values()]

    return epochs, train_acc, train_lossvalue

def logDictToList_val(trainingLog):
    xNorm = []
    validation_acc = []
    epochs_val = []
    for epoch, value in trainingLog.items():
        if 'xNorm' in value:
            epochs_val.append(epoch)
            xNorm.append(value['xNorm'])
            validation_acc.append(value['val_acc'])
    return epochs_val, xNorm, validation_acc   

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
    # trainLogPath = '/data/gpueval/imageProcessing/peguo0/cowFace/models/cowId.faceBennett.20200401-20200731.color_top100.20201214.20201214/log' # train with 100 cows.
    # trainLogPath = '/data/gpueval/imageProcessing/peguo0/cowFace/models/cowId.faceBennett.20200401-20200731.color_top1000.20201208.20201221/log' # train with 1000 cows.
    # trainLogPath = '/data/gpueval/imageProcessing/peguo0/cowFace/models/cowId.faceBennett.20200401-20200731.color_top1000.222.20210113.20210113/log' # train with 1000 cows; 222. 
    # trainLogPath = '/data/gpueval/imageProcessing/peguo0/cowFace/models/cowId.faceBennett.20200401-20200731.color_top1000.20201208.20210125/log' # train with 1000 cows.
    # trainLogPath = '/data/gpueval/imageProcessing/peguo0/cowFace/models/cowId.faceBennett.20200401-20200731.color_top1000.222.20210113.20210202/log' # train with 1000 cows.
    # trainLogPath = '/data/gpueval/imageProcessing/peguot0/cowFace/models/cowId.faceBennett.20200401-20200731.color_top1000.222.bodyDown.20210305.20210305/log' # train with 1000 cows bodyDown.
    trainLogPath = '/data/gpueval/imageProcessing/peguo0/cowFace/models/cowId.faceBennett.20200401-20200731.color_top1000.222.faceUp.20210305.20210307/log' # train with 1000 cows faceUp.
    outputDir = '/data/gpueval/imageProcessing/peguo0/cowFace/results_heatmap_histgram'
    outputFn_acc = 'accuracy_train_1000_temp.png'
    outputFn_loss = 'accuracy_train_1000_lossvalue_temp.png'
    logDict = convertTrainLogToDict(trainLogPath)
    epochs, train_acc, train_lossvalue = logDictToList_train(logDict)
    epochs_val, xNorm, validation_acc = logDictToList_val(logDict)

    ##############################
    # Plot section:
    plt.figure(1)
    ax = plt.subplot(111)
    ax.plot(epochs, train_acc, label='training-acc')
    ax.plot(epochs_val, validation_acc, label = 'validation-acc')
    ax.legend()
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.title('Epoch - Accuracy')
    plt.savefig(os.path.join(outputDir, outputFn_acc))

    plt.figure(2)
    ax = plt.subplot(111)
    ax.plot(epochs, train_lossvalue, label='train_loss_value')
    ax.plot(epochs_val, xNorm, label='xNorm')
    ax.legend()
    plt.xlabel('Epoch')
    plt.ylabel('Loss Value')
    plt.title('Epoch - Loss-value')
    plt.savefig(os.path.join(outputDir, outputFn_loss))
    
if __name__ == '__main__':
    main()