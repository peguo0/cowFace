#!/bin/bash


# trainScript=/data/gpueval/imageProcessing/hitri0/rnd-cowID/insightface/recognition/train.py
trainScript=/data/gpueval/imageProcessing/peguo0/cowFaceBackUp/insightface/recognition/train.py
function cmd() {
   echo "" 
   echo "> $@"
   eval "$@"
}

if [ $# -lt 1 ]; then
    echo " Usage: $0 <config.py path> [gpuId batchSize] [-f] [additional args]"
    echo
    echo "  gpuId    : default 0"
    echo "  batchSize: default 80"
    echo
    exit 1
fi

confPath=$1; shift
gpuId=${1:-0}; shift 
batch=${1:-80}; shift
force=0
if [ "$1" == "-f" ]; then
    force=1
    shift 
fi
moreOpt=$@



configName=$(basename $confPath)
modelDirName=${configName#"config."}
modelDirName=${modelDirName%".py"}.$(date "+%Y%m%d")

trainDir=models/$modelDirName

if [ -d $trainDir ]; then   
    if [ $force -eq 0 ]; then
        echo
        len=30
        echo "WARNING : Ouput folder $trainDir already exists."
        echo "WARNING: We will continue in ${len}s and overwrite the working folder. Please Ctrl+C to stop here."
        while [ $len -gt 0 ]; 
        do
            sleep 1s 
            ((len -= 1))
            echo -e -n "\rContinue in ${len}s ... Please Ctrl+C to stop here"
        done
    fi
else 
    mkdir -p $trainDir
fi 

set -e 
log=$trainDir/log

function main() {
    
    echo
    echo "Model output : $trainDir"
    cmd source /data/gpueval/imageProcessing/opt/python-virtualenv/mxnet-1.5.0-cu101/bin/activate
    cmd cp $confPath $trainDir
    cmd ln -sf $(basename $confPath) $trainDir/config.py 

    cmd export PYTHONPATH=$trainDir
    cmd export CUDA_VISIBLE_DEVICES=$gpuId
    cmd python3 -u $trainScript --ckpt 2 --loss arcface --dataset cowid --models-root=$trainDir --verbose=1000  --per-batch-size $batch $moreOpt
}


main 2>&1 | tee $log




