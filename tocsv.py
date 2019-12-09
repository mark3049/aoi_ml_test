# -*- coding: UTF-8 -*-
''' 匯出目錄內的JSON檔案成CSV格式檔案
'''
import logging
import glob
import os
from os import path
import csv
import json
fkeys = ['ConfirmTime', 'StationId', 'cModel', 'CycleTime']
bkeys = ['BoardSN', 'Status','TopBtm']
ckeys = ['CompName', 'PackageType', 'PartNo', 'Status', 'MachineDefect', 'ConfirmDefect']
wkeys = ['Name', 'Status', 'MachineDefect', 'ConfirmDefect' , 'Angle', 'X1', 'Y1', 'X2', 'Y2', 'WindowInfo']

def write_to_csv(info, writer):
    for _, Board in info['Board'].items():
        for _, Component in Board['Component'].items():
            false_call = Component['Status'] == 'False Call'
            for _, Window in Component['Windows'].items():
                if type(Window) != dict:
                    continue
                if not false_call and Window['Status'] == 'False Call':
                    continue
                values = []
                for key in fkeys:
                    values.append(info[key])
                for key in bkeys:
                    values.append(Board[key])
                for key in ckeys:
                    values.append(Component[key])
                for key in wkeys:
                    values.append(Window[key])
                writer.writerow(values)

    pass

if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description='AOI Test Program')
    p.add_argument('-d', '--debug', action='store_true', default=False)
    p.add_argument('src', help='AOI File Path')
    p.add_argument('dest', help="Output CSV filename", default="log.csv")
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO if args.debug else logging.ERROR)

    parent = args.src
    # parent = r'd:\20190627\7500SIII_A\XML\20190527\7500SIII_A\66201-0020-B\J423NB2001'
    files = sorted(glob.glob(path.join(parent, r'**' + os.sep + '*.json'), recursive=True))
    titles = []
    titles.extend(fkeys)
    for key in bkeys:
        titles.append(key+'(B)')
    for key in ckeys:
        titles.append(key+'(C)')
    for key in wkeys:
        titles.append(key + '(W)')
    size = len(files)
    with open(args.dest, 'wt' , newline='') as fp:
        w = csv.writer(fp)
        w.writerow(titles)
        for file in files:
            print(size, file)
            size-=1
            with open(file) as json_fp:
                panel = json.load(json_fp)
                write_to_csv(panel, w)
    pass