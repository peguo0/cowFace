'generateCowFaceDataset_rampage.py' is to create a cow dataset based on the a list of videos and the corresponding Protrack log files.
Note: it treats each video's offset as 0.0 second. 

Inputs:
1) csvFileFullPath: a list of videos e.g. '/data/gpueval/imageProcessing/peguo0/cowFace/QBH-PlatFace1_20200215_20200821_sample100_seed0.csv'
2) logDir: where all Protrack log files stored. e.g. logDir = '/data/imageProcessingNAS/farmVideos/metadata/8003993'
3) bufferFolder: the folder saved all extracted frames; it defined in videoLibs.py; e.g. bufferFolder = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/extractedFrames' # Peng
4) outputPath: the folder saved all eid folders; it defined at 'generateOneVideoCowFace', line 128. e.g. outputPath = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages'

Outputs:
1) all extrated frames, saved at buffer folder defined as input 3.
2) a list of eid folders, each of them contains a bunch of frames for this cow, saved at the output path defiend as input 4. 

Dependencies:
1) generateSubtitle
2) videoLibs: which requires av; On rampage, you can have 'av' by using virtualenv '/data/gpueval/imageProcessing/opt/python-virtualenv/tensorflow-1.11-py3.6'

An example to run it (remotely on rampage):
1. peguo0@rampage:/data/gpueval/imageProcessing/peguo0/cowFace$ tmux
2. peguo0@rampage:/data/gpueval/imageProcessing/peguo0/cowFace$ source /data/gpueval/imageProcessing/opt/python-virtualenv/tensorflow-1.11-py3.6/bin/activate
2. peguo0@rampage:/data/gpueval/imageProcessing/peguo0/cowFace$ source /data/gpueval/imageProcessing/opt/python-virtualenv/tensorflow-latest-stable/bin/activate
3. (tensorflow-1.11-py3.6) peguo0@rampage:/data/gpueval/imageProcessing/peguo0/cowFace$ python3 generateCowFaceDataset_rampage.py | tee log.txt


For sampling purpose, we need to modify several sections:
1. define which bail to extract: toggle at 'extractFrames' line 63-64
2. turn on/off the ruler: toggle at 'videoLibs.py - extractFrameByPtmsec', line 217


