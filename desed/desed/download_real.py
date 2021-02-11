# -*- coding: utf-8 -*-
import functools
import glob
import inspect
import os
import shutil
import warnings
from contextlib import closing
from multiprocessing import Pool

import pandas as pd
import youtube_dl
from dcase_util.containers import AudioContainer
from tqdm import tqdm
from youtube_dl.utils import ExtractorError, DownloadError

from .logger import create_logger, DesedWarning
from .utils import create_folder


TMP_FOLDER = "tmp/"


def download_unique_file(filename, result_dir, platform="youtube"):
    """ download a file from youtube given an audioSet filename. (It takes only a part of the file thanks to
    information provided in the filename)
    Args:
        filename : str, AudioSet filename to download
        result_dir : str, result directory which will contain the downloaded file
        platform: str, name of the platform, here youtube or vimeo

    Return:
        list, Empty list if the file is downloaded, otherwise contains the filename and the error associated

    """
    logger = create_logger(__name__ + "/" + inspect.currentframe().f_code.co_name)
    tmp_filename = ""
    fname_no_ext = os.path.splitext(filename)[0]
    segment_start = fname_no_ext.split("_")[-2]
    segment_end = fname_no_ext.split("_")[-1]
    audio_container = AudioContainer()

    # Define download parameters
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": TMP_FOLDER + "%(id)s.%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "prefer_ffmpeg": True,
        "logger": MyLogger(),
        "audioformat": "wav",
    }

    if platform.lower() == "youtube":
        query_id = filename[1:12]  # Remove the Y in front of the file.
        baseurl = "https://www.youtube.com/watch?v="
    elif platform.lower() == "vimeo":
        query_id = filename.split("_")[0]
        baseurl = "https://vimeo.com/"
    else:
        raise NotImplementedError("platform can only be vimeo or youtube")

    if not os.path.isfile(os.path.join(result_dir, filename)):
        try:
            logger.debug(filename)
            # Download file
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                meta = ydl.extract_info(f"{baseurl}{query_id}", download=True)

            audio_formats = [f for f in meta["formats"] if f.get("vcodec") == "none"]
            if audio_formats is []:
                return [filename, "no audio format available"]
            # get the best audio format
            best_audio_format = audio_formats[-1]

            tmp_filename = TMP_FOLDER + query_id + "." + best_audio_format["ext"]
            audio_container.load(
                filename=tmp_filename,
                fs=44100,
                res_type="kaiser_best",
                start=float(segment_start),
                stop=float(segment_end),
                auto_trimming=True,
            )

            # Save segmented audio
            audio_container.filename = filename
            audio_container.detect_file_format()
            audio_container.save(filename=os.path.join(result_dir, filename))

            # Remove temporary file
            os.remove(tmp_filename)
            return []

        except (KeyboardInterrupt, SystemExit):
            # Remove temporary files and current audio file.
            for fpath in glob.glob(TMP_FOLDER + query_id + "*"):
                os.remove(fpath)
            raise

        # youtube-dl error, file often removed, IO Error is for AudioContainer error if length of file is different.
        except (ExtractorError, DownloadError, IOError) as e:
            if os.path.exists(tmp_filename):
                os.remove(tmp_filename)

            return [filename, str(e)]

        # multiprocessing can give this error
        except (IndexError, ValueError) as e:
            if os.path.exists(tmp_filename):
                os.remove(tmp_filename)
            logger.info(filename)
            logger.info(str(e))
            return [filename, "Index Error"]
    else:
        logger.debug(filename, "exists, skipping")
        return []


def download(
    filenames,
    result_dir,
    n_jobs=1,
    chunk_size=10,
    base_dir_missing_files="..",
    platform="youtube",
):
    warnings.warn("Depreciated, use 'download_real' instead")
    return download_real(
        filenames, result_dir, n_jobs, chunk_size, base_dir_missing_files, platform
    )


def download_real(
    filenames,
    result_dir,
    n_jobs=1,
    chunk_size=10,
    base_dir_missing_files="..",
    platform="youtube",
):
    """ download files in parallel from youtube given a tsv file listing files to download.
    It also stores not downloaded files with their associated error in "missing_files_[tsv_file].tsv"

       Args:
           filenames : pandas Series, named "filename" listing AudioSet filenames to download
           result_dir : str, result directory which will contain downloaded files
           n_jobs : int, number of download to execute in parallel
           chunk_size : int, number of files to download before updating the progress bar. Bigger it is, faster it goes
                because data is filled in memory but progress bar only updates after a chunk is finished.
           base_dir_missing_files: str, path of the folder where to save missing files
           platform: str, the platform the filenames are coming from "youtube" or "vimeo"

       Returns:
           missing_files : pandas.DataFrame, files not downloaded whith associated error.

       """
    create_folder(result_dir)
    create_folder(TMP_FOLDER)

    p = None
    files_error = []
    try:
        if n_jobs == 1:
            for filename in tqdm(filenames):
                files_error.append(download_unique_file(filename, result_dir, platform))
        # multiprocessing
        else:
            with closing(Pool(n_jobs)) as p:
                # Put result_dir and platform as constants variable with result_dir in download_file
                download_file_alias = functools.partial(
                    download_unique_file, result_dir=result_dir, platform=platform
                )

                for val in tqdm(
                    p.imap_unordered(download_file_alias, filenames, chunk_size),
                    total=len(filenames),
                ):
                    files_error.append(val)

        # Store files which gave error
        missing_files = pd.DataFrame(files_error).dropna()
        if not missing_files.empty:
            base_dir_missing_files = os.path.join(
                base_dir_missing_files, "missing_files"
            )
            create_folder(base_dir_missing_files)

            # Save missing_files to be able to ask them
            missing_files.columns = ["filename", "error"]
            set_name = os.path.basename(result_dir)
            missing_files.to_csv(
                os.path.join(
                    base_dir_missing_files, "missing_files_" + set_name + ".tsv"
                ),
                index=False,
                sep="\t",
            )
            warnings.warn(
                f"There are missing files at {base_dir_missing_files}, \n"
                f"see info on https://github.com/turpaultn/desed#11-download on how to get them",
                DesedWarning,
            )

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
