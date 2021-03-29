# /usr/bin/python3
import cv2
import os

# imgPath = '/data/gpueval/imageProcessing/peguo0/cowFace/analysis/cowId.faceBennett.20200801-20200821/982000161226059/QBH-PlatFace1.shed8003993.20200803_152000.mp4.pts00395_069.png'
# outDir = '/data/gpueval/imageProcessing/peguo0/cowFace/analysis/testDir/'
# # crop = (150, 10, 1650, 910)
# # width = crop[2] - crop[0]
# # height = crop[3] - crop[1]
# # divides = (3,4) # divide the image into (row,column) divisions/grids 
# patchColor = (0,0,0) # Patch color; Default: Black

# blockedAreas = {'face': (200, 50, 900, 700), 'leg': (900, 50, 1600, 700), 'cow': (200, 50, 1600, 700)}

# def main():
#     topLeft = (blockedAreas['face'][0], blockedAreas['face'][1])
#     bottomRight = (blockedAreas['face'][2], blockedAreas['face'][3])
#     img = cv2.imread(imgPath)
#     imgOut = cv2.rectangle(img, topLeft, bottomRight, patchColor, -1)
    
#     ## image out name:
#     imgOutPath = outDir + 'aaa.png'
#     cv2.imwrite(imgOutPath, imgOut)


#     # # cell_width, cell_height = int(width/divides[1]), int(height/divides[0])
#     # for cell_index_row in range(divides[0]):
#     #     for cell_index_column in range(divides[1]):
#     #         # get imgOut:
#     #         topLeft = (cell_width * cell_index_column + crop[0], cell_height * cell_index_row + crop[1])
#     #         bottomRight = (topLeft[0] + cell_width, topLeft[1] + cell_height)
#     #         img = cv2.imread(imgPath)
#     #         imgOut = cv2.rectangle(img, topLeft, bottomRight, patchColor, -1)
#     #         ## get imgOut Path: 
#     #         imgFnSuffix = '_divides{}x{}_row{}_col{}'.format(divides[0], 
#     #                                                          divides[1], 
#     #                                                          cell_index_row+1, 
#     #                                                          cell_index_column+1)
#     #         imgOutPath = outDir + os.path.splitext(os.path.basename(imgPath))[0] + imgFnSuffix + '.png'
#     #         cv2.imwrite(imgOutPath, imgOut)

# if __name__ == '__main__':
#     main()

aaa = [x/10 for x in range(10,25)]
print(aaa)