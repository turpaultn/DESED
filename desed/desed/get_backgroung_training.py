import glob
import io
import logging
import os
import shutil
import zipfile

import pandas as pd
import requests
from .logger import create_logger
from .utils import create_folder


def get_background_training(basedir, sins=True, tut=False, keep_sins=False):
    logger = create_logger("DESED", terminal_level=logging.INFO)
    zip_file_url_meta = "https://zenodo.org/record/1247102/files/DCASE2018-task5-dev.meta.zip?download=1"
    destination_folder = os.path.join(basedir, "audio", "train", "soundbank")

    if sins:
        r = requests.get(zip_file_url_meta)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(destination_folder)

        extract_path = os.path.join(destination_folder, "DCASE2018-task5-dev")
        final_sins_path = os.path.join(destination_folder, "background", "sins")
        create_folder(final_sins_path)
        df = pd.read_csv(os.path.join(extract_path, "meta.txt"), sep="\t", header=None)
        df["filename"] = df[0].apply(lambda x: os.path.basename(x))
        df = df[df[1] == "other"]

        for i in range(1, 24):
            logger.info(f"downloading zip {i} / 23 ...")
            # Download the first zip, and keep only other
            zip_file_url = f"https://zenodo.org/record/1247102/files/DCASE2018-task5-dev.audio.{i}.zip?download=1"
            r = requests.get(zip_file_url)
            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall(destination_folder)

            df_files = pd.DataFrame(glob.glob(os.path.join(extract_path, "audio", "*")),
                                    columns=["filename"])
            df_files["filename"] = df_files.filename.apply(lambda x: os.path.basename(x))

            merged = df.merge(df_files, on='filename')
            merged.apply(
                lambda x: shutil.copy(os.path.join(extract_path, x[0]), os.path.join(final_sins_path, x["filename"])),
                axis=1)

            if not keep_sins:
                shutil.rmtree(os.path.join(extract_path, "audio"))

        if not keep_sins:
            shutil.rmtree(extract_path)

    if tut:
        for i in range(1, 10):
            logger.info(f"downloading zip {i} / 10 ...")
            # Download the first zip, and keep only other
            zip_file_url = f"https://zenodo.org/record/400515/files/" \
                f"TUT-acoustic-scenes-2017-development.audio.{i}.zip?download=1"
            r = requests.get(zip_file_url)
            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall(destination_folder)
        final_tut_path = os.path.join(destination_folder, "background", "tut-scenes-2017-dev")

        shutil.move(os.path.join(destination_folder, "TUT-acoustic-scenes-2017-development", "audio"),
                    final_tut_path)

        if not keep_sins:
            # Should be empty
            os.rmdir(os.path.join(destination_folder, "TUT-acoustic-scenes-2017-development"))
