import random
import os
from os import path
import glob
import json
import csv

config_json_file = 'dataset/config.json'


def read_json(filename):
    with open(filename) as f:
        return json.load(f)


def writecsv(dest, files):
    config = read_json(config_json_file)
    dest_falsecall = dest+'_falsecall.csv'
    dest_defect = dest+'_defect.csv'
    falsecall_fp = open(dest_falsecall, 'wt')
    defect_fp = open(dest_defect, 'wt')
    defect = csv.writer(defect_fp)
    falsecall = csv.writer(falsecall_fp)
    print('\n', dest_falsecall, dest_defect)
    total = len(files)
    print(total)
    for file in files:
        json_file = file[:-3]+'json'
        obj = read_json(json_file)
        x1 = config['MachineDefect'].index(obj['MachineDefect'])
        x2 = config['ConfirmDefect'].index(obj['ConfirmDefect'])
        if x2 != 0:
            x2 = 1
        x3 = config['Status'].index(obj['Status'])
        if x3 != 0:
            x3 = 1
        x4 = config['AlgorithmDefect'].index(obj['AlgorithmDefect'])

        if x2 == 0:
            falsecall.writerow([file, x1, x2, x3, x4])
        else:
            defect.writerow([file, x1, x2, x3, x4])
        total -= 1
        print('\r', total, end=' ', flush=True)
    falsecall_fp.close()
    defect_fp.close()


def mkconfig(files):
    config = {"MachineDefect": {}, "ConfirmDefect": {}, "Status": {}, "AlgorithmDefect": {}}
    size = len(files)
    for file in files:
        json_file = file[:-3]+'json'
        obj = read_json(json_file)
        for key in config.keys():
            value = obj[key]
            if value in config[key]:
                config[key][value] += 1
            else:
                config[key][value] = 1
        size -= 1
        print('\r', size, end=' ', flush=True)
    print('\n')

    with open('report.json', 'wt') as f:
        json.dump(config, f, indent=True)

    t = {}
    for key in config.keys():
        t[key] = sorted(config[key].keys())

    with open(config_json_file, 'wt') as f:
        json.dump(t, f, indent=True)


if __name__ == "__main__":
    parent = '/home/mark/result'
    files = sorted(glob.glob(path.join(parent, r'**'+os.sep+'*.png'), recursive=True))
    mkconfig(files)
    writecsv(path.join(parent, 'all'), files)
