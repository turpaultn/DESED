import argparse
import glob
import os
from pprint import pformat

import desed
from desed.utils import download_and_unpack_archive
from desed.download_soundbank import split_soundbank_train_val

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--basedir", type=str, default="../data/dcase2019")
    parser.add_argument("--soundbank_dir", type=str, default="../data/soundbank")
    parser.add_argument("--real_basedir", type=str, default=None)
    args = parser.parse_args()
    pformat(vars(args))

    basedir_dataset = args.basedir
    soundbank_dir = args.soundbank_dir
    real_basedir = args.real_basedir
    if real_basedir is None:
        real_basedir = basedir_dataset

    # ##########
    # Real data
    # ##########
    desed.download_real(real_basedir)

    # ##########
    # Synthetic soundbank
    # ##########
    # Download the soundbank if needed
    if not os.path.exists(soundbank_dir):
        desed.download_soundbank(soundbank_dir, sins_bg=True, tut_bg=True)
    else:
        # If you don't have the validation split, rearrange the soundbank in train-valid (split in 90%/10%)
        if not os.path.exists(os.path.join(soundbank_dir, "audio", "validation")):
            split_soundbank_train_val(soundbank_dir)

    # ##########
    # Synthetic soundscapes
    # ##########
    # Download jams:
    # Train and val
    url_jams_archive = "https://zenodo.org/record/4560938/files/DESED_synth_dcase20_train_val_jams.tar.gz?download=1"
    download_and_unpack_archive(url_jams_archive, destination_folder=basedir_dataset)
    # Eval
    url_jams_archive = "https://zenodo.org/record/4560938/files/DESED_synth_dcase20_eval_jams.tar.gz?download=1"
    download_and_unpack_archive(url_jams_archive, destination_folder=basedir_dataset)

    # Generate audio files. We can loop because it is the same structure of folders for the three sets.
    for set_name in ["train", "validation", "eval"]:
        path_to_jams = os.path.join(
            basedir_dataset, "audio", set_name, "synthetic20_" + set_name, "soundscapes"
        )
        list_jams = glob.glob(os.path.join(path_to_jams, "*.jams"))
        fg_path = os.path.join(
            soundbank_dir, "audio", set_name, "soundbank", "foreground"
        )
        bg_path = os.path.join(
            soundbank_dir, "audio", set_name, "soundbank", "background"
        )
        out_tsv = os.path.join(
            basedir_dataset,
            "metadata",
            set_name,
            "synthetic20_" + set_name,
            "soundscapes.tsv",
        )

        desed.generate_files_from_jams(
            list_jams,
            fg_path=fg_path,
            bg_path=bg_path,
            out_folder=path_to_jams,
            save_isolated_events=False,
            overwrite_exist_audio=False,
        )
        desed.generate_tsv_from_jams(list_jams, out_tsv)
