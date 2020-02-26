# -*- coding: utf-8 -*-
import logging
import time
import argparse
import os.path as osp
import pandas as pd
from pprint import pformat

from desed.generate_synthetic import generate_new_fg_onset_files, generate_multi_common
from desed.utils import create_folder, rm_high_polyphony, post_processing_txt_annotations
from desed.Logger import create_logger
import config as cfg


if __name__ == '__main__':
    LOG = create_logger(__name__, "Desed.log", terminal_level=logging.INFO)
    LOG.info(__file__)
    t = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--outfolder', type=str,
                        default=osp.join(cfg.audio_path_eval, 'soundscapes_generated_var_onset'))
    parser.add_argument('--outtsvfolder', type=str,
                        default=osp.join(cfg.meta_path_eval, 'soundscapes_generated_var_onset'))
    parser.add_argument('--number', type=int, default=1000)
    parser.add_argument('--fgfolder', type=str, default=osp.join(cfg.audio_path_eval, "soundbank", "foreground_on_off"))
    parser.add_argument('--bgfolder', type=str, default=osp.join(cfg.audio_path_eval, "soundbank", "background"))
    args = parser.parse_args()
    pformat(vars(args))

    # General output folder, in args
    out_folder = args.outfolder
    create_folder(out_folder)

    out_tsv_folder = args.outtsvfolder
    create_folder(out_tsv_folder)

    # Default parameters
    n_soundscapes = args.number
    ref_db = -50
    duration = 10.0

    # ################
    # Varying onset of a single event
    # ###########
    # SCAPER SETTINGS
    fg_folder = args.fgfolder
    bg_folder = args.bgfolder

    source_time_dist = 'const'
    source_time = 0.0

    event_duration_dist = 'uniform'
    event_duration_min = 0.25
    event_duration_max = 10.0

    snr_dist = 'uniform'
    snr_min = 6
    snr_max = 30

    pitch_dist = 'uniform'
    pitch_min = -3.0
    pitch_max = 3.0

    time_stretch_dist = 'uniform'
    time_stretch_min = 1
    time_stretch_max = 1

    event_time_dist = 'truncnorm'
    event_time_mean = 0.5
    event_time_std = 0.25
    event_time_min = 0.25
    event_time_max = 0.750

    out_folder_500 = osp.join(out_folder, "500ms")
    create_folder(out_folder_500)

    generate_multi_common(n_soundscapes, duration, fg_folder, bg_folder, out_folder_500, ref_db=ref_db,
                          min_events=1, max_events=1, labels=('choose', []), source_files=('choose', []),
                          sources_time=(source_time_dist, source_time),
                          events_start=(
                              event_time_dist, event_time_mean, event_time_std, event_time_min, event_time_max),
                          events_duration=(event_duration_dist, event_duration_min, event_duration_max),
                          snrs=(snr_dist, snr_min, snr_max),
                          pitch_shifts=(pitch_dist, pitch_min, pitch_max),
                          time_stretches=(time_stretch_dist, time_stretch_min, time_stretch_max),
                          txt_file=True)

    rm_high_polyphony(out_folder_500, 3)
    out_tsv = osp.join(out_tsv_folder, "500ms.tsv")
    post_processing_txt_annotations(out_folder_500, output_folder=out_folder_500,
                                output_tsv=out_tsv)
    df = pd.read_csv(out_tsv, sep="\t")
    # Be careful, if changing the values of the added onset value,
    # you maybe want to rerun the post_processing_annotations to be sure there is no inconsistency
    out_folder_5500 = osp.join(out_folder, "5500ms")
    create_folder(out_folder_5500)
    add_onset = 5.0
    df["onset"] += add_onset
    df["offset"] = df["offset"].apply(lambda x: min(x, add_onset))
    generate_new_fg_onset_files(add_onset, out_folder_500, out_folder_5500)
    df.to_csv(osp.join(out_tsv_folder, "5500ms.tsv"),
              sep="\t", float_format="%.3f", index=False)

    out_folder_9500 = osp.join(out_folder, "9500ms")
    create_folder(out_folder_9500)
    add_onset = 9.0
    df = pd.read_csv(out_tsv, sep="\t")
    df["onset"] += add_onset
    df["offset"] = df["offset"].apply(lambda x: min(x, add_onset))
    generate_new_fg_onset_files(add_onset, out_folder_500, out_folder_9500)
    df.to_csv(osp.join(out_tsv_folder, "9500ms.tsv"),
              sep="\t", float_format="%.3f", index=False)
