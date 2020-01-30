# -*- coding: utf-8 -*-
#########################################################################
# Initial software
# Copyright Nicolas Turpault, Romain Serizel, Justin Salamon, Ankit Parag Shah, 2019, v1.0
# This software is distributed under the terms of the License MIT
#########################################################################


from __future__ import print_function, absolute_import

import os
import pandas as pd
from desed.Logger import create_logger
from desed.download_real import download


if __name__ == "__main__":
    LOG = create_logger("tripletEmbedding", "Triplet.log")
    # To be changed for your root folder if needed (if dcase2019 used)
    base_missing_files_folder = ".."
    dataset_folder = ".."

    LOG.info("Download_data")
    LOG.info("\n\nOnce database is downloaded, do not forget to check your missing_files\n\n")

    LOG.info("You can change N_JOBS and CHUNK_SIZE to increase the download with more processes.")
    # Modify it with the number of process you want, but be careful, youtube can block you if you put too many.
    N_JOBS = 3

    # Only useful when multiprocessing,
    # if chunk_size is high, download is faster. Be careful, progress bar only update after each chunk.
    CHUNK_SIZE = 10

    LOG.info("Validation data")
    test = os.path.join(dataset_folder, "metadata", "validation", "validation.tsv")
    result_dir = os.path.join(dataset_folder, "audio", "validation")
    # read metadata file and get only one filename once
    df = pd.read_csv(test, header=0, sep='\t')
    filenames_test = df["filename"].drop_duplicates()
    download(filenames_test, result_dir, n_jobs=N_JOBS, chunk_size=CHUNK_SIZE,
             base_dir_missing_files=base_missing_files_folder)

    LOG.info("Train, weak data")
    train_weak = os.path.join(dataset_folder, "metadata", "train", "weak.tsv")
    result_dir = os.path.join(dataset_folder, "audio", "train", "weak")
    # read metadata file and get only one filename once
    df = pd.read_csv(train_weak, header=0, sep='\t')
    filenames_weak = df["filename"].drop_duplicates()
    download(filenames_weak, result_dir, n_jobs=N_JOBS, chunk_size=CHUNK_SIZE,
             base_dir_missing_files=base_missing_files_folder)

    LOG.info("Train, unlabel in domain data")
    train_unlabel_in_domain = os.path.join(dataset_folder, "metadata", "train", "unlabel_in_domain.tsv")
    result_dir = os.path.join(dataset_folder, "audio", "train", "unlabel_in_domain")
    # read metadata file and get only one filename once
    df = pd.read_csv(train_unlabel_in_domain, header=0, sep='\t')
    filenames_unlabel_in_domain = df["filename"].drop_duplicates()
    download(filenames_unlabel_in_domain, result_dir, n_jobs=N_JOBS, chunk_size=CHUNK_SIZE,
             base_dir_missing_files=base_missing_files_folder)

    LOG.info("###### DONE #######")
