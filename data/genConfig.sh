#!/bin/bash
#
# Generate config for insightFace
#
#

env=/data/gpueval/imageProcessing/opt/python-virtualenv/mxnet-cu90/bin/activate
codeDir=$(dirname $(realpath $0))

templateConf=$codeDir/insightface/recognition/sample_config.py

if [ $# -lt 2 ]; then
    echo
    echo " Usage: $0 <mxnet data dir path> <numUniqCow>"
    echo
    exit 1
fi

dataDirPath=$(realpath $1); shift
numCow=$1; shift
outConfig=config.$(basename $dataDirPath).$(date +%"Y%m%d").py

cp $templateConf $outConfig

cat <<EOT >> $outConfig

dataset.cowid = edict()
dataset.cowid.dataset = "cowid"
dataset.cowid.dataset_path = "$dataDirPath"
dataset.cowid.num_classes = $numCow
dataset.cowid.image_shape = (112, 112, 3)
dataset.cowid.val_targets = ["val"]

EOT

echo "$outConfig generated"
