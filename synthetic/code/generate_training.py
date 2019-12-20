# -*- coding: utf-8 -*-
#########################################################################
# Initial software
# Copyright Nicolas Turpault, Romain Serizel, Justin Salamon, Ankit Parag Shah, 2019, v1.0
# This software is distributed under the terms of the License MIT
#########################################################################
import time
import argparse
import os.path as osp
import json
from pprint import pformat
import logging

from desed.generate_synthetic import generate_single_file
from desed.utils import create_folder, rm_high_polyphony, post_processing_annotations
from desed.Logger import create_logger
import config as cfg


def generate_files(param_file, number, ref_db, duration, fg_folder, bg_folder, out_folder, min_events=0):
    log = create_logger(__name__)
    n = 0
    with open(param_file) as json_file:
        params = json.load(json_file)
    for class_lbl in params.keys():
        log.debug('Generating soundscape: {:d}/{:d}'.format(n + 1, number))
        class_params = params[class_lbl]
        for i in range(int(number * class_params['prob'])):
            generate_single_file(class_params=class_params,
                                 class_lbl=class_lbl,
                                 ref_db=ref_db,
                                 duration=duration,
                                 fg_folder=fg_folder,
                                 bg_folder=bg_folder,
                                 outfolder=out_folder,
                                 filename=n,
                                 min_events=min_events)

            n += 1

            
if __name__ == "__main__":
    LOG = create_logger("DESED", "Desed.log", terminal_level=logging.INFO, file_level=logging.INFO)
    LOG.info(__file__)
    t = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("--outfolder", type=str, default=osp.join(cfg.audio_path_train, "soundscapes_generated"))
    parser.add_argument("--outcsv", type=str, default=osp.join(cfg.meta_path_train, "synthetic_generated.csv"))
    parser.add_argument("--fgfolder", type=str, default=osp.join(cfg.audio_path_train, "soundbank", "foreground"))
    parser.add_argument("--bgfolder", type=str, default=osp.join(cfg.audio_path_train, "soundbank", "background"))
    parser.add_argument("--number", type=int, default=1000)
    args = parser.parse_args()
    pformat(vars(args))

    # Output folder, in args
    outfolder = args.outfolder
    create_folder(outfolder)
    out_csv = args.outcsv

    # SCAPER SETTINGS
    fg_dir = args.fgfolder
    bg_dir = args.bgfolder
    # JSON file
    param_json = osp.join("event_occurences", "event_occurences_train.json")

    # Default parameters
    n_soundscapes = args.number
    db_ref = -50
    clip_duration = 10.0

    generate_files(param_json, n_soundscapes,
                   ref_db=db_ref,
                   duration=clip_duration,
                   fg_folder=fg_dir,
                   bg_folder=bg_dir,
                   out_folder=outfolder)

    rm_high_polyphony(outfolder, 3)
    post_processing_annotations(outfolder, output_folder=outfolder, output_csv=out_csv)
    LOG.info(f"time of the program: {time.time() - t}")
