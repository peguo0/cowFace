'generateCowFaceDataset.py' is to create a cow dataset based on the a list of videos and the corresponding Protrack log files.
Note: it treats each video's offset as 0.0 second. 

Inputs:
1) csvFileFullPath: a list of videos e.g. '/data/gpueval/imageProcessing/peguo0/cowFace/QBH-PlatFace1_20200215_20200821_sample100_seed0.csv'
2) logDir: where all Protrack log files stored. e.g. logDir = '/data/imageProcessingNAS/farmVideos/metadata/8003993'
3) outputPath + 4) outputSubFolder: where all eid folders would be saved.

Outputs:
1) a list of eid folders, each of them contains a bunch of frames for this cow, saved at the output path defiend as input 4. 

Dependencies:
1) generateSubtitle
2) videoLibs: which requires av; On rampage, you can have 'av' by using virtualenv '/data/gpueval/imageProcessing/opt/python-virtualenv/tensorflow-latest-stable/'

An example to run it:
1. peguo0@rampage:/data/gpueval/imageProcessing/peguo0/cowFace$ tmux
2. peguo0@rampage:/data/gpueval/imageProcessing/peguo0/cowFace$ source /data/gpueval/imageProcessing/opt/python-virtualenv/tensorflow-latest-stable/bin/activate
3. (tensorflow-1.11-py3.6) peguo0@rampage:/data/gpueval/imageProcessing/peguo0/cowFace$ python3 generateCowFaceDataset.py | tee log.txt

##########################################
##########################################
For drawing ruler or bail sampling purpose, we use 'generateCowFaceDataset_withRuler.py' by controling two parameters:
1) drawRulerFlag = True; 2) specificBails = [3]

An example to run it:
1. peguo0@rampage:/data/gpueval/imageProcessing/peguo0/cowFace$ tmux
2. peguo0@rampage:/data/gpueval/imageProcessing/peguo0/cowFace$ source /data/gpueval/imageProcessing/opt/python-virtualenv/tensorflow-latest-stable/bin/activate
3. (tensorflow-1.11-py3.6) peguo0@rampage:/data/gpueval/imageProcessing/peguo0/cowFace$ python3 generateCowFaceDataset_withRuler.py | tee log.txt


##########################################
##########################################
Old reliable version:
1. peguo0@rampage:/data/gpueval/imageProcessing/peguo0/cowFace$ tmux
2. peguo0@rampage:/data/gpueval/imageProcessing/peguo0/cowFace$ source /data/gpueval/imageProcessing/opt/python-virtualenv/tensorflow-latest-stable/bin/activate
3. (tensorflow-1.11-py3.6) peguo0@rampage:/data/gpueval/imageProcessing/peguo0/cowFace$ python3 generateCowFaceDataset_rampage.py | tee log.txt