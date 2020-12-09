#!/bin/bash

if [ $# -lt 3 ]; then
    echo
    echo " Usage: $0 <numTop> <datasetDir> <outDir>"
    echo
    exit 1
fi

numCow=$1; shift
dataset=$1; shift
outDir=$1; shift

tmpFile=/dev/shm/$0.tmp
eidFile=/dev/shm/$0.eid

stats="$dataset.imgPerCow"
echo "Gathering stats: $stats ..."
echo -n > $stats 

dirs=$(find -L $dataset -type d | sed '1d')

for dir in $dirs
do
    eid=$(basename $dir)
    num=$(find $dir -name "*.png" | wc -l)
    echo "$eid $num" >> $stats
done

totCow=$(wc -l $stats | awk '{print $1}')

echo "Selecting the top $numCow cows out of $totCow"
eids=$(cat $stats | sort -r -n -k 2 | head -n $numCow | awk '{print $1}')
numEid=$(echo "$eids" | wc | awk '{print $1}')

counter=1

if [ ! -d $outDir ]; then
    mkdir -p $outDir
fi  

echo "Generating symlink to $outDir ..."
#echo -n > $tmpFile
set -e
for eid in $eids
do
    printf "\r%6d/%d eids" $counter $numEid
    
    cowPath=$(realpath $dataset/$eid)
    ln -s $cowPath $outDir/$eid    
#     files=$(find $dataset/$eid -name "*.png")
#     if [ ! -d $outDir/$eid ]; then
#         mkdir -p $outDir/$eid 
#     fi
#     for f in $files
#     do
#         path=$(realpath $f)        
#         ln -s $path $outDir/$eid/$(basename $f)
#     done
    ((counter++))
    
done
echo
