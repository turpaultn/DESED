# -*- coding: utf-8 -*-
import functools
import glob
import json
import logging
import time
import argparse
import os.path as osp
from pprint import pformat

from desed.generate_synthetic import SoundscapesGenerator, generate_files_from_jams
from desed.logger import create_logger
from desed.post_process import rm_high_polyphony, post_process_txt_labels
from desed.utils import create_folder, modify_jams, change_snr


if __name__ == "__main__":
    LOG = create_logger(__name__, terminal_level=logging.INFO)
    LOG.info(__file__)
    t = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("--fg_folder", type=str, required=True)
    parser.add_argument("--bg_folder", type=str, required=True)
    parser.add_argument("--out_folder", type=str, required=True)
    parser.add_argument(
        "--out_tsv",
        type=str,
        default=osp.join("..", "..", "data", "generated", "FBSNR_XdB.tsv"),
    )
    parser.add_argument("--number", type=int, default=1000)
    args = parser.parse_args()
    pformat(vars(args))

    # General output folder, in args
    out_folder = args.out_folder
    create_folder(out_folder)
    out_tsv = args.out_tsv
    if out_tsv is not None:
        create_folder(osp.dirname(args.out_tsv))

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

    # Generate events same way as the training set
    out_folder_30 = osp.join(out_folder, "30dB")
    create_folder(out_folder_30)
    param_json = osp.join("event_occurences", "event_occurences_eval.json")
    with open(param_json) as json_file:
        co_occur_dict = json.load(json_file)
    sg.generate_by_label_occurence(
        label_occurences=co_occur_dict, number=args.number, out_folder=out_folder_30
    )

    # Remove files that have polyphony greater than 3
    rm_high_polyphony(out_folder_30, 3)
    # Combine labels of same events appending at the same time or less than 150ms interval
    post_process_txt_labels(
        out_folder_30, output_folder=out_folder_30, output_tsv=out_tsv
    )

    # ###
    # Generate variation of the dataset by varying the FBSNR
    # ###
    # We create the same dataset with different background SNR
    # The foreground background snr ratio is between 0dB and 24dB (see utils snr_min (6dB) and snr_max (30dB))
    out_folder_24 = osp.join(out_folder, "24dB")
    create_folder(out_folder_24)

    jams_to_modify = glob.glob(osp.join(out_folder_30, "*.jams"))
    # Put FBSNR to [0;24] range so reducing of 6 compared to [6;30]
    minus_6_snr = functools.partial(change_snr, db_change=-6)
    new_jams24 = modify_jams(jams_to_modify, minus_6_snr, out_folder_24)
    generate_files_from_jams(new_jams24, out_folder_24, out_folder_24)

    # Same for 15
    out_folder_15 = osp.join(out_folder, "15dB")
    create_folder(out_folder_15)
    minus_15_snr = functools.partial(change_snr, db_change=-15)
    new_jams15 = modify_jams(jams_to_modify, minus_15_snr, out_folder_15)
    generate_files_from_jams(new_jams15, out_folder_15, out_folder_15)

    out_folder_0 = osp.join(out_folder, "0dB")
    create_folder(out_folder_0)
    minus_30_snr = functools.partial(change_snr, db_change=-30)
    new_jams0 = modify_jams(jams_to_modify, minus_30_snr, out_folder_0)
    generate_files_from_jams(new_jams0, out_folder_0, out_folder_0)
