#! /urs/bin/python3
import os
from PIL import Image
import matplotlib.pyplot as plt
threshold_colorType = 100000

# Normal:
imagePath = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_20200409-20200821_pm_116993_color/982000189576284/QBH-PlatFace1.shed8003993.20200821_160000.mp4.pts00424_377.png' 
# Purple:
imagePath = '/data/gpueval/imageProcessing/peguo0/cowFace/outputImages/cowFaceDataset_20200409-20200821_pm_116993/982000189576284/QBH-PlatFace1.shed8003993.20200820_150000.mp4.pts00307_958.png'

# Load image
img = Image.open(imagePath)
colors = img.getcolors(threshold_colorType) 

# get rgb channels distribution
rs = []
gs = []
bs = []
for color in colors:
    rgb = color[1]
    r = rgb[0]
    g = rgb[1]
    b = rgb[2] 
    rs.append(r)
    gs.append(g)
    bs.append(b)

# Plot section
bins = range(0,270,10)
plt.figure(1)

plt.subplot(1,3,1)
plt.hist(rs, bins = bins, facecolor='blue')
plt.xlabel('Red')
plt.ylabel('Number of RGB')

plt.subplot(1,3,2)
plt.hist(gs, bins = bins, facecolor='blue')
plt.xlabel('Green')

plt.subplot(1,3,3)
plt.hist(bs, bins = bins, facecolor='blue')
plt.xlabel('Blue')

plt.tight_layout() 
plt.savefig('aaa.png')