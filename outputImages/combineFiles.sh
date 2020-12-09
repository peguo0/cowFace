#!/bin/bash

inputFile=/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowList_files.txt
outputFile=./cowList_1369_sorted.txt

echo -n > $outputFile
for file in $(< $inputFile)
do
cat $file >> $outputFile
done
