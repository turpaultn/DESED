import os
import shutil

import pandas as pd
import pytest

from desed.download import _download_audioset_file, download_audioset_files

absolute_dir_path = os.path.abspath(os.path.dirname(__file__))
result_dir = os.path.join(absolute_dir_path, "generated", "audio", "validation")


@pytest.fixture()
def rm_folder():
    shutil.rmtree(os.path.join(absolute_dir_path, "generated"))


# Problem with this test, if I exchange the single process and multiprocessing, it does not work
# It gives: "Fatal Python error: Aborted"
@pytest.mark.parametrize("n_jobs,chunk_size,n_download", [(3, 3, 10), (1, 3, 6),])
def test_download_multiprocessing(n_jobs, chunk_size, n_download):
    test = os.path.join(absolute_dir_path, "material", "validation.tsv")
    df = pd.read_csv(test, header=0, sep="\t")

    filenames_test = df["filename"].drop_duplicates()[:n_download]

    download_audioset_files(
        filenames_test,
        result_dir,
        n_jobs=n_jobs,
        chunk_size=chunk_size,
        missing_files_tsv=os.path.join(
            absolute_dir_path, "generated", "missing_files", "missing_files_test.csv"
        ),
    )


def test_download_file():
    fname = "173180999_0_10.wav"
    res = _download_audioset_file(fname, result_dir, platform="vimeo")
    # Cannot check if download succeeds since depending country sometimes it does not work


def test_download_file_fail():
    errors = [
        "\x1b[0;31mERROR:\x1b[0m This video is unavailable.\nSorry about that.",
        "ERROR: This video is unavailable.\nSorry about that.",
    ]
    fname = "Y4U2-ZMKWgD0_380.000_390.000.wav"
    res = _download_audioset_file(fname, result_dir)
    print(res)
    assert res[0] == fname
    # assert res[1] in errors , "Download did not fail with the right exception"
