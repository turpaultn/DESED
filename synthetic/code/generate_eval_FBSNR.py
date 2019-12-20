# -*- coding: utf-8 -*-
#########################################################################
# Initial software
# Copyright Nicolas Turpault, Romain Serizel, Justin Salamon, Ankit Parag Shah, 2019, v1.0
# This software is distributed under the terms of the License MIT
#########################################################################
import logging
import time
import argparse
import os.path as osp
from pprint import pformat

import generate_training
from desed.generate_synthetic import generate_new_bg_snr_files
from desed.utils import create_folder, rm_high_polyphony, post_processing_annotations
from desed.Logger import create_logger

import config as cfg


if __name__ == '__main__':
    LOG = create_logger(__name__, "Desed.log", terminal_level=logging.INFO)
    LOG.info(__file__)
    t = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--outfolder', type=str, default=osp.join(cfg.audio_path_eval, 'soundscapes_generated_fbsnr'))
    parser.add_argument('--outcsv', type=str,
                        default=osp.join(cfg.meta_path_eval, "soundscapes_generated_fbsnr", "XdB.csv"))
    parser.add_argument('--number', type=int, default=1000)
    parser.add_argument('--fgfolder', type=str, default=osp.join(cfg.audio_path_eval, "soundbank", "foreground"))
    parser.add_argument('--bgfolder', type=str, default=osp.join(cfg.audio_path_eval, "soundbank", "background"))
    args = parser.parse_args()
    pformat(vars(args))

    # General output folder, in args
    out_folder = args.outfolder
    create_folder(out_folder)

    # SCAPER SETTINGS
    fg_dir = args.fgfolder
    bg_dir = args.bgfolder
    # JSON file
    param_json = osp.join("event_occurences", 'event_occurences_eval.json')

    # Default parameters
    n_soundscapes = args.number
    db_ref = -50
    clip_duration = 10.0

    # ########
    # FBSNR
    # #######
    # Generate events same way as the training set
    out_folder_30 = osp.join(out_folder, "30dB")
    create_folder(out_folder_30)

    generate_training.generate_files(param_json, n_soundscapes,
                                     ref_db=db_ref,
                                     duration=clip_duration,
                                     fg_folder=fg_dir,
                                     bg_folder=bg_dir,
                                     out_folder=out_folder_30)

    rm_high_polyphony(out_folder_30, 3)
    post_processing_annotations(out_folder_30, output_folder=out_folder_30, output_csv=args.outcsv)

    # We create the same dataset with different background SNR
    # Be careful, 6 means the background SNR is 6,
    # so the foreground background snr ratio is between 0dB and 24dB (see utils snr_min (6dB) and snr_max (30dB))
    out_folder_24 = osp.join(out_folder, "24dB")
    create_folder(out_folder_24)
    generate_new_bg_snr_files(6, out_folder_30, out_folder_24)

    # Same for 15
    out_folder_15 = osp.join(out_folder, "15dB")
    create_folder(out_folder_15)
    generate_new_bg_snr_files(15, out_folder_30, out_folder_15)

    out_folder_0 = osp.join(out_folder, "0dB")
    create_folder(out_folder_0)
    generate_new_bg_snr_files(30, out_folder_30, out_folder_0)
