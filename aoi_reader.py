# -*- coding: UTF-8 -*-
import logging
import xml.etree.cElementTree as ET
from os import path
# import csv
import argparse
import glob
import os


log = logging.getLogger(__name__)


def read_AOI_Result(filename):
    tree = ET.ElementTree(file=filename)
    root = tree.getroot()
    if root.tag != 'Panel':
        log.warning(root.tag, "!=Panel", filename)
        return [], []
    win_infos = []
    c_infos = []
    for Board in root:
        if Board.tag != 'Board':
            log.warning("%s %s", str(Board), path.basename(filename))
            continue
        sn = Board.attrib['BoardSN']
        topbtm, = Board.attrib['TopBtm']
        for Component in Board:
            if Component.tag != 'Component':
                log.warning("%s %s", str(Component), path.basename(filename))
                continue
            cinfo = {}
            cinfo['SN'] = sn
            cinfo['machine'] = Component.attrib['MachineDefect']
            cinfo['OP'] = Component.attrib['ConfirmDefect']
            cinfo['status'] = Component.attrib['Status']
            cinfo['name'] = Component.attrib['CompName']
            c_infos.append(cinfo)
            for win in Component:
                if win.tag != 'Window':
                    continue
                info = {}
                info['machine'] = win.attrib['MachineDefect']
                info['OP'] = win.attrib['ConfirmDefect']
                info['status'] = win.attrib['Status']
                info['name'] = win.attrib['Name']
                info['SN'] = sn
                info['side'] = topbtm
                info['file'] = path.basename(filename)
                info['Angle'] = win.attrib['Angle']
                info['X1'] = int(win.attrib['X1'])
                info['Y1'] = int(win.attrib['Y1'])
                info['X2'] = int(win.attrib['X2'])
                info['Y2'] = int(win.attrib['Y2'])
                info['PicPath'] = win.attrib['PicPath']
                info['WindowInfo'] = win.attrib['WindowInfo']
                info['width'] = int(win.attrib['X2'])-int(win.attrib['X1'])
                info['height'] = int(win.attrib['Y2'])-int(win.attrib['Y1'])
                win_infos.append(info)
    return c_infos, win_infos


def listXML(parent):

    files = sorted(glob.glob(path.join(parent, r'**'+os.sep+'*.xml'), recursive=True))
    filematch = {}
    for file in files:
        if file.endswith("7500SIII_B.xml") or file.endswith("7500SIII_A.xml"):
            continue
        # 每一個序號僅抓最新的XML
        dirname = path.dirname(file)
        filename = path.basename(file)
        if dirname in filematch:
            # log.warning('%s -> %s ', filename, filematch[dirname])
            pass
        filematch[dirname] = filename  # remove duplice file.
    # print(len(files))
    files = []
    for dirname, filename in filematch.items():
        files.append(path.join(dirname, filename))
    return files


def argsParser():
    p = argparse.ArgumentParser(description='AOI Test Program')
    p.add_argument('-d', '--debug', action='store_true', default=False)
    # p.add_argument('-s', '--skip', action='store_true', default=False)
    # p.add_argument('-c', '--csv', action='store_true', default=False)
    # p.add_argument('-w', '--wininfo', action='store_true', default=False)
    p.add_argument('src', help='AOI File Path')
    return p.parse_args()


if __name__ == '__main__':
    args = argsParser()
    logging.basicConfig(level=logging.INFO if args.debug else logging.ERROR)
    log.info(args)
    files = listXML(args.src)
    print(len(files))
    cinfo, winfo = read_AOI_Result(files[0])
    print(cinfo)
    print(winfo)
