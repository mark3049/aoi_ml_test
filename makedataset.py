import random
import os
from os import path
import glob


def writelist(filename, files):
    with open(filename, 'wt') as fp:
        fp.writelines(files)


if __name__ == "__main__":
    parent = '/home/mark/result'
    files = sorted(glob.glob(path.join(parent, r'**'+os.sep+'*.json'), recursive=True))
    random.shuffle(files)
    c = int(len(files) / 0.75)
    writelist('train.txt', files[:c])
    writelist('test.txt', files[c:])
