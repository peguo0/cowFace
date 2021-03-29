#/usr/bin/python3
import cv2
import os

imgPath = '/data/gpueval/imageProcessing/peguo0/cowFace/analysis/cowId.faceBennett.20200801-20200821/982000161226059/QBH-PlatFace1.shed8003993.20200803_152000.mp4.pts00395_069.png'
outDir = '/data/gpueval/imageProcessing/peguo0/cowFace/analysis/testGrid12/'
crop = (150, 10, 1650, 910)
width = crop[2] - crop[0]
height = crop[3] - crop[1]
divides = (3,4) # divide the image into (row,column) divisions/grids 
patchColor = (0,0,0) # Patch color; Default: Black

def main():
    cell_width, cell_height = int(width/divides[1]), int(height/divides[0])
    for cell_index_row in range(divides[0]):
        for cell_index_column in range(divides[1]):
            # get imgOut:
            topLeft = (cell_width * cell_index_column + crop[0], cell_height * cell_index_row + crop[1])
            bottomRight = (topLeft[0] + cell_width, topLeft[1] + cell_height)
            img = cv2.imread(imgPath)
            imgOut = cv2.rectangle(img, topLeft, bottomRight, patchColor, -1)
            ## get imgOut Path: 
            imgFnSuffix = '_divides{}x{}_row{}_col{}'.format(divides[0], 
                                                             divides[1], 
                                                             cell_index_row+1, 
                                                             cell_index_column+1)
            imgOutPath = outDir + os.path.splitext(os.path.basename(imgPath))[0] + imgFnSuffix + '.png'
            cv2.imwrite(imgOutPath, imgOut)

if __name__ == '__main__':
    main()

