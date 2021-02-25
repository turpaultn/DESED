import glob
import os

import desed
from desed.utils import download_and_unpack_archive

if __name__ == '__main__':
    basedir_dataset = "../data/dataset"
    soundbank_dir = "../data/soundbank"

    download = False
    # Download the data
    if download:
        # Real
        desed.download_real(basedir_dataset)
        # Soundbank
        desed.download_soundbank(soundbank_dir, sins_bg=True, tut_bg=True)

    # Download jams:
    # Train and val
    url_jams_archive = "https://zenodo.org/record/4560938/files/DESED_synth_dcase20_train_val_jams.tar.gz?download=1"
    download_and_unpack_archive(url_jams_archive, destination_folder=basedir_dataset)
    # Eval
    url_jams_archive = "https://zenodo.org/record/4560938/files/DESED_synth_dcase20_eval_jams.tar.gz?download=1"
    download_and_unpack_archive(url_jams_archive, destination_folder=basedir_dataset)

    # Generate audio files. We can loop because it is the same structure of folders for the three sets.
    for set_name in ["train", "validation", "eval"]:
        path_to_jams = os.path.join(basedir_dataset, "audio", set_name, "synthetic20_" + set_name, "soundscapes")
        list_jams = glob.glob(os.path.join(path_to_jams, "*.jams"))
        fg_path = os.path.join(soundbank_dir, "audio", set_name, "soundbank", "foreground")
        bg_path = os.path.join(soundbank_dir, "audio", set_name, "soundbank", "background")
        out_tsv = os.path.join(basedir_dataset, "metadata", set_name, "synthetic20_" + set_name, "soundscapes.tsv")

        desed.generate_files_from_jams(
            list_jams,
            fg_path=fg_path,
            bg_path=bg_path,
            out_folder=path_to_jams,
            save_isolated_events=False,
            overwrite_exist_audio=False
        )
        desed.generate_tsv_from_jams(list_jams, out_tsv)

