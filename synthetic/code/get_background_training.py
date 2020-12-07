# -*- coding: utf-8 -*-
import time
import argparse
import logging

from pprint import pformat

from desed.download_soundbank import get_backgrounds_train
from desed.logger import create_logger

if __name__ == '__main__':
    LOG = create_logger("DESED", terminal_level=logging.INFO)
    t = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--basedir', type=str, default="..",
                        help="the base folder of the dataset (will create subset automatically)")
    parser.add_argument('--no_SINS', action="store_true", default=False,
                        help="If specified, avoid the download of SINS subset")
    parser.add_argument('--keep-sins', action="store_true", default=False,
                        help="if set to True, keep the entire subset of SINS (not just class 'other')")
    parser.add_argument('--TUT', action="store_true", default=False,
                        help="If specified, download TUT background set in addition to SINS")
    args = parser.parse_args()
    pformat(vars(args))

    get_backgrounds_train(args.basedir, not args.no_SINS, args.TUT, args.keep_sins)

    LOG.info(f"time of the program: {time.time() - t}")
