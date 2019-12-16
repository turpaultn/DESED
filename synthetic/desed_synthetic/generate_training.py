# -*- coding: utf-8 -*-
#########################################################################
# Initial software
# Copyright Nicolas Turpault, Romain Serizel, Justin Salamon, Ankit Parag Shah, 2019, v1.0
# This software is distributed under the terms of the License MIT
#########################################################################
import time
import argparse
import scaper
import numpy as np
import os.path as osp
import json
from pprint import pformat

from utils import choose_class, add_event, create_folder, rm_high_polyphony, post_processing_annotations
from Logger import LOG


def generate_single_file(class_params, class_lbl, ref_db, duration, fg_folder, bg_folder, outfolder, filename,
                         min_events=0):
    # create a scaper
    sc = scaper.Scaper(duration, fg_folder, bg_folder)
    sc.protected_labels = []
    sc.ref_db = ref_db

    # add background
    sc.add_background(label=('choose', []),
                      source_file=('choose', []),
                      source_time=('const', 0))

    # add main event
    sc = add_event(sc, class_lbl, duration, fg_folder)

    # add random number of foreground events
    n_events = np.random.randint(min_events, class_params['event_max'])
    for _ in range(n_events):
        chosen_class = choose_class(class_params)
        sc = add_event(sc, chosen_class, duration, fg_folder)

    # generate
    audiofile = osp.join(outfolder, f"{filename}.wav")
    jamsfile = osp.join(outfolder, f"{filename}.jams")
    txtfile = osp.join(outfolder, f"{filename}.txt")

    sc.generate(audiofile, jamsfile,
                allow_repeated_label=True,
                allow_repeated_source=True,
                reverb=0.1,
                disable_sox_warnings=True,
                no_audio=False,
                txt_path=txtfile)


def generate_files(param_file, number, ref_db, duration, fg_folder, bg_folder, outfolder, min_events=0):
    n = 0
    with open(param_file) as json_file:
        params = json.load(json_file)
    for class_lbl in params.keys():
        LOG.debug('Generating soundscape: {:d}/{:d}'.format(n + 1, n_soundscapes))
        class_params = params[class_lbl]
        for i in range(int(number * class_params['prob'])):
            generate_single_file(class_params=class_params,
                                 class_lbl=class_lbl,
                                 ref_db=ref_db,
                                 duration=duration,
                                 fg_folder=fg_folder,
                                 bg_folder=bg_folder,
                                 outfolder=outfolder,
                                 filename=n,
                                 min_events=min_events)

            n += 1

            
if __name__ == "__main__":
    LOG.info(__file__)
    t = time.time()
    absolute_dir_path = osp.abspath(osp.dirname(__file__))
    base_path_train = osp.join(absolute_dir_path, '..', 'audio', 'train')
    parser = argparse.ArgumentParser()
    parser.add_argument("--outfolder", type=str, default=osp.join(base_path_train, "soundscapes_generated"))
    parser.add_argument("--outcsv", type=str, default=osp.join(base_path_train, "synthetic_generated.csv"))
    parser.add_argument("--fgfolder", type=str, default=osp.join(base_path_train, "soundbank", "foreground"))
    parser.add_argument("--bgfolder", type=str, default=osp.join(base_path_train, "soundbank", "background"))
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
                   outfolder=outfolder)

    rm_high_polyphony(outfolder, 3)
    post_processing_annotations(outfolder, output_folder=outfolder, output_csv=out_csv)
    LOG.info(f"time of the program: {time.time() - t}")
