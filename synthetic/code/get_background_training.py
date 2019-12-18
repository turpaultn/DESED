# -*- coding: utf-8 -*-
#########################################################################
# Initial software
# Copyright Nicolas Turpault, Romain Serizel, Justin Salamon, Ankit Parag Shah, 2019, v1.0
# This software is distributed under the terms of the License MIT
#########################################################################
import time
import argparse
import pandas as pd
import glob
import os
import shutil
import logging

import requests
import zipfile
import io
from pprint import pformat

from desed.utils import create_folder
from desed.Logger import create_logger

if __name__ == '__main__':
    LOG = create_logger("DESED", "Desed.log", terminal_level=logging.INFO, file_level=logging.INFO)
    t = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--keep-sins', action="store_true", default=False)
    parser.add_argument('--basedir', type=str, default="..")
    args = parser.parse_args()
    pformat(vars(args))

    basedir = args.basedir

    zip_file_url_meta = "https://zenodo.org/record/1247102/files/DCASE2018-task5-dev.meta.zip?download=1"
    destination_folder = os.path.join(basedir, "audio", "train", "soundbank")
    r = requests.get(zip_file_url_meta)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(destination_folder)
    
    extract_path = os.path.join(destination_folder, "DCASE2018-task5-dev")
    final_path = os.path.join(destination_folder, "background", "sins")
    create_folder(final_path)
    df = pd.read_csv(os.path.join(extract_path, "meta.txt"), sep="\t", header=None)
    df["filename"] = df[0].apply(lambda x: os.path.basename(x))
    df = df[df[1] == "other"]
    
    for i in range(1, 24):
        LOG.info(f"downloading zip {i} / 23 ...")
        # Download the first zip, and keep only other
        zip_file_url = f"https://zenodo.org/record/1247102/files/DCASE2018-task5-dev.audio.{i}.zip?download=1"
        r = requests.get(zip_file_url)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(destination_folder)
    
        df_files = pd.DataFrame(glob.glob(os.path.join(extract_path, "audio", "*")), 
                                          columns=["filename"])
        df_files["filename"] = df_files.filename.apply(lambda x: os.path.basename(x))
    
        merged = df.merge(df_files, on='filename')
        merged.apply(lambda x: shutil.copy(os.path.join(extract_path, x[0]), os.path.join(final_path, x["filename"])), 
                     axis=1)
    
        if not args.keep_sins:
            shutil.rmtree(os.path.join(extract_path, "audio"))

    if not args.keep_sins:
        shutil.rmtree(extract_path)
    LOG.info(f"time of the program: {time.time() - t}")
