# -*- coding: UTF-8 -*-
import os
from os import path
import logging
import cv2
from PIL import Image
import json

from aoi_reader import listXML, read_AOI_Result

log = logging.getLogger(__name__)


def genMinROI(info):
    x1 = info['X1']
    x2 = info['X2']
    y1 = info['Y1']
    y2 = info['Y2']
    cx, cy = (x1+x2)//2, (y1+y2)//2
    w, h = (x2-x1), (y2-y1)
    if w < 50:
        x1, x2 = cx-25, cx + 25
    if h < 50:
        y1, y2 = cy-25, cy + 25
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
    if not path.exists(outdir):
        os.mkdir(outdir)
    outdir = path.join(outdir, '%s_%s' % (SN, side))
    if not path.exists(outdir):
        os.mkdir(outdir)
    return outdir


def drawimage(xmlfile, dest):
    _, winfos = read_AOI_Result(xmlfile)
    if len(winfos) == 0:
        return

    outdir = mkdestDir(
        dest=dest,
        datecode=path.basename(xmlfile)[:8],
        SN=winfos[0]['SN'],
        side=winfos[0]['side'])

    pictures = {}
    for info in winfos:
        picfile = combinPath(xmlfile, info['PicPath'])
        if not path.isfile(picfile):
            log.error('picture not exist %s', picfile)
        if picfile in pictures:
            im = pictures[picfile]
        else:
            im = cv2.imread(picfile)
        drawRect(im, info)
        pictures[picfile] = im

    for picfile, im in pictures.items():
        name = path.basename(picfile)[:-4]+'.jpg'
        cv2.imwrite(path.join(outdir, name), im)


def extract(xmlfile, dest):
    _, winfos = read_AOI_Result(xmlfile)
    if len(winfos) == 0:
        return
    datecode = path.basename(xmlfile)[:8]
    SN = winfos[0]['SN']
    SIDE = winfos[0]['side']
    outdir = mkdestDir(
        dest=dest,
        datecode=datecode,
        SN=SN,
        side=SIDE
        )
    index = 0
    picDict = {}
    for info in winfos:
        picfile = combinPath(xmlfile, info['PicPath'])
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
        x1, y1, x2, y2 = genMinROI(info)
        # cv2.imshow('Main', im[y1:y2, x1:x2])
        # cv2.waitKey(0)
        img = im.crop((x1, y1, x2, y2))
        if (x2-x1) > 50 or (y2-y1) > 50:
            img = img.resize((50, 50))
        img.save(path.join(outdir, name))
        # print(path.join(outdir, name))
        name = out_name+'-%04d.json' % index
        with open(path.join(outdir, name), 'wt') as fp:
            json.dump(info, fp)


def argsParser():
    import argparse
    p = argparse.ArgumentParser(description='Extract AOI XML/MAP')
    p.add_argument('-d', '--debug', action='store_true', default=False)
    p.add_argument('src', help='AOI File Path')
    p.add_argument('dest', help='Output Path')
    return p.parse_args()


if __name__ == "__main__":
    args = argsParser()
    logging.basicConfig(level=logging.INFO if args.debug else logging.ERROR)

    files = listXML(args.src)

    total = len(files)
    print('total:', total)
    for filename in files:
        # log.info(filename)
        # drawimage(xmlfile=filename, dest=args.dest)
        extract(xmlfile=filename, dest=args.dest)
        total -= 1
        print('\r', total, end=' ', flush=True)
    print('\n succes')
