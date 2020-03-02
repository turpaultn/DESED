# -*- coding: utf-8 -*-
import time
import argparse
import os.path as osp
import glob
from pprint import pformat
import logging

from desed.generate_synthetic import generate_files_from_jams, generate_tsv_from_jams
from desed.logger import create_logger


if __name__ == '__main__':
    LOG = create_logger("DESED", terminal_level=logging.INFO)
    LOG.info(__file__)
    t = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--jams_folder', type=str)
    parser.add_argument('--soundbank', type=str)
    parser.add_argument('--out_audio_dir', type=str)
    parser.add_argument('--out_tsv', type=str, default=None)
    parser.add_argument('--save_jams', action="store_true", default=False)
    parser.add_argument('--save_isolated', action="store_true", default=False)
    args = parser.parse_args()
    pformat(vars(args))

    # ########
    # Training
    # ########
    jams_folder = args.jams_folder
    out_audio_dir = args.out_audio_dir
    soundbank_dir = args.soundbank
    if args.save_jams:
        out_folder_jams = out_audio_dir
    else:
        out_folder_jams = None
    out_tsv = args.out_tsv
    save_isolated = args.save_isolated
    if save_isolated:
        isolated_events_path = out_audio_dir
    else:
        isolated_events_path = None

    list_jams = glob.glob(osp.join(jams_folder, "*.jams"))
    fg_path_train = osp.join(soundbank_dir, "foreground")
    bg_path_train = osp.join(soundbank_dir, "background")
    generate_files_from_jams(list_jams, out_audio_dir, out_folder_jams=out_folder_jams,
                             fg_path=fg_path_train, bg_path=bg_path_train, save_isolated_events=save_isolated,
                             isolated_events_path=isolated_events_path)
    if out_tsv:
        generate_tsv_from_jams(list_jams, out_tsv)
