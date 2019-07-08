import random
import os
from os import path
import glob
import json
import csv


def read_json(filename):
    with open(filename) as f:
        return json.load(f)


def writecsv(dest, files):
    config = read_json('dataset/config.json')
    with open(dest, 'wt') as fp:
        writer = csv.writer(fp)
        for file in files:
            json_file = file[:-3]+'json'
            obj = read_json(json_file)
            x1 = config['machine'].index(obj['machine'])
            x2 = config['OP'].index(obj['OP'])
            x3 = config['status'].index(obj['status'])
            writer.writerow([file, x1, x2, x3])


if __name__ == "__main__":
    parent = '/home/mark/result'

    files = sorted(glob.glob(path.join(parent, r'**'+os.sep+'*.png'), recursive=True))
    random.shuffle(files)
    total = len(files)
    c = int(total * 0.75)
    print("total:", total, c, total-c)
    writecsv(path.join(parent, 'train.csv'), files[:c])
    writecsv(path.join(parent, 'test.csv'), files[c:])
