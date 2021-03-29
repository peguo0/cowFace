from analysis import loadFv, computeClusterCentroid, distance2
import numpy as np
import matplotlib.pyplot as plt 
from scipy.stats import ttest_ind

datasetFn = 'cowId.faceBennett.20200801-20200821_model_top1000.222_batch10_epoch40.fv'
eid1 = '982000161226059'
eid2 = '982091012162172'
eid3 = '982123714450265' # black cow

def sortDictByValue(dict1):
    sorted_dict = {}
    sorted_keys = sorted(dict1, key=dict1.get)  # [1, 3, 2]
    for w in sorted_keys:
        sorted_dict[w] = dict1[w]
    return sorted_dict

def main():
    eidDict,dfDict = loadFv(datasetFn)
    eidDict = computeClusterCentroid(eidDict)

    # distance between cows: 
    distanceDict = {}
    for eid in eidDict:
        d2 = distance2(eidDict[eid1]['centroid'],eidDict[eid]['centroid'])
        distanceDict[eid] = d2
    distanceDict_sorted = sortDictByValue(distanceDict)
    allDistance = list(distanceDict_sorted.values())[1:]
    # allDistance = allDistance[1:]

    # distance between images of one cow: 
    numOfImage = len(eidDict[eid1]['fvs'])
    allDistance_oneCow = []
    for i in range(numOfImage - 1):
        for j in range(i+1, numOfImage):
            ddd = distance2(eidDict[eid1]['fvs'][i],eidDict[eid1]['fvs'][j])
            allDistance_oneCow.append(ddd)
    allDistance_oneCow = sorted(allDistance_oneCow)

    # # distance between images to the center: 
    # numOfImage = len(eidDict[eid1]['fvs'])
    # allDistance_oneCow_toCenter = []
    # for i in range(numOfImage - 1):
    #     ddd = distance2(eidDict[eid1]['centroid'],eidDict[eid1]['fvs'][i])
    #     allDistance_oneCow_toCenter.append(ddd)
    # allDistance_oneCow_toCenter = sorted(allDistance_oneCow_toCenter)
    # print('aaaaa', allDistance_oneCow_toCenter)

    ############
    ############
    # plot among clusters
    plt.figure(1)
    for percentile in [5, 25, 50, 75, 95]:
        print('The {}th percentile is: {}'.format(percentile, np.percentile(allDistance, percentile)))
    plt.plot(allDistance)
    # plt.xlabel('Number of cows')
    # plt.ylabel('Distance to the target cow')
    # plt.savefig('plot_distribution_allCows_temp.png')

    ############
    # plot among images within one cluster
    for percentile in [5, 25, 50, 75, 95]:
        print('The {}th percentile is: {}'.format(percentile, np.percentile(allDistance_oneCow, percentile)))
    plt.plot(allDistance_oneCow)
    plt.xlabel('Number of images')
    plt.ylabel('Squared Distance')
    plt.savefig('plot_distribution_oneCow_temp.png')

    #######
    # plot histagram of all cows:
    bins = [x/10 for x in range(0,30)] # bins = [x/10 for x in range(10,25)]
    plt.figure(2)
    plt.hist(allDistance, bins = bins)
    # plt.xlabel('Distance to the target cow')
    # plt.ylabel('Number of cows')
    # plt.savefig('plot_hist_allCows_temp.png')
    #######
    ## plot histagram of one cow:
    # bins = [x/10 for x in range(0,8)] # bins = [x/10 for x in range(0,8)] 
    # plt.figure(3)
    plt.hist(allDistance_oneCow, bins = bins)
    plt.xlabel('Squared Distance')
    plt.ylabel('Number of images')
    plt.savefig('plot_hist_oneCow_tempAAA.png')

    #######
    # plot boxplot two sets:
    data = [allDistance, allDistance_oneCow]
    plt.figure(4)
    plt.boxplot(data)
    ticks = [1, 2]
    lables = ['allCows', 'oneCow']
    plt.xticks(ticks, lables)
    plt.ylabel('Distacne (suqared)')
    plt.savefig('plot_boxplot_distance_temp.png')

    t,p = ttest_ind(allDistance, allDistance_oneCow, equal_var = False)
    print('P value: ', p)

if __name__ == '__main__':
    main()