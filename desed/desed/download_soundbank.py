import glob
import inspect
import logging
import os
import shutil

import pandas as pd

from .logger import create_logger
from .utils import download_file, create_folder


def _copy_files_kept(meta_df, input_dir, output_dir):
    """ Fonction to copy some files from input_dir to output_dir.
    The files to copy are stored in a pandas dataframe with a column "filename" and must match a name in the input_dir.

    Args:
        meta_df: pd.Dataframe, the dataframe with a column "filename" of files to keep (filtered filenames).
        input_dir: str, folder containing filenames to match.
        output_dir: str, the destination folder of the files copied

    Returns:

    """
    list_files_available = glob.glob(os.path.join(input_dir, "*"))
    df_files = pd.DataFrame(list_files_available, columns=["filename"])
    df_files["filename"] = df_files.filename.apply(lambda x: os.path.basename(x))

    merged = meta_df.merge(df_files, on="filename")
    merged.apply(
        lambda x: shutil.copy(
            os.path.join(input_dir, x["filename"]),
            os.path.join(output_dir, x["filename"]),
        ),
        axis=1,
    )


def download_sins(destination_folder):
    """ Download SINS database: see https://zenodo.org/record/1247102

    Args:
        destination_folder: str, the folder in which to download tut (will create `DCASE2018-task5-dev` folder in it)

    Returns:
        str, path of TUT extracted database
    """
    logger = create_logger(
        __name__ + "/" + inspect.currentframe().f_code.co_name,
        terminal_level=logging.INFO,
    )
    archive_folder = os.path.join(
        "tmp", "zip_extracted_sins"
    )  # not using tempdir because too big files for some /tmp folders
    create_folder(archive_folder)

    zip_file_url_meta = f"https://zenodo.org/record/1247102/files/DCASE2018-task5-dev.meta.zip?download=1"
    fpath_meta = os.path.join(archive_folder, "DCASE2018-task5-dev.meta.zip")
    download_file(zip_file_url_meta, fpath_meta)
    shutil.unpack_archive(fpath_meta, destination_folder)
    os.remove(fpath_meta)

    for i in range(1, 24):
        logger.info(f"SINS downloading zip {i} / 23 ...")
        zip_file_url = f"https://zenodo.org/record/1247102/files/DCASE2018-task5-dev.audio.{i}.zip?download=1"
        fpath = os.path.join(archive_folder, f"DCASE2018-task5-dev.audio.{i}.zip")
        download_file(zip_file_url, fpath)
        shutil.unpack_archive(fpath, destination_folder)
        os.remove(fpath)

    shutil.rmtree(archive_folder)
    return os.path.join(destination_folder, "DCASE2018-task5-dev")


def filter_sins(
    sins_basedir="DCASE2018-task5-dev",
    destination_folder=os.path.join("background", "sins"),
    classes_kept=["other"],
    rm_original_sins=True,
):
    """ Fonction to copy a only some classes of sins into a new folder.
    Args:
        sins_basedir: str, the path where SINS database has been extracted
        destination_folder: str, the path where to store the filtered SINS version
            (in desed: basedir_soundbank/audio/train/background/sins)
        classes_kept: list, list of classes to keep in the origingal SINS database to use as backgrounds
        rm_original_sins: bool, whether to keep the original database too or not.

    Returns:
    """
    logger = create_logger(
        __name__ + "/" + inspect.currentframe().f_code.co_name,
        terminal_level=logging.INFO,
    )
    logger.info("Filtering SINS...")
    create_folder(destination_folder)

    df = pd.read_csv(os.path.join(sins_basedir, "meta.txt"), sep="\t", header=None)
    df["filename"] = df[0].apply(lambda x: os.path.basename(x))
    df = df[df[1].isin(classes_kept)]

    _copy_files_kept(
        df, input_dir=os.path.join(sins_basedir, "audio"), output_dir=destination_folder
    )

    if rm_original_sins:
        shutil.rmtree(sins_basedir)


def download_tut(destination_folder):
    """ Download 'TUT Acoustic scenes 2017, Development dataset', see: https://zenodo.org/record/400515
    Args:
        destination_folder: str, the folder in which to download tut (will create `TUT-acoustic-scenes-2017-development`
            folder in it)

    Returns:
        str, path of extracted TUT database
    """
    logger = create_logger(
        __name__ + "/" + inspect.currentframe().f_code.co_name,
        terminal_level=logging.INFO,
    )
    archive_folder = os.path.join(
        "tmp", "zip_extracted_tut"
    )  # not using tempdir because too big files for some /tmp folders
    create_folder(archive_folder)
    zip_meta_tut = f"https://zenodo.org/record/400515/files/TUT-acoustic-scenes-2017-development.meta.zip?download=1"
    fpath_meta = os.path.join(
        archive_folder, "TUT-acoustic-scenes-2017-development.meta.zip"
    )
    download_file(zip_meta_tut, fpath_meta)
    shutil.unpack_archive(fpath_meta, destination_folder)

    for i in range(1, 11):
        logger.info(f"TUT (scenes-2017-dev) downloading zip {i} / 10 ...")
        zip_file_url = (
            f"https://zenodo.org/record/400515/files/"
            f"TUT-acoustic-scenes-2017-development.audio.{i}.zip?download=1"
        )
        fpath = os.path.join(
            archive_folder, f"TUT-acoustic-scenes-2017-development.audio.{i}.zip"
        )
        download_file(zip_file_url, fpath)
        shutil.unpack_archive(fpath, destination_folder)
        os.remove(fpath)

    shutil.rmtree(archive_folder)
    return os.path.join(destination_folder, "TUT-acoustic-scenes-2017-development")


def filter_tut(
    tut_basedir="TUT-acoustic-scenes-2017-development",
    destination_folder=os.path.join("background", "tut-scenes-2017-dev"),
    classes_kept=["home", "office", "library"],
    rm_original_tut=True,
):
    """ Fonction to copy a only some classes of TUT into a new folder.
    Args:
        tut_basedir: str, the path where TUT database has been extracted
        destination_folder: str, the path where to store the filtered TUT version
            (in desed: basedir_soundbank/audio/train/background/tut-scenes-2017-dev)
        classes_kept: list, list of classes to be kept from TUT.
        rm_original_tut: bool, whether to keep the original database too or not.

    Returns:
    """
    logger = create_logger(
        __name__ + "/" + inspect.currentframe().f_code.co_name,
        terminal_level=logging.INFO,
    )
    logger.info("Filtering SINS...")
    create_folder(destination_folder)

    df = pd.read_csv(os.path.join(tut_basedir, "meta.txt"), sep="\t", header=None)
    df["filename"] = df[0].apply(lambda x: os.path.basename(x))
    df = df[df[1].isin(classes_kept)]

    _copy_files_kept(df, os.path.join(tut_basedir, "audio"), destination_folder)

    if rm_original_tut:
        shutil.rmtree(tut_basedir)


def get_backgrounds_train(basedir_soundbank, sins=True, tut=False, keep_original=False):
    """ Download the background files of the DESED soundbank.
    (These files were not included in the Zenodo because of redistributing license issues.)
    Args:
        basedir_soundbank: str, the base folder of DESED dataset.
        sins: bool, download part of sins database as backgrounds.
        tut: bool, download part of TUT database as backgrounds.
        keep_original: bool, whether to keep the original databases too (sins, tut)

    Returns:
    """
    destination_folder = os.path.join(basedir_soundbank, "audio", "train", "soundbank")
    if sins:
        sins_path = download_sins(destination_folder)
        filter_sins(
            sins_path,
            destination_folder=os.path.join(destination_folder, "background", "sins"),
            rm_original_sins=not keep_original,
        )

    if tut:
        tut_path = download_tut(destination_folder)
        filter_tut(
            tut_path,
            destination_folder=os.path.join(
                destination_folder, "background", "tut-scenes-2017-dev"
            ),
            rm_original_tut=not keep_original,
        )


def download_zenodo_soundbank(destination_folder):
    """ Be careful, there are only the foregrounds of training.
    Args:
        destination_folder: str, the path of the root of the soundbank (will create the structure inside)

    Returns:
    """
    zip_meta_tut = "https://zenodo.org/record/4307908/files/DESED_synth_soundbank.tar.gz?download=1"
    archive_folder = os.path.join(
        "tmp", "zip_extracted_sb"
    )  # not using tempdir because too big files for some /tmp folders
    create_folder(archive_folder)
    fname = os.path.join(archive_folder, "DESED_synth_soundbank.tar.gz")
    download_file(zip_meta_tut, fname)
    shutil.unpack_archive(fname, destination_folder)
    os.remove(fname)


def make_validation_sb(basedir):
    """ Split the training into training and validation (pre-made, 90%/10%) of backgrounds and foregrounds
    Args:
        basedir: str, path where the soundbank is downloaded (parent folder of "audio")

    Returns:

    """
    fname_valid = (
        "https://zenodo.org/record/4307908/files/soundbank_validation.tsv?download=1"
    )
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


def download_soundbank(
    basedir,
    sins_bg=True,
    tut_bg=False,
    split_train_valid=True,
    keep_original_sins_tut=False,
):
    """ Download the soundbank.
    Args:
        basedir: str, the dirname where to store the soundbank.
        sins_bg: bool, whether to download SINS backgrounds (default in 2019-2020).
        tut_bg: bool, whether to download 'TUT Acoustic scenes 2017, Development dataset' backgrounds or not
            (appeared in DCASE task 4 2020).
        split_train_valid: bool, whether to split the training foregrounds and backgrounds in training and validation
            (90%/10%). Default since DCASE task 4 2020.
        keep_original_sins_tut: bool, whether to keep the original versions of TUT and SINS.

    Returns:

    """
    print("downloading soundbank (foregrounds)...")
    download_zenodo_soundbank(basedir)
    print("Downloading backgrounds...")
    get_backgrounds_train(
        basedir, sins_bg, tut_bg, keep_original=keep_original_sins_tut
    )
    if split_train_valid:
        print("Splitting soundbank train into train and validation (90%/10%)...")
        make_validation_sb(basedir)
