# -*- coding: utf-8 -*-
import time
import argparse
import os
import os.path as osp
import glob
from pprint import pformat
import logging

from desed.generate_synthetic import generate_files_from_jams, generate_tsv_from_jams
from desed.logger import create_logger


if __name__ == '__main__':
    LOG = create_logger("DESED", terminal_level=logging.INFO)
    LOG.info(__file__)
    t = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--save_jams', action="store_true", default=False)
    parser.add_argument('--basedir', type=str, default="..")
    args = parser.parse_args()
    pformat(vars(args))

    base_folder = args.basedir
    # ########
    # Training
    # ########
    train_folder = osp.join(base_folder, 'metadata', 'train', 'soundscapes', 'synthetic')
    out_train_folder = osp.join(base_folder, 'audio', 'train', 'synthetic')
    if args.save_jams:
        out_folder_jams_train = out_train_folder
    else:
        out_folder_jams_train = None
    out_train_tsv = osp.join(base_folder, 'metadata', 'train', 'soundscapes', 'synthetic.tsv')

    list_jams_train = glob.glob(osp.join(train_folder, "*.jams"))
    fg_path_train = osp.join(base_folder, "audio", "train", "soundbank", "foreground")
    bg_path_train = osp.join(base_folder, 'audio', "train", "soundbank", "background")
    generate_files_from_jams(list_jams_train, out_train_folder, fg_path=fg_path_train, bg_path=bg_path_train,
                             out_folder_jams=out_folder_jams_train)
    generate_tsv_from_jams(list_jams_train, out_train_tsv)

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
        out_tsv = osp.join(base_folder, "metadata", "eval", "soundscapes", bn + ".tsv")

        list_jams = glob.glob(osp.join(folder, "*.jams"))
        if args.save_jams:
            out_folder_jams_eval = out_folder
        else:
            out_folder_jams_eval = None
        generate_files_from_jams(list_jams, out_folder, fg_path=fg_path_eval, bg_path=bg_path_eval,
                                 out_folder_jams=out_folder_jams_eval)
        generate_tsv_from_jams(list_jams, out_tsv)
