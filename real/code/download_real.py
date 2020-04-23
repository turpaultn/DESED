# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import argparse
import os
from pprint import pformat

import pandas as pd
from desed.logger import create_logger
from desed.download_real import download


LOG = create_logger("tripletEmbedding", "Triplet.log")


def download_from_csv(csv_path, result_dir):
    LOG.info(f"downloading data from: {csv_path}")
    # read metadata file and get only one filename once
    df = pd.read_csv(csv_path, header=0, sep='\t')
    filenames_test = df["filename"].drop_duplicates()
    download(filenames_test, result_dir, n_jobs=N_JOBS, chunk_size=CHUNK_SIZE,
             base_dir_missing_files=base_missing_files_folder)
    LOG.info("###### DONE #######")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset_folder', type=str, default="..")
    parser.add_argument('-m', '--missing_files_folder', type=str, default="..")
    args = parser.parse_args()
    pformat(vars(args))
    # To be changed for your root folder if needed (if dcase2019 used)
    base_missing_files_folder = ".."
    dataset_folder = args.dataset_folder

    LOG.info("Download_data")
    LOG.info("\n\nOnce database is downloaded, do not forget to check your missing_files\n\n")

    LOG.info("You can change N_JOBS and CHUNK_SIZE to increase the download with more processes.")
    # Modify it with the number of process you want, but be careful, youtube can block you if you put too many.
    N_JOBS = 3

    # Only useful when multiprocessing,
    # if chunk_size is high, download is faster. Be careful, progress bar only update after each chunk.
    CHUNK_SIZE = 10

    download_from_csv(
        os.path.join(dataset_folder, "metadata", "validation", "validation.tsv"),
        os.path.join(dataset_folder, "audio", "validation")
    )

    download_from_csv(
        os.path.join(dataset_folder, "metadata", "train", "weak.tsv"),
        os.path.join(dataset_folder, "audio", "train", "weak")
    )

    download_from_csv(
        os.path.join(dataset_folder, "metadata", "train", "unlabel_in_domain.tsv"),
        os.path.join(dataset_folder, "audio", "train", "unlabel_in_domain")
    )
