# -*- coding: UTF-8 -*-
import os
from os import path
import logging
import cv2
from PIL import Image
import json
import threading
import time
import queue

from aoi_reader import listXML
from aoi_reader import SFC_Reader, InspDataReader, combin

log = logging.getLogger(__name__)
lock = threading.Lock()


def genMinROI(info):
    scale = 1.25
    x1 = info['X1']
    x2 = info['X2']
    y1 = info['Y1']
    y2 = info['Y2']
    cx, cy = (x1+x2)//2, (y1+y2)//2
    w, h = int((x2-x1)*scale), int((y2-y1)*scale)
    if w < 50:
        x1, x2 = cx-25, cx + 25
    if h < 50:
        y1, y2 = cy-25, cy + 25
    if x1 < 0:
        x2 -= x1
        x1 = 0
    if y1 < 0:
        y2 -= y1
        y1 = 0
    return x1, y1, x2, y2


def drawRect(image, info):
    x1 = info['X1']
    x2 = info['X2']
    y1 = info['Y1']
    y2 = info['Y2']

    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
    x1, y1, x2, y2 = genMinROI(info)
    cv2.rectangle(image, (x1-2, y1-2), (x2+2, y2+2), (0, 255, 0), 2)


def combinPath(XMLPath, PicPath):
    # xml path = {parent}/{user define}/XML/{TRI Define}/{XML}.xml
    # PicPath = 'D:\AO\MAP\{TRI Define}\{PIC}.jpg
    # TRI Define = {Date}/{Line}/{PN}/{SN}
    basePath = os.sep.join(XMLPath.split(os.sep)[:-6])
    picture = os.sep.join(PicPath.split('\\')[2:])
    return path.join(basePath, picture)


def mkdestDir(dest, datecode, SN, side):
    outdir = path.join(dest, datecode)
    lock.acquire()
    if not path.exists(outdir):
        try:
            os.mkdir(outdir)
        except IOError:
            pass
    outdir = path.join(outdir, '%s_%s' % (SN, side))
    if not path.exists(outdir):
        try:
            os.mkdir(outdir)
        except IOError:
            pass
    lock.release()
    return outdir


class JobQueue:
    def __init__(self):
        self.queue = queue.Queue()
        self.lock = threading.Lock()

    def get(self):
        try:
            self.lock.acquire()
            if self.queue.qsize():
                return self.queue.get()
        finally:
            self.lock.release()

    def size(self):
        return self.queue.qsize()

    def put(self, value):
        try:
            self.lock.acquire()
            self.queue.put(value)
        finally:
            self.lock.release()


class extract_thread(threading.Thread):
    def __init__(self, dest, queue, name=None):
        threading.Thread.__init__(self)
        self.dest = dest
        self.queue = queue
        self.terminate = False
        self._loop = True
        self.insp_reader = InspDataReader()
        self.sfc_reader = SFC_Reader()
        if name:
            self.setName(name)
        self.start()

    def read_xml(self, filename):
        sfc = self.sfc_reader.read(filename)
        insp = self.insp_reader.read(filename)
        if sfc is None or insp is None:
            return None
        combin(sfc=sfc, insp=insp)
        return sfc

    def run(self):
        while self._loop:
            xmlfile = self.queue.get()
            if xmlfile is None:
                break
            self.extract(xmlfile, self.dest)
        log.info('thread %s terminate', self._name)
        self.terminate = True

    def forceExit(self):
        self._loop = False

    def extract(self, xmlfile, dest):
        info = self.read_xml(xmlfile)
        if info is None:
            return
        datecode = path.basename(xmlfile)[:8]
        SN = path.basename(xmlfile)[15:-4]
        SIDE = info['TB']
        outdir = mkdestDir(
            dest=dest,
            datecode=datecode,
            SN=SN,
            side=SIDE
            )
        index = 0
        picDict = {}
        for bkey, Board in info['Board'].items():
            for ckey, Component in Board['Component'].items():
                false_call = Component['Status'] == 'False Call'
                for wkey, Window in Component['Windows'].items():
                    if type(Window) != dict:
                        continue
                    if not false_call and Window['Status'] == 'False Call':
                        continue

                    picfile = combinPath(xmlfile, Window['PicPath'])
                    if not path.isfile(picfile):
                        log.warning("picfile not exists %s", picfile)
                    if picfile in picDict:
                        im = picDict[picfile]
                    else:
                        try:
                            im = Image.open(picfile)
                            picDict[picfile] = im
                        except IOError as ex:
                            log.warning("except %s", str(ex))
                            continue
                    index += 1
                    out_name = '%s_%s_%s_%s' % (datecode, SN, SIDE, path.basename(picfile)[:-4])
                    name = out_name+'-%04d.png' % index
                    x1, y1, x2, y2 = genMinROI(Window)
                    # cv2.imshow('Main', im[y1:y2, x1:x2])
                    # cv2.waitKey(0)
                    width, height = im.size
                    if x1 < 0:
                        x1 = 0
                    if y1 < 0:
                        y1 = 0
                    if x2 >= width:
                        x2 = width-1
                    if y2 >= height:
                        y2 = height-1
                    img = im.crop((x1, y1, x2, y2))

                    img = img.resize((50, 50))
                    img.save(path.join(outdir, name))
                    # print(path.join(outdir, name))
                    name = out_name+'-%04d.json' % index
                    with open(path.join(outdir, name), 'wt') as fp:
                        json.dump(Window, fp)
        if index == 0:
            pass
            # print(xmlfile)


def argsParser():
    import argparse
    p = argparse.ArgumentParser(description='Extract AOI XML/MAP')
    p.add_argument('-d', '--debug', action='store_true', default=False)
    p.add_argument('-t', '--thread', type=int, default=5, help='work thread count')
    p.add_argument('src', help='AOI File Path')
    p.add_argument('dest', help='Output Path')
    return p.parse_args()


if __name__ == "__main__":
    args = argsParser()
    logging.basicConfig(level=logging.INFO if args.debug else logging.ERROR)

    jobs = JobQueue()
    files = listXML(args.src)

    total = len(files)
    print('total:', total)
    for filename in files:
        jobs.put(filename)

    threads = [extract_thread(dest=args.dest, queue=jobs, name="thread %02d" % index) for index in range(args.thread)]
    try:
        while True:
            print('\r', jobs.size(), end=' ', flush=True)
            time.sleep(1)
            t = [x for x in threads if x.terminate is True]
            if len(t) == len(threads):
                log.info("all thread finish")
                break
    except KeyboardInterrupt:
        [x.forceExit for x in threads]
        time.sleep(3)
    [x.join() for x in threads]
    print('\n succes')
