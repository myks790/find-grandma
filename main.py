import argparse
from guard import watch
from snapshot_downloader import snapshot_down
# from phone_watcher import watch_phone

argparser = argparse.ArgumentParser(
    description='test yolov3 network with coco weights')

argparser.add_argument(
    '-w',
    '--weights',
    help='path to weights file',
    default='yolov3.weights')

argparser.add_argument(
    '-i',
    '--image',
    help='path to image file')

argparser.add_argument(
    '-p',
    '--path',
    help='path to base path',
    default='D:/temp/ch-gm')


def _main_(args):
    base_path = args.path
    weights_path = args.weights

    # watch_phone()
    snapshot_down(base_path)
    while True:
        print('start=============')
        watch(base_path, weights_path)
        print('end=============')


if __name__ == '__main__':
    args = argparser.parse_args()
    _main_(args)
