import glob
import inspect
import io
import logging
import os
import shutil
import zipfile

import pandas as pd
import requests
from .logger import create_logger
from .utils import create_folder


def extract_zip(url_path, output_folder):
    r = requests.get(url_path)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(output_folder)


def copy_files_kept(meta_df, list_sins_files, input_dir, output_dir):
    df_files = pd.DataFrame(list_sins_files, columns=["filename"])
    df_files["filename"] = df_files.filename.apply(lambda x: os.path.basename(x))

    merged = meta_df.merge(df_files, on='filename')
    merged.apply(
        lambda x: shutil.copy(os.path.join(input_dir, x[0]), os.path.join(output_dir, x["filename"])),
        axis=1)


def get_sins(destination_folder, keep_sins=False):
    logger = create_logger(__name__ + "/" + inspect.currentframe().f_code.co_name, terminal_level=logging.INFO)
    zip_file_url_meta = "https://zenodo.org/record/1247102/files/DCASE2018-task5-dev.meta.zip?download=1"
    extract_zip(zip_file_url_meta, destination_folder)

    extracted_sins_path = os.path.join(destination_folder, "DCASE2018-task5-dev")
    final_sins_path = os.path.join(destination_folder, "background", "sins")
    create_folder(final_sins_path)

    df = pd.read_csv(os.path.join(extracted_sins_path, "meta.txt"), sep="\t", header=None)
    df["filename"] = df[0].apply(lambda x: os.path.basename(x))
    df = df[df[1] == "other"]

    for i in range(1, 24):
        logger.info(f"SINS downloading zip {i} / 23 ...")
        # Download the first zip, and keep only other
        zip_file_url = f"https://zenodo.org/record/1247102/files/DCASE2018-task5-dev.audio.{i}.zip?download=1"
        extract_zip(zip_file_url, destination_folder)

        list_files_i = glob.glob(os.path.join(extracted_sins_path, "audio", "*"))
        copy_files_kept(df, list_files_i, extracted_sins_path, final_sins_path)

        if not keep_sins:
            # Save disk space if limited
            shutil.rmtree(os.path.join(extracted_sins_path, "audio"))

    if not keep_sins:
        shutil.rmtree(extracted_sins_path)


def get_tut(destination_folder, keep_original):
    logger = create_logger(__name__ + "/" + inspect.currentframe().f_code.co_name, terminal_level=logging.INFO)
    zip_meta_tut = "https://zenodo.org/record/400515/files/TUT-acoustic-scenes-2017-development.meta.zip?download=1"
    extract_zip(zip_meta_tut, destination_folder)

    extracted_tut_path = os.path.join(destination_folder, "TUT-acoustic-scenes-2017-development")
    final_tut_path = os.path.join(destination_folder, "background", "tut-scenes-2017-dev")
    create_folder(final_tut_path)

    df = pd.read_csv(os.path.join(extracted_tut_path, "meta.txt"), sep="\t", header=None)
    df["filename"] = df[0].apply(lambda x: os.path.basename(x))
    df = df[df[1].isin(["home", "office", "library"])]

    for i in range(1, 10):
        logger.info(f"TUT (scenes-2017-dev) downloading zip {i} / 10 ...")
        zip_file_url = f"https://zenodo.org/record/400515/files/" \
            f"TUT-acoustic-scenes-2017-development.audio.{i}.zip?download=1"
        extract_zip(zip_file_url, destination_folder)

        list_files_i = glob.glob(os.path.join(extracted_tut_path, "audio", "*"))
        copy_files_kept(df, list_files_i, extracted_tut_path, final_tut_path)
    # shutil.move(os.path.join(destination_folder, "TUT-acoustic-scenes-2017-development", "audio"),
    #             final_tut_path)

    if not keep_original:
        os.rmdir(extracted_tut_path)


def get_background_training(basedir, sins=True, tut=False, keep_original=False):
    destination_folder = os.path.join(basedir, "audio", "train", "soundbank")
    if sins:
        get_sins(destination_folder, keep_original)

    if tut:
        get_tut(destination_folder, keep_original)
