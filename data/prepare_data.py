import argparse
import concurrent.futures
import os
import pickle

import cv2
from tqdm import tqdm


def process_img(inpath, outpath, args, pbar):
    
    if hasattr(args, 'preprocessFunction'):
        bgr =  args.preprocessFunction(inpath)
    else:
        bgr = cv2.imread(inpath)
        
    if args.cropx0y0x1y1 is not None:
        x0, y0, x1, y1 = map(int, args.cropx0y0x1y1.split(","))
        bgr = bgr[y0:y1, x0:x1, :]
    if args.width is not None and args.height is not None:
        bgr = cv2.resize(bgr, (args.width, args.height))
    d = os.path.dirname(outpath)
    os.makedirs(d, exist_ok=True)
    cv2.imwrite(outpath, bgr)
    pbar.update(1)


def generate_val(cows, outpath, max_pairs_per_cow=3):

    # get all pairs:
    pairs = []
    for cow, imgpaths in cows.items():
        # ok, everything's a pair inside imgpaths, but for a small amount of data, let's just append sequential instead
        # of combinatorially ... and only do upto
        for i in range(1, min(max_pairs_per_cow + 1, len(imgpaths))):
            pairs.append((cow, imgpaths[i - 1]["processed_path"], imgpaths[i]["processed_path"]))

    # get all non-pairs:
    nonpairs = []
    # ok, there's a lot of non-pairs, so just compare the first image of each cow
    for cow, imgpaths in cows.items():
        for cow2, imgpaths2 in list(cows.items())[:max_pairs_per_cow]:
            nonpairs.append((cow, cow2, imgpaths[0]["processed_path"], imgpaths2[0]["processed_path"]))

    # get the list for insightface format:
    bins = []
    issame = []
    for _, path1, path2 in pairs:
        with open(path1, "rb") as f:
            bins.append(f.read())
        with open(path2, "rb") as f:
            bins.append(f.read())
        issame.append(True)
    for _, _, path1, path2 in nonpairs:
        with open(path1, "rb") as f:
            bins.append(f.read())
        with open(path2, "rb") as f:
            bins.append(f.read())
        issame.append(False)
    bins = bins * 10
    issame = issame * 10
    with open(outpath, "wb") as f:
        pickle.dump((bins, issame), f, protocol=pickle.HIGHEST_PROTOCOL)


def get_splits(indir,testPercent,valPercent):
    cows = {}
    for label in os.listdir(indir):
        imgdir = os.path.join(indir, label)
        cows[label] = []
        for imgname in os.listdir(imgdir):
            imgpath = os.path.join(imgdir, imgname)
            cows[label].append({"raw_path": imgpath})

    trainPercent=100 - testPercent - valPercent
    trainIdLim=round(trainPercent/100.0*len(cows))
    valIdLim=trainIdLim + round(valPercent/100.0*len(cows))
    print(len(cows))
    ids = list(cows.keys())

    trainDataset={k: cows[k] for k in ids[: trainIdLim]}
    valDataset={k: cows[k] for k in ids[trainIdLim: valIdLim]}
    testDataset={k: cows[k] for k in ids[valIdLim:]}
    
    return {
        "train": trainDataset,
        "test": testDataset,
        "val": valDataset,
    }


def main(args):

    tasks = []
    os.makedirs(args.outdir, exist_ok=True)
    print("getting splits")
    testPercent=args.testPercent
    valPercent=args.valPercent

    if hasattr(args, 'notest') and args.notest :
        testPercent=0
    
    splits = get_splits(args.indir,testPercent,valPercent)
    
    print("split sizes:")
    print({k: len(v) for k, v in splits.items()})
    for splitname, cows in splits.items():
        print(splitname)
        odir = os.path.join(args.outdir, splitname)
        os.makedirs(odir, exist_ok=True)

        # process the images:
        tasks = []
        for cowid, imgs in cows.items():
            for d in imgs:
                d["processed_path"] = os.path.join(
                    odir, cowid, os.path.splitext(os.path.basename(d["raw_path"]))[0] + ".jpg"
                )
                tasks.append((d["raw_path"], d["processed_path"]))
        pbar = tqdm(unit="img", total=len(tasks))
        with concurrent.futures.ThreadPoolExecutor(max_workers=128) as executor:
            futures = {executor.submit(process_img, inpath, outpath, args, pbar): inpath for inpath, outpath in tasks}
            for future in concurrent.futures.as_completed(futures):
                _ = futures[future]
                try:
                    _ = future.result()
                except Exception as exc:
                    print(exc)

        # create the val:
        print("creating val")
        generate_val(cows, os.path.join(args.outdir, splitname + ".bin"))


def parse_args():
    parser = argparse.ArgumentParser(description="Create dataset ready for insightface / mxnet")
    parser.add_argument("indir", help="input data dir in form dir/cowid/imgid")
    parser.add_argument("outdir", help="out dir")
    parser.add_argument("--cropx0y0x1y1", required=False, default=None, help="format 'x0,y0,x1,y1'")
    parser.add_argument("--width", type=int, required=False, default=None, help="output image width")
    parser.add_argument("--height", type=int, required=False, default=None, help="output image height")
    parser.add_argument("--notest", action="store_true", required=False, default=False, help="No test dataset. Note: insightFace use 'val' to test their model (best weights set). Where normally 'validation' is for finetune hyperparam (not the weights). DEPRECATED")
    parser.add_argument("--testPercent", type=int, required=False, default=0, help="Percentage of test set. Default 0")
    parser.add_argument("--valPercent", type=int, required=False, default=10, help="Percentage of val set. Default 10")
    
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    main(args)
