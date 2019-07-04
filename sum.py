import json
import glob
import os
from os import path


def listJson(parent):
    files = sorted(glob.glob(path.join(parent, r'**'+os.sep+'*.json'), recursive=True))
    return files


if __name__ == "__main__":
    from sys import stdout
    files = listJson('/home/mark/result')
    machine = {}
    OP = {}
    status = {}

    count = 0
    for file in files:
        count += 1
        stdout.write('\r %d' % count)
        stdout.flush()
        # if count > 100:
        #    break
        with open(file) as fp:
            obj = json.load(fp)
            if obj['machine'] in machine:
                machine[obj['machine']] += 1
            else:
                machine[obj['machine']] = 1

            if obj['OP'] in OP:
                OP[obj['OP']] += 1
            else:
                OP[obj['OP']] = 1

            if obj['status'] in status:
                status[obj['status']] += 1
            else:
                status[obj['status']] = 1
    config = {}
    config['machine'] = sorted(machine.keys())
    config['OP'] = sorted(OP.keys())
    config['status'] = sorted(status.keys())
    with open('config.json', 'wt') as fp:
        json.dump(config, fp)
    print("\nmachine:")
    for key, value in machine.items():
        print(key, ',', value)
    print("OP:")
    for key, value in OP.items():
        print(key, ',', value)
    print('status:')
    print(status)
