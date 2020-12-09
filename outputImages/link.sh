#! /bin/bash

listFile=/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowList_1369_110-130.txt
firstTenLines=$(cat $listFile | head -10)

for line in $firstTenLines
do
    ln -s $line /data/gpueval/imageProcessing/peguo0/cowFace/outputImages/test-10
done

