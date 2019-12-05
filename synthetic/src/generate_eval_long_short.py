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
from pprint import pformat

from utils import create_folder, rm_high_polyphony, post_processing_annotations
from generate_eval_FBSNR import generate_new_bg_snr_files
from Logger import LOG


if __name__ == '__main__':
    LOG.info(__file__)
    t = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--outfolder', type=str, default=osp.join('..', 'eval', 'soundscapes_generated_ls'))
    parser.add_argument('--outcsv', type=str, default=osp.join('..', 'eval', "soundscapes_generated_ls", "XdB.csv"))
    parser.add_argument('--number', type=int, default=1000)
    parser.add_argument('--fgfolder', type=str, default=osp.join("..", "eval", "soundbank", "foreground_short"))
    parser.add_argument('--bgfolder', type=str, default=osp.join("..", "eval", "soundbank", "background_long"))
    args = parser.parse_args()
    pformat(vars(args))

    # General output folder, in args
    out_folder = args.outfolder
    create_folder(out_folder)

    # Default parameters
    n_soundscapes = args.number
    ref_db = -50
    duration = 10.0

    # ################
    # Long event as background, short events as foreground
    # ###########
    fg_folder = args.fgfolder
    bg_folder = args.bgfolder
    # Generate events same way as the training set
    min_events = 1
    max_events = 5

    event_time_dist = 'truncnorm'
    event_time_mean = 5.0
    event_time_std = 2.0
    event_time_min = 0.0
    event_time_max = 10.0

    source_time_dist = 'const'
    source_time = 0.0

    event_duration_dist = 'uniform'
    event_duration_min = 0.25
    event_duration_max = 10.0

    snr_dist = 'const'
    snr = 30

    pitch_dist = 'uniform'
    pitch_min = -3.0
    pitch_max = 3.0

    time_stretch_dist = 'uniform'
    time_stretch_min = 1
    time_stretch_max = 1

    out_folder_ls_30 = osp.join(out_folder, "ls_30dB")
    create_folder(out_folder_ls_30)
    for n in range(n_soundscapes):
        LOG.debug('Generating soundscape: {:d}/{:d}'.format(n+1, n_soundscapes))
        # create a scaper
        sc = scaper.Scaper(duration, fg_folder, bg_folder)
        sc.protected_labels = []
        sc.ref_db = ref_db

        # add background
        sc.add_background(label=('choose', []),
                          source_file=('choose', []),
                          source_time=('const', 0))

        # add random number of foreground events
        n_events = np.random.randint(min_events, max_events+1)
        for _ in range(n_events):
            sc.add_event(label=('choose', []),
                         source_file=('choose', []),
                         source_time=(source_time_dist, source_time),
                         event_time=(event_time_dist, event_time_mean, event_time_std, event_time_min, event_time_max),
                         event_duration=(event_duration_dist, event_duration_min, event_duration_max),
                         snr=(snr_dist, snr),
                         pitch_shift=(pitch_dist, pitch_min, pitch_max),
                         time_stretch=(time_stretch_dist, time_stretch_min, time_stretch_max))

        # generate
        audiofile = osp.join(out_folder_ls_30, f"{n}.wav")
        jamsfile = osp.join(out_folder_ls_30, f"{n}.jams")
        # Useless since there is no background event in there
        # txtfile = osp.join(out_folder_ls_30, f"{n}.txt")

        sc.generate(audiofile, jamsfile,
                    allow_repeated_label=True,
                    allow_repeated_source=True,
                    reverb=0.1,
                    disable_sox_warnings=True,
                    no_audio=False,
                    txt_path=None)

    rm_high_polyphony(out_folder_ls_30, 3)
    post_processing_annotations(out_folder_ls_30, output_folder=out_folder_ls_30, output_csv=args.outcsv,
                                background_label=True)

    # We create the same dataset with different background SNR
    # Be careful, 15 means the background SNR is 15,
    # so the foreground background snr ratio is between -9dB and 15dB
    out_folder_ls_15 = osp.join(out_folder, "ls_15dB")
    create_folder(out_folder_ls_15)
    generate_new_bg_snr_files(15, out_folder_ls_30, out_folder_ls_15)
    
    # Same for 30dB
    out_folder_ls_0 = osp.join(out_folder, "ls_0dB")
    create_folder(out_folder_ls_0)
    generate_new_bg_snr_files(30, out_folder_ls_30, out_folder_ls_0)

