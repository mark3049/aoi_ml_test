import json
import logging
import os
from os import path
import glob
import cv2


log = logging.getLogger(__name__)
max_file_count = 30


def is_over_file_limit(parent):
    '''檢查檔案數量是否超過需求

    當max_file_count<= 0時不受限制
    '''
    global max_file_count

    if max_file_count <= 0:
        return False
    files = glob.glob(path.join(parent, '*.json'))
    if len(files) > max_file_count:
        return True
    else:
        return False



def drawROI(image, winInfo):
    x1 = winInfo['X1']
    x2 = winInfo['X2']
    y1 = winInfo['Y1']
    y2 = winInfo['Y2']
    cv2.rectangle(image, (x1-2, y1-2), (x2+2, y2+2), (0, 0, 255), 2)


def out_image(src, out_dir, winInfo, basename):
    out_img = path.join(out_dir, basename + '_orig.jpg')
    if not path.exists(out_img):
        os.link(src, out_img)
    image = cv2.imread(src)
    drawROI(image, winInfo)
    out_img = path.join(out_dir, basename + '_box.jpg')
    cv2.imwrite(out_img, image)
    log.info('out image %s', path.join(out_dir, basename))


def write_to_folder(info, dest):

    for _, Board in info['Board'].items():
        for _, Component in Board['Component'].items():
            for _, Window in Component['Windows'].items():
                if type(Window) != dict:
                    continue
            if 'SOLDER JOINT' != Window['MachineDefect']:
                continue
            PackageType = Component['PackageType'].strip()
            if len(PackageType) == 0:
                PackageType = 'empty'
            out_dir = path.join(dest, PackageType)
            if not path.exists(out_dir):
                os.mkdir(out_dir)
            out_dir = path.join(out_dir, Component['Status'])
            if not path.exists(out_dir):
                os.mkdir(out_dir)

            if is_over_file_limit(out_dir):
                continue
            filename = '{sn}-{name}'.format(
                sn=Board['BoardSN'],
                name=Window['Name']
                )
            src_img = Window['PicPath']
            if not path.exists(src_img):
                log.info("PicPath is not exist %s", src_img)
                continue
            out_json = path.join(out_dir, filename + '.json')
            d = {}
            d['S/N'] = Board['BoardSN']
            d['CompName'] = Component['CompName']
            d['DefectName'] = Window['Name']
            d['MachineDefect'] = Window['MachineDefect']
            d['Manual Inspect Result'] = Window['ConfirmDefect']
            # d['X1'] = Window['X1']
            # d['X2'] = Window['X2']
            # d['Y1'] = Window['Y1']
            # d['Y2'] = Window['Y2']
            try:
                with open(out_json, 'wt') as fp:
                    json.dump(d, fp, indent=True, sort_keys=True)
                out_image(src_img, out_dir, Window, filename)
            except OSError as e:
                log.error(str(e))


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description='AOI Test Program')
    p.add_argument('-d', '--debug', action='store_true', default=False)
    p.add_argument('--dest', help="Output Image folder", default="output")
    p.add_argument('-m', '--max', type=int,
                   default=max_file_count,
                   help="限制最多檔案數量")
    p.add_argument('src', help='AOI File Path with json')
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO if args.debug else logging.ERROR)
    max_file_count = args.max
    parent = args.src
    # parent = r'd:\20190627\7500SIII_A\XML\20190527\7500SIII_A\66201-0020-B\J423NB2001'

    if not path.exists(args.dest):
        os.mkdir(args.dest)

    files = sorted(glob.glob(path.join(parent, r'**' + os.sep + '*.json'), recursive=True))
    for file in files:
        with open(file) as fp:
            info = json.load(fp)
            write_to_folder(info, args.dest)

    pass
