import os
import random
import csv
import argparse


def writefile(name, values):
    print(name, len(values))
    with open(name, 'wt') as fp:
        w = csv.writer(fp)
        w.writerows(values)


def do_split(parent, label, args):
    src = os.path.join(parent, 'all_'+label+'.csv')
    dest_train = os.path.join(parent, 'train_'+label+'.csv')
    dest_test = os.path.join(parent, 'test_'+label+'.csv')
    dest_verify = os.path.join(parent, 'verify_'+label+'.csv')
    values = []

    with open(src) as src_fp:
        for row in csv.reader(src_fp):
            values.append(row)
    print('total:', len(values))
    random.shuffle(values)
    size = len(values)

    index = int(size*args.train)
    writefile(dest_train, values[:index])
    values = values[index:]

    index = int(size*args.test)
    writefile(dest_test, values[:index])
    values = values[index:]

    if args.verify is None:
        writefile(dest_verify, values)
    else:
        index = int(size*args.verify)
        writefile(dest_verify, values[:index])


def argsParser():
    p = argparse.ArgumentParser(description='Split AOI csv')
    p.add_argument('-d', '--debug', action='store_true', default=False)
    p.add_argument('-t', '--test', default=0.1, type=float, help='test scale')
    p.add_argument('-m', '--train', default=0.7, type=float, help='train scale')
    p.add_argument('-v', '--verify', default=None, type=float, help='verify scale')
    return p.parse_args()


if __name__ == "__main__":
    args = argsParser()
    parent = '/home/mark/result'
    do_split(parent, 'falsecall', args)
    do_split(parent, 'defect', args)
