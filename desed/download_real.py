import functools
import glob
import os
import shutil
from contextlib import closing
from multiprocessing import Pool

import pandas as pd
import youtube_dl
from dcase_util.containers import AudioContainer
from tqdm import tqdm
from youtube_dl import DownloadError
from youtube_dl.utils import ExtractorError

from .Logger import create_logger


TMP_FOLDER = "tmp/"


def download_file(result_dir, filename):
    """ download a file from youtube given an audioSet filename. (It takes only a part of the file thanks to
    information provided in the filename)

    Parameters
    ----------

    result_dir : str, result directory which will contain the downloaded file

    filename : str, AudioSet filename to download

    Return
    ------

    list : list, Empty list if the file is downloaded, otherwise contains the filename and the error associated

    """
    LOG = create_logger(__name__, "Desed_real.log")
    tmp_filename = ""
    query_id = filename[1:12]
    segment_start = filename[13:-4].split('_')[0]
    segment_end = filename[13:-4].split('_')[1]
    audio_container = AudioContainer()

    # Define download parameters
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': TMP_FOLDER+'%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'prefer_ffmpeg': True,
        'logger': MyLogger(),
        'audioformat': 'wav'
    }

    try:
        # Download file
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(
                'https://www.youtube.com/watch?v={query_id}'.format(query_id=query_id), download=True)

        audio_formats = [f for f in meta["formats"] if f.get('vcodec') == 'none']

        if audio_formats is []:
            return [filename, "no audio format available"]

        # get the best audio format
        best_audio_format = audio_formats[-1]

        tmp_filename = TMP_FOLDER + query_id + "." + best_audio_format["ext"]

        audio_container.load(filename=tmp_filename, fs=44100, res_type='kaiser_best',
                             start=float(segment_start), stop=float(segment_end))

        # Save segmented audio
        audio_container.filename = filename
        audio_container.detect_file_format()
        audio_container.save(filename=os.path.join(result_dir, filename))

        #Remove temporary file
        os.remove(tmp_filename)
        return []

    except (KeyboardInterrupt, SystemExit):
        # Remove temporary files and current audio file.
        for fpath in glob.glob(TMP_FOLDER + query_id + "*"):
            os.remove(fpath)
        raise

    # youtube-dl error, file often removed
    except (ExtractorError, DownloadError) as e:
        if os.path.exists(tmp_filename):
            os.remove(tmp_filename)

        return [filename, str(e)]

    # multiprocessing can give this error
    except IndexError as e:
        if os.path.exists(tmp_filename):
            os.remove(tmp_filename)
        LOG.info(filename)
        LOG.info(str(e))
        return [filename, "Index Error"]


def download(filenames, result_dir, n_jobs=1, chunk_size=10, base_dir_missing_files=".."):
    """ download files in parallel from youtube given a csv file listing files to download. It also stores not downloaded
    files with their associated error in "missing_files_[csv_file].csv"

       Parameters
       ----------
       filenames : pandas Series, named "filename" listing AudioSet filenames to download

       result_dir : str, result directory which will contain downloaded files

       n_jobs : int, number of download to execute in parallel

       chunk_size : int, number of files to download before updating the progress bar. Bigger it is, faster it goes
       because data is filled in memory but progress bar only updates after a chunk is finished.

       Return
       ------

       missing_files : pandas.DataFrame, files not downloaded whith associated error.

       """

    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    if not os.path.exists(TMP_FOLDER):
        os.mkdir(TMP_FOLDER)
    # Remove already existing files in folder
    existing_files = [os.path.basename(fpath) for fpath in glob.glob(os.path.join(result_dir, "*"))]
    filenames = filenames[~filenames.isin(existing_files)]

    p = None
    non_existing_files = []
    try:
        if n_jobs == 1:
            for filename in tqdm(filenames):
                non_existing_files.append(download_file(result_dir, filename))
        # multiprocessing
        else:
            with closing(Pool(n_jobs)) as p:
                # Put result_dir as a constant variable with result_dir in download_file
                download_file_alias = functools.partial(download_file, result_dir)

                for val in tqdm(p.imap_unordered(download_file_alias, filenames, chunk_size), total=len(filenames)):
                    non_existing_files.append(val)

        # Store files which gave error
        missing_files = pd.DataFrame(non_existing_files).dropna()
        if not missing_files.empty:
            base_dir_missing_files = os.path.join(base_dir_missing_files, "missing_files")
            if not os.path.exists(base_dir_missing_files):
                os.makedirs(base_dir_missing_files)

            missing_files.columns = ["filename", "error"]
            missing_files.to_csv(os.path.join(base_dir_missing_files,
                                              "missing_files_" + result_dir.split('/')[-1] + ".csv"),
                                 index=False, sep="\t")

    except KeyboardInterrupt:
        if p is not None:
            p.terminate()
        raise KeyboardInterrupt

    if os.path.exists(TMP_FOLDER):
        shutil.rmtree(TMP_FOLDER)

    return missing_files


# Needed to not print warning which cause breaks in the progress bar.
class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass
