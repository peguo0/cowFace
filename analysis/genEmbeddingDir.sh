#!/bin/bash

source /data/gpueval/imageProcessing/opt/python-virtualenv/mxnet-1.5.0-cu101/bin/activate

codeDir=$(dirname $(realpath $0))

if [ $# -lt 5 ]; then
    echo
    echo " Usage: $0 <test img dir> <model prefix> <outFilePath> <epoch> <cropCoords> [others to pass on]"
    echo
    echo "   test img dir : directory (and sub directory) containing images to generate feature vector"
    echo "   model prefix : example: ../models/sideDataset.20200401-202000731.pm.top1000.20200918/r100-arcface-cowid/model.epoch"
    echo "   outFilePath  : feature vector file to be saved to. Format per line: path:float1,float2,float3, ..."
    echo "                    Note: comment line start with '#'"
    echo "   epoch        : epoch to use."
    echo "   cropCoords   : the coordinate to crop out before feeding to insightFace. Eg: 480,250,930,530"
    echo "   others       : Eg: --imsize 222"
    echo
    exit 1
fi

imgDir=$1; shift
modelPrefix=$1; shift 
outPath=$1; shift
epoch=$1;shift
crop=$1; shift
others="$@"


# Find the best epoch: 
#modelDir=$modelDirRoot/r100-arcface-cowid
# lastModelPath=$(ls -1 $modelDir/model-*.params | sort | tail -1)
# lastEpochFn=$(basename $lastModelPath)
# lastEpoch=${lastEpochFn#model-}
# lastEpoch=${lastEpoch%.params}

#echo $LD_LIBRARY_PATH
#export MXNET_CUDNN_AUTOTUNE_DEFAULT=0
cmd="python3 $codeDir/genEmbedding.py $imgDir $modelPrefix $epoch $outPath --crop=$crop $@"
echo "> $cmd"
eval "$cmd"
