import os
import random
import csv


def do_split(parent, label):
    src = os.path.join(parent, 'all_'+label+'.csv')
    dest_train = os.path.join(parent, 'train_'+label+'.csv')
    dest_test = os.path.join(parent, 'test_'+label+'.csv')
    with open(src) as src_fp:
        with open(dest_train, 'wt') as train_fp:
            with open(dest_test, 'wt') as test_fp:
                train_w = csv.writer(train_fp)
                test_w = csv.writer(test_fp)

                for row in csv.reader(src_fp):
                    if random.randint(0, 99) < 25:
                        test_w.writerow(row)
                    else:
                        train_w.writerow(row)


if __name__ == "__main__":
    parent = '/home/mark/result'
    do_split(parent, 'falsecall')
    do_split(parent, 'defect')
