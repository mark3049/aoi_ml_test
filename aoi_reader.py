# -*- coding: UTF-8 -*-
import logging
# import xml.etree.cElementTree as ET
import xml.etree.ElementTree as ET
from lxml import etree
from os import path
# import csv
import argparse
import glob
import os
import json


log = logging.getLogger(__name__)


def hotfix(info):
    # 因為TRI 90/270 方向不對，需要轉90度
    _anglestrs = ['90', '270']
    if info['Angle'] not in _anglestrs:
        return

    x1 = info['X1']
    x2 = info['X2']
    y1 = info['Y1']
    y2 = info['Y2']

    cx, cy = (x1+x2)//2, (y1+y2)//2
    w, h = (x2-x1)//2, (y2-y1)//2

    info['X1'], info['X2'] = cx-h, cx+h
    info['Y1'], info['Y2'] = cy-w, cy+w


class InspDataReader:

    def __init__(self):
        self.parser = etree.XMLParser(recover=True)

    def read(self, filename):
        path = os.path.dirname(filename)
        basename = os.path.basename(filename)

        filename = os.path.join(path, basename[:15]+'7500SIII_B.xml')
        if os.path.isfile(os.path.join(path, filename)):
            self._filename = os.path.join(path, filename)
        else:
            filename = os.path.join(path, basename[:15]+'7500SIII_A.xml')
            if os.path.isfile(os.path.join(path, filename)):
                self._filename = os.path.join(path, filename)
            else:
                return None

        f = etree.parse(self._filename, parser=self.parser)
        root = f.getroot()
        if root.tag != 'InspData':
            log.warning("Root tag %s != InspData %s", root.tag, filename)
            return None
        panel = {}
        for Panel in root:
            if Panel.tag != 'Panel':
                continue
            panel = dict(Panel.attrib)
            panel['Board'] = {}
            for Board in Panel:
                if Board.tag != 'Board':
                    continue
                name, value = self._BoardParser(Board)
                if name is None:
                    continue
                panel['Board'][name] = value
        return panel

    def _BoardParser(self, Board):
        if Board.tag != 'Board':
            return None, None
        board = dict(Board.attrib)
        board['Component'] = {}
        for child in Board:
            if child.tag == 'Component':
                name, value = self._ComponentParser(child)
                if name is None:
                    continue
                board['Component'][name] = value
        return Board.attrib['NO'], board

    def _ComponentParser(self, Component):
        com = dict(Component.attrib)
        # if com[key] == 'PASS':
        #    return None, None
        for e in Component:
            if e.tag != 'Windows':
                continue
            value = self._Windows(e)
            if value is None:
                return None, None
            com['Windows'] = value
        return Component.attrib['Name'], com

    def _Windows(self, Windows):
        wins = {}
        for w in Windows:
            if w.tag == 'Window':
                name, value = self._Window(w)
                wins[name] = value
        if len(wins) == 0:
            return None
        return wins

    def _Window(self, Window):
        win = dict(Window.attrib)  # self.attribs(Window, ['WinDefect', 'AlgorithmDefect', 'Algorithm', 'key', 'WindowInfo'])
        return Window.attrib['Name'], win


class SFC_Reader:
    def read(self, filename):
        self._filename = path.basename(filename)
        tree = ET.ElementTree(file=filename)
        root = tree.getroot()
        if root.tag != 'Panel':
            log.warning("Root tag %s != Panel %s", root.tag, filename)
            return None
        panel = dict(root.attrib)
        panel['Board'] = {}
        for Board in root:
            name, value = self._boardParser(Board)
            if name is None:
                continue
            panel['Board'][name] = value
        return panel

    def _boardParser(self, Board):
        if Board.tag != 'Board':
            log.warning("%s %s", str(Board), self._filename)
            return None, None
        board = dict(Board.attrib)
        # board['SN'] = Board.attrib['BoardSN']
        board['Component'] = {}
        for Component in Board:
            name, value = self._componentParser(Component)
            if name is None:
                continue
            board['Component'][name] = value
        return Board.attrib['imulti'], board

    def _componentParser(self, Component):
        if Component.tag != 'Component':
            log.warning("%s %s", str(Component), self._filename)
            return None, None
        cinfo = dict(Component.attrib)
        cinfo['Windows'] = {}
        for win in Component:
            name, value = self._winParser(win)
            if name is None:
                continue
            cinfo['Windows'][name] = value
        return Component.attrib['CompName'], cinfo

    def _winParser(self, win):
        if win.tag != 'Window':
            return None, None
        info = dict(win.attrib)
        info['X1'] = int(win.attrib['X1'])
        info['Y1'] = int(win.attrib['Y1'])
        info['X2'] = int(win.attrib['X2'])
        info['Y2'] = int(win.attrib['Y2'])
        hotfix(info)
        return win.attrib['Name'], info


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


def combin_element(left, right):
    for key in right.keys():
        if type(right[key]) is dict:
            continue
        if key in left:
            v1 = left[key].strip()
            v2 = right[key].strip()
            if v1 != v2:
                log.warning("%s != %s", v1, v2)
        else:
            left[key] = right[key]


def combin(sfc, insp):
    combin_element(sfc, insp)
    for key in sfc.keys():
        if type(sfc[key]) == dict:
            if key in insp:
                combin(sfc[key], insp[key])
            else:
                log.error("key %s not exist ", key)
    return sfc


def combinPath(XMLPath, PicPath):
    # xml path = {parent}/{user define}/XML/{TRI Define}/{XML}.xml
    # PicPath = 'D:\AO\MAP\{TRI Define}\{PIC}.jpg
    # TRI Define = {Date}/{Line}/{PN}/{SN}
    basePath = os.sep.join(XMLPath.split(os.sep)[:-6])
    picture = os.sep.join(PicPath.split('\\')[2:])
    return path.join(basePath, picture)


def changePicPath(context, XMLPath):
    for bkey, Board in context['Board'].items():
        for ckey, Component in Board['Component'].items():
            for wkey, Window in Component['Windows'].items():
                PicPath = combinPath(XMLPath, Window['PicPath'])
                if not os.path.isfile(PicPath):
                    log.error("%s is not exist", PicPath)
                Window['PicPath'] = PicPath


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
    total = len(files)
    insp_reader = InspDataReader()
    sfc_reader = SFC_Reader()
    for file in files:
        dest = file[:-4]+".json"
        if path.exists(dest):
            continue
        print(total, file)
        insp = insp_reader.read(file)
        sfc = sfc_reader.read(file)
        if insp is None:
            log.error("%s can't read", file)
            continue
        combin(insp=insp, sfc=sfc)
        changePicPath(sfc, file)
        total -= 1
        with open(dest, 'wt') as f:
            json.dump(sfc, f, indent=True, sort_keys=True)
