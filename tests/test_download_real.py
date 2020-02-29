import os
import pandas as pd
import pytest

from desed.download_real import download, download_file

absolute_dir_path = os.path.abspath(os.path.dirname(__file__))
result_dir = os.path.join(absolute_dir_path, "generated", "audio", "validation")


@pytest.fixture()
def rm_folder():
    os.removedirs(os.path.join(absolute_dir_path, "generated"))


# Problem with this test, if I exchange the single process and multiprocessing, it does not work
# It gives: "Fatal Python error: Aborted"
@pytest.mark.parametrize("n_jobs,chunk_size,n_download", [
    (3, 3, 12),
    (1, 3, 15),
])
def test_download_multiprocessing(n_jobs, chunk_size, n_download):
    test = os.path.join(absolute_dir_path, "material", "validation.tsv")
    df = pd.read_csv(test, header=0, sep='\t')

    filenames_test = df["filename"].drop_duplicates()[:n_download]

    download(filenames_test, result_dir, n_jobs=n_jobs, chunk_size=chunk_size,
             base_dir_missing_files=os.path.join(absolute_dir_path, "generated", "missing_files"))


def test_download_file():
    fname = "Y00pbt6aJV8Y_350.000_360.000.wav"
    res = download_file(fname, result_dir)
    # Cannot check if download succeeds since depending country sometimes it does not work


def test_download_file_fail():
    errors = ['\x1b[0;31mERROR:\x1b[0m This video is unavailable.\nSorry about that.',
              "ERROR: This video is unavailable.\nSorry about that."]
    fname = "Y4U2-ZMKWgD0_380.000_390.000.wav"
    res = download_file(fname, result_dir)
    print(res)
    assert res[0] == fname
    assert res[1] in errors , "Download did not fail with the right exception"

