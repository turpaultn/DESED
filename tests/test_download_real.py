import os
import pandas as pd
import pytest

from desed.download_real import download

# Problem with this test, if I exchange the single process and multiprocessing, it does not work
# It gives: "Fatal Python error: Aborted"
@pytest.mark.parametrize("n_jobs,chunk_size,n_download", [
    (3, 3, 12),
    (1, 3, 15),
])
def test_download_multiprocessing(n_jobs, chunk_size, n_download):
    test = os.path.join("material", "validation.tsv")
    result_dir = os.path.join("generated", "audio", "validation")
    df = pd.read_csv(test, header=0, sep='\t')

    filenames_test = df["filename"].drop_duplicates()[:n_download]

    download(filenames_test, result_dir, n_jobs=n_jobs, chunk_size=chunk_size,
             base_dir_missing_files=os.path.join("generated", "missing_files"))
