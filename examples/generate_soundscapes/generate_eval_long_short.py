# -*- coding: utf-8 -*-
import glob
import logging
import time
import argparse
import os.path as osp
from pprint import pformat

from desed.utils import create_folder, modify_jams, change_snr
from desed.post_process import rm_high_polyphony, post_process_txt_labels
from desed.generate_synthetic import SoundscapesGenerator
from desed.logger import create_logger
import config as cfg


if __name__ == "__main__":
    LOG = create_logger(__name__, terminal_level=logging.INFO)
    LOG.info(__file__)
    t = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fg_folder",
        type=str,
        required=True,
        help="the foreground folder (in which there are subfolders for each class, "
        "here consider using foreground_short",
    )
    parser.add_argument(
        "--bg_folder",
        type=str,
        required=True,
        help="the background folder (in which there are subfolders for each class, "
        "here consider using background_long",
    )
    parser.add_argument("--out_folder", type=str, required=True)
    parser.add_argument(
        "--out_tsv",
        type=str,
        default=osp.join("..", "..", "data", "generated", "long_short.tsv"),
    )
    parser.add_argument("--number", type=int, default=1000)

    args = parser.parse_args()
    pformat(vars(args))

    # General output folder, in args
    out_folder = args.out_folder
    create_folder(out_folder)
    create_folder(osp.dirname(args.out_tsv))

    # ################
    # Long event as background, short events as foreground
    # ###########
    duration = 10.0
    ref_db = -55
    samplerate = 16000

    sg = SoundscapesGenerator(
        duration=duration,
        fg_folder=args.fg_folder,
        bg_folder=args.bg_folder,
        ref_db=ref_db,
        samplerate=samplerate,
    )

    n_soundscapes = args.number
    # Distribution of events
    min_events = 1
    max_events = 5

    evt_time_dist = "truncnorm"
    evt_time_mean = 5.0
    evt_time_std = 2.0
    evt_time_min = 0.0
    evt_time_max = 10.0

    source_time_dist = "const"
    source_time = 0.0

    event_duration_dist = "uniform"
    event_duration_min = 0.25
    event_duration_max = 10.0

    snr_dist = "const"
    snr = 30

    pitch_dist = "uniform"
    pitch_min = -3.0
    pitch_max = 3.0

    time_stretch_dist = "uniform"
    time_stretch_min = 1
    time_stretch_max = 1

    out_folder_ls_30 = osp.join(out_folder, "ls_30dB")
    create_folder(out_folder_ls_30)
    sg.generate(
        n_soundscapes,
        out_folder_ls_30,
        min_events,
        max_events,
        labels=("choose", []),
        source_files=("choose", []),
        sources_time=(source_time_dist, source_time),
        events_start=(
            evt_time_dist,
            evt_time_mean,
            evt_time_std,
            evt_time_min,
            evt_time_max,
        ),
        events_duration=(event_duration_dist, event_duration_min, event_duration_max),
        snrs=("const", 30),
        pitch_shifts=("uniform", -3.0, 3.0),
        time_stretches=("uniform", 1, 1),
        txt_file=True,
    )

    rm_high_polyphony(out_folder_ls_30, 3)
    post_process_txt_labels(
        out_folder_ls_30,
        output_folder=out_folder_ls_30,
        output_tsv=args.out_tsv,
        background_label=True,
    )

    list_jams = glob.glob(osp.join(out_folder_ls_30, "*.jams"))
    # We create the same dataset with different background SNR
    # Be careful, 15 means the background SNR is 15,
    # so the foreground background snr ratio is between -9dB and 15dB
    out_folder_ls_15 = osp.join(out_folder, "ls_15dB")
    modify_jams(list_jams, change_snr, out_folder_ls_15, db_change=-15)

    # Same for 0dB FBSNR, from original fbsnr [6;30]dB, we go to [-24;0]dB FBSNR
    out_folder_ls_0 = osp.join(out_folder, "ls_0dB")
    modify_jams(list_jams, change_snr, out_folder_ls_15, db_change=-30)
