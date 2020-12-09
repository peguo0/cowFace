#!/bin/bash


trainScript=/data/gpueval/imageProcessing/hitri0/rnd-cowID/insightface/recognition/train.py

function cmd() {
   echo "" 
   echo "> $@"
   eval "$@"
}

if [ $# -lt 1 ]; then
    echo " Usage: $0 <config.py path> [gpuId batchSize] [additional args]"
    echo
    echo "  gpuId    : default 0"
    echo "  batchSize: default 80"
    echo
    exit 1
fi

confPath=$1; shift
gpuId=${1:-0}; shift 
batch=${1:-80}; shift
moreOpt=$@

set -e


configName=$(basename $confPath)
modelDirName=${configName#"config."}
modelDirName=${modelDirName%".py"}.$(date "+%Y%m%d")

trainDir=models/$modelDirName

if [ -d $trainDir ]; then   
    echo
    echo "WARNING : Ouput folder $trainDir already exists."
    echo "WARNING: We will continue in 100s and overwrite the working folder. Please Ctrl+C to stop here."
    len=100
    while [ $len -gt 0 ]; 
    do
        sleep 1s 
        ((len -= 1))
        echo -e -n "\rContinue in ${len}s ... Please Ctrl+C to stop here"
    done
else 
    mkdir -p $trainDir
fi

log=$trainDir/log

function main() {
    
    echo
    echo "Model output : $trainDir"
    cmd source /data/gpueval/imageProcessing/opt/python-virtualenv/mxnet-1.5.0-cu101/bin/activate
    cmd cp $confPath $trainDir
    cmd ln -sf $(basename $confPath) $trainDir/config.py 

    cmd export PYTHONPATH=$trainDir
    cmd export CUDA_VISIBLE_DEVICES=$gpuId
    cmd python3 -u $trainScript --ckpt 2 --network r100 --loss arcface --dataset cowid --models-root=$trainDir --verbose=1000  --per-batch-size $batch $moreOpt
}


main 2>&1 | tee $log




