import argparse
import os

import cv2
import mxnet as mx
import numpy as np
from sklearn.preprocessing import normalize
import fnmatch
from tqdm import tqdm

from datetime import datetime

# def do_flip(data):
#    for idx in range(data.shape[0]):
#        data[idx, :, :] = np.fliplr(data[idx, :, :])

defaultCropCoords='480,250,930,530'

class EmbeddingModel:
    """
    modelprefix: path/prefix-####.params Eg: model.epoch-0401.params  => prefix=model.epoch
    """
    def __init__(self, modelprefix, epoch, gpu, imsize,cropCoords=defaultCropCoords):
        self.modelprefix = modelprefix
        self.epoch = epoch
        self.gpu = gpu
        self.cropCoords=cropCoords
        self.nnInputSize=imsize
        # load the model:
        ctx = mx.gpu(self.gpu) if self.gpu >= 0 else mx.cpu()
        sym, arg_params, aux_params = mx.model.load_checkpoint(self.modelprefix, self.epoch)
        all_layers = sym.get_internals()
        sym = all_layers["fc1_output"]
        self.model = mx.mod.Module(symbol=sym, context=ctx, label_names=None)
        self.model.bind(data_shapes=[("data", (1, 3, self.nnInputSize, self.nnInputSize))])
        self.model.set_params(arg_params, aux_params)

    def  cropCenter(self,bgr):
        """
        Return a crop of the image raw for embedding
        """
        cropx0y0x1y1=self.cropCoords
        width=self.nnInputSize
        height=self.nnInputSize

        #bgr=cv2.imread(imgPath)
        x0, y0, x1, y1 = map(int, cropx0y0x1y1.split(","))
        bgr = bgr[y0:y1, x0:x1, :]
        bgr = cv2.resize(bgr, (width, height))
        return bgr

    def preprocessing(self,imgPath):
        bgr=cv2.imread(imgPath)
        return bgr 

    def embedRaw(self,imgPath):
        bgr=self.preprocessing(imgPath)
        cropped=self.cropCenter(bgr)
        return self.embed(cropped)

    def embed(self, bgr):
        # TODO: bgr->rgb?
        # TODO: LR flip?
        d = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        d = np.transpose(d, (2, 0, 1))
        d = np.expand_dims(d, axis=0)
        d = mx.nd.array(d)
        db = mx.io.DataBatch(data=(d,))
        self.model.forward(db, is_train=False)
        embedding = self.model.get_outputs()[0].asnumpy()
        embedding = normalize(embedding)
        embedding = embedding.flatten()
        return embedding

def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path,followlinks=True):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def runInferenceDir(indir,model,outPath):
    # Load all the file path:
    pngs=find("*.png",indir)
    pbar=tqdm(pngs)
    tot=len(pngs)
    f=open(outPath,"w")

    # print header
    f.write(f"# Generated on {datetime.now()}\n")
    f.write(f"# Model prefix={os.path.realpath(model.modelprefix)}\n")
    f.write(f"# Epoch={model.epoch}\n")

    for png in pbar:
        fv=model.embedRaw(png).tolist()
        f.write("{}:{}\n".format(png,",".join(str(x) for x in fv)))
    print("{} generated.".format(outPath))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="cow model test")
    # general
    parser.add_argument("indir", help="directory with input images (raw png). Images can be in subdir")
    parser.add_argument("modelprefix")
    parser.add_argument("modelepoch", type=int)
    parser.add_argument("outPath",help="output file path")
    
    parser.add_argument("--imsize", default=112, type=int)
    parser.add_argument("--gpu", default=0, type=int, help="gpu id")
    parser.add_argument("--flip", default=0, type=int, help="whether do lr flip aug")
    parser.add_argument("--crop", default=defaultCropCoords, type=str, help="Crop coordinate")

    args = parser.parse_args()

    # create model:
    model = EmbeddingModel(modelprefix=args.modelprefix, epoch=args.modelepoch, gpu=args.gpu, imsize=args.imsize,cropCoords=args.crop)

    runInferenceDir(args.indir,model,args.outPath)

    # # Load all the file path:
    # pngs=find("*.png",args.indir)
    # pbar=tqdm(pngs)
    # tot=len(pngs)
    # f=open(args.outPath,"w")
    # for png in pbar:
    #     fv=model.embedRaw(png).tolist()
    #     f.write("{}:{}\n".format(png,",".join(str(x) for x in fv)))
    # print("{} generated.".format(args.outPath))


    # # get an embedding:
    # embs = {}
    # for label in os.listdir(args.indir):
    #     labeldir = os.path.join(args.indir, label)
    #     embs[label] = {"raw": []}
    #     for imgname in os.listdir(labeldir):
    #         path = os.path.join(labeldir, imgname)
    #         print(path, end="\r")
    #         bgr = cv2.imread(path)
    #         embs[label]["raw"].append(model.embed(bgr))
    #         if len(embs[label]["raw"]) > 100:
    #             break
    #     if len(embs) > 100:
    #         break

    # def diff(e1, e2):
    #     dist = np.sum(np.square(e1 - e2))
    #     # sim = np.dot(f1, f2.T)
    #     return dist

    # # get avg and std for each emb:
    # print("internal diffs")
    # for label, d in embs.items():
    #     arr = np.array(d["raw"])
    #     centroid = arr.mean(axis=0)
    #     # get diffs of each from itself
    #     diffs = []
    #     for r in d["raw"]:
    #         diffs.append(diff(centroid, r))
    #     avgdiff = np.mean(diffs)
    #     stddiff = np.std(diffs)
    #     print("%s %0.8f +- %0.8f" % (label, avgdiff, stddiff))
    #     d["centroid"] = centroid
    #     d["diffs_from_own_avg"] = diffs
    #     d["avg_of_diffs_from_own_avg"] = avgdiff
    #     d["std_of_diffs_from_own_avg"] = stddiff

    # # det diffs from each:
    # print("between cow diffs")
    # for label1, d1 in embs.items():
    #     diffs = []
    #     for label2, d2 in embs.items():
    #         if label1 == label2:
    #             continue
    #         diffs.append(diff(d1["centroid"], d2["centroid"]))
    #     avgdiff = np.mean(diffs)
    #     stddiff = np.std(diffs)
    #     d1["avg_centroid_diff_from_others"] = avgdiff
    #     d1["std_centroid_diff_from_others"] = stddiff
    #     print("%s %0.8f +- %0.8f" % (label1, avgdiff, stddiff))
