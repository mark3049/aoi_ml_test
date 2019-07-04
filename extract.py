# -*- coding: UTF-8 -*-
import os
from os import path
import logging
import cv2

from aoi_reader import listXML, read_AOI_Result

log = logging.getLogger(__name__)


def drawRect(image, info):
    x1 = info['X1']
    x2 = info['X2']
    y1 = info['Y1']
    y2 = info['Y2']

    anglestrs = ['90', '270']
    cx, cy = (x1+x2)//2, (y1+y2)//2
    w, h = (x2-x1)//2, (y2-y1)//2
    if info['Angle'] in anglestrs:
        # 因為TRI 90/270 方向不對，需要轉90度
        x1, x2 = cx-h, cx+h
        y1, y2 = cy-w, cy+w
        w, h = h, w
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
    if w < 50:
        x1, x2 = cx-25, cx + 25
    if h < 50:
        y1, y2 = cy-25, cy + 25

    cv2.rectangle(image, (x1-2, y1-2), (x2+2, y2+2), (0, 255, 0), 2)


def drawimage(parent, filename, dest):
    _, winfos = read_AOI_Result(filename)
    if len(winfos) == 0:
        return
    datecode = path.basename(filename)[:8]
    pictures = {}
    for info in winfos:
        PicPath = info['PicPath']
        dirs = PicPath.split('\\')[2:]
        picfile = path.join(parent, os.sep.join(dirs))
        if not path.isfile(picfile):
            log.error('picture not exist %s', picfile)
        if picfile in pictures:
            im = pictures[picfile]
        else:
            im = cv2.imread(picfile)
        drawRect(im, info)
        pictures[picfile] = im
    dest_dir = path.join(dest, datecode)
    if not path.exists(dest_dir):
        os.mkdir(dest_dir)
    dest_dir = path.join(dest_dir, winfos[0]['SN'])

    if not path.exists(dest_dir):
        os.mkdir(dest_dir)
    for picsrc, im in pictures.items():
        name = path.basename(picsrc)[:-4]+'.png'
        cv2.imwrite(path.join(dest_dir, name), im)


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)

    src_path = '/home/mark/test'
    dest_path = '/home/mark/result'
    files = listXML('/home/mark/test')
    count = 0
    for filename in files:
        drawimage(src_path, filename, dest_path)
        sys.stdout.write('.')
        count += 1
        if count > 80:
            sys.stdout.write('\n')
        sys.stdout.flush()
