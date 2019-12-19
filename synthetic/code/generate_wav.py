# -*- coding: utf-8 -*-
#########################################################################
# Initial software
# Copyright Nicolas Turpault, Romain Serizel, Justin Salamon, Ankit Parag Shah, 2019, v1.0
# This software is distributed under the terms of the License MIT
#########################################################################
import time
import argparse
import os
import os.path as osp
import glob
from pprint import pformat
import logging

from desed.generate_synthetic import generate_files_from_jams, generate_csv_from_jams
from desed.Logger import create_logger


if __name__ == '__main__':
    LOG = create_logger("DESED", "Desed.log", terminal_level=logging.INFO, file_level=logging.INFO)
    LOG.info(__file__)
    t = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--overwrite-jams', action="store_true", default=False)
    parser.add_argument('--basedir', type=str, default="..")
    args = parser.parse_args()
    pformat(vars(args))

    base_folder = args.basedir
    # ########
    # Training
    # ########
    train_folder = osp.join(base_folder, 'metadata', 'train', 'soundscapes', 'synthetic')
    out_train_folder = osp.join(base_folder, 'audio', 'train', 'synthetic')
    out_train_csv = osp.join(base_folder, 'metadata', 'train', 'soundscapes', 'synthetic.csv')

    list_jams_train = glob.glob(osp.join(train_folder, "*.jams"))
    fg_path_train = osp.join(base_folder, "audio", "train", "soundbank", "foreground")
    bg_path_train = osp.join(base_folder, 'audio', "train", "soundbank", "background")
    generate_files_from_jams(list_jams_train, out_train_folder, fg_path=fg_path_train, bg_path=bg_path_train,
                             overwrite_jams=args.overwrite_jams)
    generate_csv_from_jams(list_jams_train, out_train_csv)

    # ########
    # Eval
    # ########
    # In the evaluation part, there multiple subsets which allows to check robustness of systems
    eval_folder = osp.join(base_folder, 'metadata', 'eval', "soundscapes")
    list_folders = [osp.join(eval_folder, dI) for dI in os.listdir(eval_folder) if osp.isdir(osp.join(eval_folder, dI))]
    fg_path_eval = osp.join(base_folder, "audio", "eval", "soundbank", "foreground")
    bg_path_eval = osp.join(base_folder, "audio", "eval", "soundbank", "background")

    for folder in list_folders:
        bn_dir = osp.basename(folder)
        # Manage cases with different folders to create sounds.
        if bn_dir in ["500ms", "5500ms", "9500ms"]:
            fg_path_eval = osp.join(base_folder, "audio", "eval", "soundbank", "foreground_on_off")
            bg_path_eval = osp.join(base_folder, "audio", "eval", "soundbank", "background")
        elif bn_dir in ["ls_0dB", "ls_15dB", "ls_30dB"]:
            fg_path_eval = osp.join(base_folder, "audio", "eval", "soundbank", "foreground_short")
            bg_path_eval = osp.join(base_folder, "audio", "eval", "soundbank", "background_long")
        else:
            fg_path_eval = osp.join(base_folder, "audio", "eval", "soundbank", "foreground")
            bg_path_eval = osp.join(base_folder, "audio", "eval", "soundbank", "background")

        LOG.info(folder)
        bn = osp.basename(folder)
        out_folder = osp.join(base_folder, "audio", "eval", "soundscapes", bn)
        out_csv = osp.join(base_folder, "metadata", "eval", "soundscapes", bn + ".csv")

        list_jams = glob.glob(osp.join(folder, "*.jams"))
        generate_files_from_jams(list_jams, out_folder, fg_path=fg_path_eval, bg_path=bg_path_eval,
                                 overwrite_jams=args.overwrite_jams)
        generate_csv_from_jams(list_jams, out_csv)
