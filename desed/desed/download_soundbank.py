import glob
import inspect
import logging
import os
import shutil

import pandas as pd

from .logger import create_logger
from .utils import download_file, create_folder


def copy_files_kept(meta_df, list_sins_files, input_dir, output_dir):
    df_files = pd.DataFrame(list_sins_files, columns=["filename"])
    df_files["filename"] = df_files.filename.apply(lambda x: os.path.basename(x))

    merged = meta_df.merge(df_files, on='filename')
    merged.apply(
        lambda x: shutil.copy(os.path.join(input_dir, x[0]), os.path.join(output_dir, x["filename"])),
        axis=1)


def get_sins(destination_folder, classes_kept=["other"], keep_original=False, archive_folder="./"):
    """ Download SINS database: see https://zenodo.org/record/1247102
    Args:
        destination_folder: str, the destination folder of sins database (structure included)
        classes_kept: list, list of classes to keep in the origingal SINS database to use as backgrounds
        keep_original: bool, whether to keep the original database too or not.
        archive_folder: str, the folder where to store the archive_folder

    Returns:

    """
    logger = create_logger(__name__ + "/" + inspect.currentframe().f_code.co_name, terminal_level=logging.INFO)
    zip_file_url_meta = f"https://zenodo.org/record/1247102/files/DCASE2018-task5-dev.meta.zip?download=1"
    fpath_meta = os.path.join(archive_folder, "DCASE2018-task5-dev.meta.zip")
    download_file(zip_file_url_meta, fpath_meta)
    shutil.unpack_archive(fpath_meta, destination_folder)

    extracted_sins_path = os.path.join(destination_folder, "DCASE2018-task5-dev")
    final_sins_path = os.path.join(destination_folder, "background", "sins")
    create_folder(final_sins_path)

    df = pd.read_csv(os.path.join(extracted_sins_path, "meta.txt"), sep="\t", header=None)
    df["filename"] = df[0].apply(lambda x: os.path.basename(x))
    df = df[df[1].isin(classes_kept)]

    for i in range(1, 24):
        logger.info(f"SINS downloading zip {i} / 23 ...")
        # Download the first zip, and keep only other
        zip_file_url = f"https://zenodo.org/record/1247102/files/DCASE2018-task5-dev.audio.{i}.zip?download=1"
        fpath = os.path.join(archive_folder, f"DCASE2018-task5-dev.audio.{i}.zip")
        download_file(zip_file_url, fpath)
        shutil.unpack_archive(fpath, destination_folder)

        list_files_i = glob.glob(os.path.join(extracted_sins_path, "audio", "*"))
        copy_files_kept(df, list_files_i, extracted_sins_path, final_sins_path)

        if not keep_original:
            # Save disk space if limited
            shutil.rmtree(os.path.join(extracted_sins_path, "audio"))
            #remove "DCASE2018-task5-dev.audio.{i}.zip" files
            os.remove(fpath)

    if not keep_original:
        shutil.rmtree(extracted_sins_path)
        #remove DCASE2018-task5-dev.meta.zip file
        os.remove(fpath_meta)


def get_tut(destination_folder, classes_kept=["home", "office", "library"],
            keep_original=False, archive_folder="./"):
    """ Download 'TUT Acoustic scenes 2017, Development dataset', see: https://zenodo.org/record/400515
    Args:
        destination_folder: str, the path where to download the dataset
        classes_kept: list, list of classes to be kept
        keep_original: bool, whether to keep the original database too or not.
        archive_folder: str, the folder where to store the archive_folder
    Returns:

    """
    logger = create_logger(__name__ + "/" + inspect.currentframe().f_code.co_name, terminal_level=logging.INFO)
    zip_meta_tut = f"https://zenodo.org/record/400515/files/TUT-acoustic-scenes-2017-development.meta.zip?download=1"
    fpath_meta = os.path.join(archive_folder, "TUT-acoustic-scenes-2017-development.meta.zip")
    download_file(zip_meta_tut, os.path.join(archive_folder, fpath_meta))
    shutil.unpack_archive(fpath_meta, destination_folder)

    extracted_tut_path = os.path.join(destination_folder, "TUT-acoustic-scenes-2017-development")
    final_tut_path = os.path.join(destination_folder, "background", "tut-scenes-2017-dev")
    create_folder(final_tut_path)

    df = pd.read_csv(os.path.join(extracted_tut_path, "meta.txt"), sep="\t", header=None)
    df["filename"] = df[0].apply(lambda x: os.path.basename(x))
    df = df[df[1].isin(classes_kept)]

    for i in range(1, 10):
        logger.info(f"TUT (scenes-2017-dev) downloading zip {i} / 9 ...")
        zip_file_url = f"https://zenodo.org/record/400515/files/" \
            f"TUT-acoustic-scenes-2017-development.audio.{i}.zip?download=1"
        fpath = os.path.join(archive_folder, f"TUT-acoustic-scenes-2017-development.audio.{i}.zip")
        download_file(zip_file_url, fpath)
        shutil.unpack_archive(fpath, destination_folder)

        list_files_i = glob.glob(os.path.join(extracted_tut_path, "audio", "*"))
        copy_files_kept(df, list_files_i, extracted_tut_path, final_tut_path)

    if not keep_original:
        shutil.rmtree(extracted_tut_path)


def get_backgrounds_train(basedir, sins=True, tut=False, keep_original=False, archive_folder="./"):
    """ Download the background files of the DESED soundbank.
    (These files were not included in the Zenodo because of redistributing license issues.)
    Args:
        basedir: str, the base folder of DESED dataset.
        sins: bool, download part of sins database as backgrounds.
        tut: bool, download part of TUT database as backgrounds.
        keep_original: bool, whether to keep the original databases too (sins, tut)
        archive_folder: str, the path where to store the zip files.
    Returns:

    """
    destination_folder = os.path.join(basedir, "audio", "train", "soundbank")
    if sins:
        get_sins(destination_folder, keep_original=keep_original, archive_folder=archive_folder)

    if tut:
        get_tut(destination_folder, keep_original=keep_original, archive_folder=archive_folder)


def download_zenodo_soundbank(destination_folder, archive_folder="./"):
    """ Be careful, there are only the foregrounds of training.
    Args:
        destination_folder: str, the path of the root of the soundbank (will create the structure inside)
        archive_folder: str, the folder where to store the archive_folder
    Returns:

    """
    zip_meta_tut = "https://zenodo.org/record/4307908/files/DESED_synth_soundbank.tar.gz?download=1"
    fname = os.path.join(archive_folder, "DESED_synth_soundbank.tar.gz")
    download_file(zip_meta_tut, fname)
    shutil.unpack_archive(fname, destination_folder)


def make_validation_sb(basedir):
    fname_valid = "https://zenodo.org/record/4307908/files/soundbank_validation.tsv?download=1"
    fpath = os.path.join(basedir, "soundbank_validation.tsv")
    download_file(fname_valid, fpath)
    df = pd.read_csv(fpath, sep="\t")
    for fpath in df.filepath:
        source_path = os.path.join(basedir, fpath.replace("validation", "train"))
        if os.path.exists(source_path):
            destination_path = os.path.join(basedir, fpath)
            create_folder(os.path.dirname(destination_path))
            shutil.move(source_path, destination_path)
    print("Splitted files in train and validation")


def download_soundbank(basedir, sins_bg=True, tut_bg=False, split_train_valid=True, keep_original_sins_tut=False):
    tmp_folder = "zip_extracted_folder"
    create_folder(tmp_folder)

    print("downloading soundbank (foregrounds)...")
    download_zenodo_soundbank(basedir, archive_folder=tmp_folder)
    print("Downloading backgrounds...")
    get_backgrounds_train(basedir, sins_bg, tut_bg, keep_original=keep_original_sins_tut, archive_folder=tmp_folder)
    if split_train_valid:
        print("Splitting soundbank train into train and validation (90%/10%)...")
        make_validation_sb(basedir)

    shutil.rmtree(tmp_folder)
