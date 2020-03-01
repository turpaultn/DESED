# -*- coding: utf-8 -*-
import functools
import glob
import json
import logging
import time
import argparse
import os.path as osp
from pprint import pformat

from desed.generate_synthetic import SoundscapesGenerator
from desed.logger import create_logger
from desed.post_process import rm_high_polyphony, post_process_txt_labels
from desed.utils import create_folder

import config as cfg


if __name__ == '__main__':
    LOG = create_logger(__name__, terminal_level=logging.INFO)
    LOG.info(__file__)
    t = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_folder', type=str, default=osp.join(cfg.audio_path_train, 'soundscapes_generated_ss'),
                        help="")
    parser.add_argument('--out_tsv', type=str,
                        default=osp.join(cfg.meta_path_train, "soundscapes_generated_ss", "XdB.tsv"))
    parser.add_argument('--number', type=int, default=1000)
    parser.add_argument('--fg_folder', type=str, default=osp.join(cfg.audio_path_train, "soundbank", "foreground"))
    parser.add_argument('--bg_folder', type=str, default=osp.join(cfg.audio_path_train, "soundbank", "background"))
    parser.add_argument('--json_params', type=str, default=osp.join("event_occurences", 'event_occurences_train.json'))
    args = parser.parse_args()
    pformat(vars(args))

    # General output folder, in args
    out_folder = args.out_folder
    create_folder(out_folder)
    create_folder(osp.dirname(args.out_tsv))

    # Default parameters
    clip_duration = 10.0

    sg = SoundscapesGenerator(duration=clip_duration,
                              fg_folder=args.fg_folder,
                              bg_folder=args.bg_folder,
                              ref_db=cfg.ref_db,
                              samplerate=cfg.samplerate)

    # Generate events same way as the training set
    out_folder_30 = osp.join(out_folder, "30dB")
    create_folder(out_folder_30)
    param_json = args.json_params
    with open(param_json) as json_file:
        co_occur_dict = json.load(json_file)
    sg.generate_by_label_occurence(label_occurences=co_occur_dict,
                                   number=args.number,
                                   out_folder=out_folder_30,
                                   save_isolated_events=True)

    # Remove files that have polyphony greater than 3
    rm_high_polyphony(out_folder_30, 3)
    # Combine labels of same events appending at the same time or less than 150ms interval
    post_process_txt_labels(out_folder_30, output_folder=out_folder_30, output_tsv=args.out_tsv)
