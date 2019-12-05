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

            
if __name__ == "__main__":
    LOG.info(__file__)
    t = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("--outfolder", type=str, default=osp.join("..", "training", "synthetic", "soundscapes_generated"))
    parser.add_argument("--outcsv", type=str, default=osp.join("..", "training", "synthetic_generated.csv"))
    parser.add_argument("--number", type=int, default=1000)
    args = parser.parse_args()
    pformat(vars(args))

    # Output folder, in args
    outfolder = args.outfolder
    create_folder(outfolder)
    out_csv = args.outcsv

    # SCAPER SETTINGS
    fg_folder = osp.join("..", "audio", "train", "soundbank", "foreground")
    bg_folder = osp.join("..", "audio", "train", "soundbank", "background")
    # JSON file
    param_file = osp.join("event_occurences", "event_occurences_train.json")

    # Default parameters
    n_soundscapes = args.number
    ref_db = -50
    duration = 10.0

    with open(param_file) as json_file:
        params = json.load(json_file)

    n = 0
    for class_lbl in params.keys():
        class_params = params[class_lbl]
        for i in range(int(n_soundscapes * class_params["prob"])):

            print(f"Generating soundscape: {n + 1}/{n_soundscapes}")

            # create a scaper
            sc = scaper.Scaper(duration, fg_folder, bg_folder)
            sc.protected_labels = []
            sc.ref_db = ref_db

            # add background
            sc.add_background(label=("choose", []),
                              source_file=("choose", []),
                              source_time=("const", 0))

            # add main event
            sc = add_event(sc, class_lbl, duration, fg_folder)

            # add random number of foreground events
            n_events = np.random.randint(0, class_params["event_max"])
            for _ in range(n_events):
                chosen_class = choose_class(class_params)
                sc = add_event(sc, chosen_class, duration, fg_folder)

            # generate
            audiofile = osp.join(outfolder, f"{n}.wav")
            jamsfile = osp.join(outfolder, f"{n}.jams")
            txtfile = osp.join(outfolder, f"{n}.txt")
            sc.generate(audiofile, jamsfile,
                        allow_repeated_label=True,
                        allow_repeated_source=True,
                        reverb=0.1,
                        disable_sox_warnings=True,
                        no_audio=False,
                        txt_path=txtfile)
            n += 1

    rm_high_polyphony(outfolder, 3)
    post_processing_annotations(outfolder, output_folder=outfolder, output_csv=out_csv)
    LOG.info(f"time of the program: {time.time() - t}")
