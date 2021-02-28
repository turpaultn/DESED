# -*- coding: utf-8 -*-
import time
import argparse
import os.path as osp
import glob
from pprint import pformat
import logging

import desed
from desed.generate_synthetic import generate_files_from_jams, generate_tsv_from_jams
from desed.logger import create_logger
from desed.download import unsplit_desed_soundbank, download_and_unpack_archive

if __name__ == "__main__":
    LOG = create_logger("DESED", terminal_level=logging.INFO)
    LOG.info(__file__)
    t = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("--save_jams", action="store_true", default=False)
    parser.add_argument("--basedir", type=str, default="../data/dataset")
    parser.add_argument("--soundbank_dir", type=str, default="../data/soundbank")
    parser.add_argument("--real_basedir", type=str, default=None)

    args = parser.parse_args()
    pformat(vars(args))

    base_folder = args.basedir
    soundbank_dir = args.soundbank_dir
    real_basedir = args.real_basedir
    if real_basedir is None:
        real_basedir = base_folder

    # ##########
    # Real data
    # ##########
    # desed.download_real(real_basedir)

    # ##########
    # Synthetic soundbank
    # ##########
    # Download the soundbank
    if not osp.exists(soundbank_dir):
        # Soundbank
        # Be careful, in 2019, we don't have the train-valid split !!
        desed.download.download_desed_soundbank(
            soundbank_dir, sins_bg=True, tut_bg=True, split_train_valid=False
        )
    else:
        # If you have the validation split, you should rearrange the soundbank as in 2019 (unsplitted)
        if osp.exists(osp.join(soundbank_dir, "audio", "validation")):
            unsplit_desed_soundbank(soundbank_dir)

    # ##########
    # Synthetic soundscapes
    # ##########
    # #
    # Eval soundscapes
    # In 2019, the evaluation data has also been provided in a tar.gz since some files were
    # created using matlab (distortions)
    url_jams_archive = "https://zenodo.org/record/3571305/files/DESED_synth_eval_dcase2019.tar.gz?download=1"
    download_and_unpack_archive(url_jams_archive, destination_folder=base_folder)

    # Download jams:
    url_jams_archive = "https://zenodo.org/record/3571305/files/DESED_synth_dcase2019jams.tar.gz?download=1"
    download_and_unpack_archive(url_jams_archive, destination_folder=base_folder)
    # Todo re-upload 2019 jams without having this "synthetic" parent folder
    base_folder = osp.join(base_folder, "synthetic")

    # #
    # Training soundscapes
    train_folder = osp.join(
        base_folder, "metadata", "train", "soundscapes", "synthetic"
    )
    out_train_folder = osp.join(base_folder, "audio", "train", "synthetic")
    if args.save_jams:
        out_folder_jams_train = out_train_folder
    else:
        out_folder_jams_train = None
    out_train_tsv = osp.join(
        base_folder, "metadata", "train", "soundscapes", "synthetic.tsv"
    )

    list_jams_train = glob.glob(osp.join(train_folder, "*.jams"))
    fg_path_train = osp.join(soundbank_dir, "audio", "train", "soundbank", "foreground")
    bg_path_train = osp.join(soundbank_dir, "audio", "train", "soundbank", "background")
    generate_files_from_jams(
        list_jams_train,
        out_train_folder,
        fg_path=fg_path_train,
        bg_path=bg_path_train,
        out_folder_jams=out_folder_jams_train,
    )
    generate_tsv_from_jams(list_jams_train, out_train_tsv)

    # In the following, we regenerate the evaluation data from jams. In 2019 (except distotions),

    # # In the evaluation part, there multiple subsets which allows to check robustness of systems
    # eval_folder = osp.join(base_folder, 'metadata', 'eval', "soundscapes")
    # list_folders = [osp.join(eval_folder, dI) for dI in os.listdir(eval_folder) if osp.isdir(osp.join(eval_folder, dI))]
    # fg_path_eval = osp.join(soundbank_dir, "audio", "eval", "soundbank", "foreground")
    # bg_path_eval = osp.join(soundbank_dir, "audio", "eval", "soundbank", "background")
    #
    # for folder in list_folders:
    #     bn_dir = osp.basename(folder)
    #     # Manage cases with different folders to create sounds.
    #     if bn_dir in ["500ms", "5500ms", "9500ms"]:
    #         fg_path_eval = osp.join(soundbank_dir, "audio", "eval", "soundbank", "foreground_on_off")
    #         bg_path_eval = osp.join(soundbank_dir, "audio", "eval", "soundbank", "background")
    #     elif bn_dir in ["ls_0dB", "ls_15dB", "ls_30dB"]:
    #         fg_path_eval = osp.join(soundbank_dir, "audio", "eval", "soundbank", "foreground_short")
    #         bg_path_eval = osp.join(soundbank_dir, "audio", "eval", "soundbank", "background_long")
    #     else:
    #         fg_path_eval = osp.join(soundbank_dir, "audio", "eval", "soundbank", "foreground")
    #         bg_path_eval = osp.join(soundbank_dir, "audio", "eval", "soundbank", "background")
    #
    #     LOG.info(folder)
    #     bn = osp.basename(folder)
    #     out_folder = osp.join(base_folder, "audio", "eval", "soundscapes", bn)
    #     out_tsv = osp.join(base_folder, "metadata", "eval", "soundscapes", bn + ".tsv")
    #
    #     list_jams = glob.glob(osp.join(folder, "*.jams"))
    #     if args.save_jams:
    #         out_folder_jams_eval = out_folder
    #     else:
    #         out_folder_jams_eval = None
    #     generate_files_from_jams(list_jams, out_folder, fg_path=fg_path_eval, bg_path=bg_path_eval,
    #                              out_folder_jams=out_folder_jams_eval)
    #     generate_tsv_from_jams(list_jams, out_tsv)
