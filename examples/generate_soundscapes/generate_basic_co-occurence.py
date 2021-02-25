# -*- coding: utf-8 -*-
import time
import argparse
import os.path as osp
import json
from pprint import pformat
import logging

from desed.generate_synthetic import SoundscapesGenerator
from desed.post_process import rm_high_polyphony, post_process_txt_labels
from desed.logger import create_logger


if __name__ == "__main__":
    LOG = create_logger("DESED", terminal_level=logging.INFO)
    LOG.info(__file__)
    t = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("--fg_folder", type=str, required=True)
    parser.add_argument("--bg_folder", type=str, required=True)
    parser.add_argument("--out_folder", type=str, required=True)
    parser.add_argument(
        "--co_occur_json",
        type=str,
        default=osp.join("event_occurences", "event_occurences_train.json"),
    )
    parser.add_argument("--out_tsv", type=str, default=None)
    parser.add_argument("--number", type=int, default=1000)
    args = parser.parse_args()
    pformat(vars(args))

    # Output folder, in args
    out_folder = args.out_folder
    out_tsv = args.out_tsv

    # Default parameters
    clip_duration = 10.0
    ref_db = -55
    samplerate = 16000

    sg = SoundscapesGenerator(
        duration=clip_duration,
        fg_folder=args.fg_folder,
        bg_folder=args.bg_folder,
        ref_db=ref_db,
        samplerate=samplerate,
    )

    co_occur_json = osp.join("event_occurences", "event_occurences_train.json")
    with open(co_occur_json) as json_file:
        co_occur_dict = json.load(json_file)

    sg.generate_by_label_occurence(
        label_occurences=co_occur_dict, number=args.number, out_folder=out_folder
    )

    rm_high_polyphony(out_folder, 3)
    post_process_txt_labels(out_folder, output_folder=out_folder, output_tsv=out_tsv)
    LOG.info(f"time of the program: {time.time() - t}")
