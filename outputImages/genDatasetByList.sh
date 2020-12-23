#!/bin/bash

if [ $# -lt 3 ]; then
    echo
    echo " Usage: $0 <dataset> <imgPreCowDir> <outDir>"
    echo
    exit 1
fi

dataset=$1; shift
imgPreCowDir=$1; shift
outDir=$1; shift

cowList=$imgPreCowDir.imgPerCow
numCow=100

eids=$(cat $cowList | sort -r -n -k 2 | head -n $numCow | awk '{print $1}')
numEid=$(echo "$eids" | wc | awk '{print $1}')

counter=1

if [ ! -d $outDir ]; then
    mkdir -p $outDir
fi  

echo "Generating symlink to $outDir ..."
set -e
for eid in $eids
do
    printf "\r%6d/%d eids" $counter $numEid    
    cowPath=$(realpath $dataset/$eid)
    if [ -d $cowPath ]; then
        ln -s $cowPath $outDir/$eid
    fi          
    ((counter++))
    
done
echo
