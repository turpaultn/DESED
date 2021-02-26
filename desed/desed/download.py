import functools
import glob
import inspect
import logging
import os
import shutil
import subprocess
import warnings

from contextlib import closing
from multiprocessing import Pool
import pandas as pd
import youtube_dl

from dcase_util.containers import AudioContainer
from tqdm import tqdm
from youtube_dl import DownloadError
from youtube_dl.utils import ExtractorError

from .logger import create_logger, DesedWarning
from .utils import create_folder, download_file_from_url, download_and_unpack_archive


class LoggerYtdlWarnings(object):
    """ Class needed to avoid printing warnings from youtube_dl which cause breaks in the progress bar."""
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


def download_audioset_file(filename, result_dir, platform="youtube", tmp_folder="tmp"):
    """ download a file from youtube given an audioSet filename. (It takes only a part of the file thanks to
    information provided in the filename)
    Args:
        filename : str, AudioSet filename to download.
        result_dir : str, result directory which will contain the downloaded file.
        platform: str, name of the platform, here youtube or vimeo.
        tmp_folder: str, the directory in which to download the temporary file generated by youtube_dl.
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
        "outtmpl": tmp_folder + "%(id)s.%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "prefer_ffmpeg": True,
        "logger": LoggerYtdlWarnings(),
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

            tmp_filename = tmp_folder + query_id + "." + best_audio_format["ext"]
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
            for fpath in glob.glob(tmp_folder + query_id + "*"):
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


def download_audioset_files(
    filenames,
    result_dir,
    n_jobs=1,
    chunk_size=10,
    missing_files_tsv="..",
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
           missing_files_tsv: str, path of the tsv which will contain the files that couldn't have been downloaded.
           platform: str, the platform the filenames are coming from "youtube" or "vimeo"

       Returns:
           missing_files : pandas.DataFrame, files not downloaded whith associated error.

       """
    warnings.filterwarnings("ignore")
    create_folder(result_dir)
    TMP_FOLDER = "tmp/"
    create_folder(TMP_FOLDER)

    p = None
    files_error = []
    try:
        if n_jobs == 1:
            for filename in tqdm(filenames):
                files_error.append(
                    download_audioset_file(filename, result_dir, platform)
                )
        # multiprocessing
        else:
            with closing(Pool(n_jobs)) as p:
                # Put result_dir and platform as constants variable with result_dir in download_file
                download_file_alias = functools.partial(
                    download_audioset_file,
                    result_dir=result_dir,
                    platform=platform,
                    tmp_folder=TMP_FOLDER,
                )

                for val in tqdm(
                    p.imap_unordered(download_file_alias, filenames, chunk_size),
                    total=len(filenames),
                ):
                    files_error.append(val)

        # Store files which gave error
        missing_files = pd.DataFrame(files_error).dropna()
        if not missing_files.empty:
            # Save missing_files to be able to ask them
            missing_files.columns = ["filename", "error"]
            missing_files.to_csv(missing_files_tsv, index=False, sep="\t")
            warnings.warn(
                f"There are missing files at {missing_files_tsv}, \n"
                f"see info on https://github.com/turpaultn/desed on how to get them",
                DesedWarning,
            )

    except KeyboardInterrupt:
        if p is not None:
            p.terminate()
        raise KeyboardInterrupt

    if os.path.exists(TMP_FOLDER):
        shutil.rmtree(TMP_FOLDER)
    warnings.resetwarnings()
    return missing_files


def download_audioset_files_from_csv(
    tsv_path, result_dir, missing_files_tsv=None, n_jobs=3, chunk_size=10
):
    """ Download audioset files from a tsv_path containing a column "filename"

    Args:
        tsv_path: str, the path to the tsv (tab separated values) containing the column 'filename' with the files to
            download
        result_dir: str, the directory in which to download the files.
        missing_files_tsv: str, path of the tsv which will contain the files that couldn't have been downloaded.
        n_jobs : int, number of download to execute in parallel
        chunk_size : int, number of files to download before updating the progress bar. Bigger it is, faster it goes
            because data is filled in memory but progress bar only updates after a chunk is finished.

    Returns:

    """
    logger = create_logger(__name__ + "/" + inspect.currentframe().f_code.co_name)
    logger.info(f"downloading data from: {tsv_path}")
    if missing_files_tsv is None:
        missing_files_tsv = (
            "missing_files" + os.path.basename(os.path.splitext(tsv_path)[0]) + ".tsv"
        )
    # read metadata file and get only one filename once
    df = pd.read_csv(tsv_path, header=0, sep="\t")
    filenames_test = df["filename"].drop_duplicates()

    download_audioset_files(
        filenames_test,
        result_dir,
        n_jobs=n_jobs,
        chunk_size=chunk_size,
        missing_files_tsv=missing_files_tsv,
    )
    logger.info("###### DONE #######")


def download_eval_public(dataset_folder):
    """ Download the public eval part of desed dataset from Zenodo.

    Args:
        dataset_folder: str, the path to the root of the dataset where to download the evaluation files (this folder
            contains audio and metadata folders).

    Returns:

    """
    create_folder(dataset_folder)
    url_public_eval = (
        f"https://zenodo.org/record/4560759/files/DESED_public_eval.tar.gz?download=1"
    )
    download_and_unpack_archive(url_public_eval, dataset_folder)


def download_audioset_data(
    dataset_folder,
    weak=True,
    unlabel_in_domain=True,
    validation=True,
    n_jobs=3,
    chunk_size=10,
):
    """ Download the DESED dataset files from Audioset.

    Args:
        dataset_folder: str, the path to the root of the dataset where to download the evaluation files (this folder
            contains audio and metadata folders).
        weak: bool, whether to download the weak set or not.
        unlabel_in_domain: bool, whether to download the unlabel_in_domain set or not.
        validation: bool, whether to download the validation set or not.
        n_jobs : int, number of download to execute in parallel
        chunk_size : int, number of files to download before updating the progress bar. Bigger it is, faster it goes
            because data is filled in memory but progress bar only updates after a chunk is finished.

    Returns:

    """
    logger = create_logger(__name__ + "/" + inspect.currentframe().f_code.co_name)
    basedir_missing_files = "missing_files"
    create_folder(basedir_missing_files)
    create_folder(dataset_folder)

    # Metadata:
    url_metadata = (
        f"https://zenodo.org/record/4560857/files/audioset_metadata.tar.gz?download=1"
    )
    download_and_unpack_archive(url_metadata, dataset_folder)

    if weak:
        logger.info("Downloading Weakly labeled data...")
        download_audioset_files_from_csv(
            os.path.join(dataset_folder, "metadata", "train", "weak.tsv"),
            os.path.join(dataset_folder, "audio", "train", "weak"),
            missing_files_tsv=os.path.join(
                basedir_missing_files, "missing_files_" + "weak" + ".tsv"
            ),
            n_jobs=n_jobs,
            chunk_size=chunk_size,
        )

    if unlabel_in_domain:
        logger.info("Downloading Unlabeled (in_domain) labeled data...")
        download_audioset_files_from_csv(
            os.path.join(dataset_folder, "metadata", "train", "unlabel_in_domain.tsv"),
            os.path.join(dataset_folder, "audio", "train", "unlabel_in_domain"),
            missing_files_tsv=os.path.join(
                basedir_missing_files, "missing_files_" + "unlabel_in_domain" + ".tsv"
            ),
            n_jobs=n_jobs,
            chunk_size=chunk_size,
        )

    if validation:
        logger.info("Downloading validation, strongly labeled data...")
        download_audioset_files_from_csv(
            os.path.join(dataset_folder, "metadata", "validation", "validation.tsv"),
            os.path.join(dataset_folder, "audio", "validation"),
            missing_files_tsv=os.path.join(
                basedir_missing_files, "missing_files_" + "validation" + ".tsv"
            ),
            n_jobs=n_jobs,
            chunk_size=chunk_size,
        )

    logger.info(
        f"Please check your missing_files: {basedir_missing_files}, "
        f"you can relaunch 'download_audioset_sets' to try to recude them, "
        "then, send these missing_files to "
    )


def download_real(
    dataset_folder,
    weak=True,
    unlabel_in_domain=True,
    validation=True,
    eval=True,
    n_jobs=3,
    chunk_size=10,
):
    """ Download the DESED real part of the dataset.

    Args:
        dataset_folder: str, the path to the root of the dataset where to download the evaluation files (this folder
            contains audio and metadata folders).
        weak: bool, whether to download the weak set or not.
        unlabel_in_domain: bool, whether to download the unlabel_in_domain set or not.
        validation: bool, whether to download the validation set or not.
        eval: bool, whether to download the public eval set or not.
        n_jobs : int, number of download to execute in parallel
        chunk_size : int, number of files to download before updating the progress bar. Bigger it is, faster it goes
            because data is filled in memory but progress bar only updates after a chunk is finished.

    Returns:
    """
    if eval:
        download_eval_public(dataset_folder)
    download_audioset_data(
        dataset_folder,
        weak=weak,
        unlabel_in_domain=unlabel_in_domain,
        validation=validation,
        n_jobs=n_jobs,
        chunk_size=chunk_size,
    )


def _copy_files_kept(meta_df, input_dir, output_dir):
    """ Fonction to copy some files from input_dir to output_dir.
    The files to copy are stored in a pandas dataframe with a column "filename" and must match a name in the input_dir.

    Args:
        meta_df: pd.Dataframe, the dataframe with a column "filename" of files to keep (filtered filenames).
        input_dir: str, folder containing filenames to match.
        output_dir: str, the destination folder of the files copied

    Returns:

    """
    list_files_available = glob.glob(os.path.join(input_dir, "*"))
    df_files = pd.DataFrame(list_files_available, columns=["filename"])
    df_files["filename"] = df_files.filename.apply(lambda x: os.path.basename(x))

    merged = meta_df.merge(df_files, on="filename")
    merged.apply(
        lambda x: shutil.copy(
            os.path.join(input_dir, x["filename"]),
            os.path.join(output_dir, x["filename"]),
        ),
        axis=1,
    )


def download_sins(destination_folder):
    """ Download SINS database: see https://zenodo.org/record/1247102

    Args:
        destination_folder: str, the folder in which to download tut (will create `DCASE2018-task5-dev` folder in it)

    Returns:
        str, path of TUT extracted database
    """
    logger = create_logger(
        __name__ + "/" + inspect.currentframe().f_code.co_name,
        terminal_level=logging.INFO,
    )
    create_folder(destination_folder)
    zip_file_url_meta = f"https://zenodo.org/record/1247102/files/DCASE2018-task5-dev.meta.zip?download=1"
    download_and_unpack_archive(zip_file_url_meta, destination_folder, archive_format="zip")

    for i in range(1, 24):
        logger.info(f"SINS downloading zip {i} / 23 ...")
        zip_file_url = f"https://zenodo.org/record/1247102/files/DCASE2018-task5-dev.audio.{i}.zip?download=1"
        download_and_unpack_archive(zip_file_url, destination_folder, archive_format="zip")

    return os.path.join(destination_folder, "DCASE2018-task5-dev")


def filter_sins(
    sins_basedir="DCASE2018-task5-dev",
    destination_folder=os.path.join("background", "sins"),
    classes_kept=["other"],
    rm_original_sins=True,
):
    """ Fonction to copy a only some classes of sins into a new folder.
    Args:
        sins_basedir: str, the path where SINS database has been extracted
        destination_folder: str, the path where to store the filtered SINS version
            (in desed: basedir_soundbank/audio/train/background/sins)
        classes_kept: list, list of classes to keep in the origingal SINS database to use as backgrounds
        rm_original_sins: bool, whether to keep the original database too or not.

    Returns:
    """
    logger = create_logger(
        __name__ + "/" + inspect.currentframe().f_code.co_name,
        terminal_level=logging.INFO,
    )
    logger.info("Filtering SINS...")

    df = pd.read_csv(os.path.join(sins_basedir, "meta.txt"), sep="\t", header=None)
    df["filename"] = df[0].apply(lambda x: os.path.basename(x))
    df = df[df[1].isin(classes_kept)]

    _copy_files_kept(
        df, input_dir=os.path.join(sins_basedir, "audio"), output_dir=destination_folder
    )

    if rm_original_sins:
        shutil.rmtree(sins_basedir)


def download_tut(destination_folder):
    """ Download 'TUT Acoustic scenes 2017, Development dataset', see: https://zenodo.org/record/400515
    Args:
        destination_folder: str, the folder in which to download tut (will create `TUT-acoustic-scenes-2017-development`
            folder in it)

    Returns:
        str, path of extracted TUT database
    """
    logger = create_logger(
        __name__ + "/" + inspect.currentframe().f_code.co_name,
        terminal_level=logging.INFO,
    )
    create_folder(destination_folder)
    zip_meta_tut = f"https://zenodo.org/record/400515/files/TUT-acoustic-scenes-2017-development.meta.zip?download=1"
    download_and_unpack_archive(zip_meta_tut, destination_folder, archive_format="zip")

    for i in range(1, 11):
        logger.info(f"TUT (scenes-2017-dev) downloading zip {i} / 10 ...")
        zip_file_url = (
            f"https://zenodo.org/record/400515/files/"
            f"TUT-acoustic-scenes-2017-development.audio.{i}.zip?download=1"
        )
        download_and_unpack_archive(zip_file_url, destination_folder, archive_format="zip")

    return os.path.join(destination_folder, "TUT-acoustic-scenes-2017-development")


def filter_tut(
    tut_basedir="TUT-acoustic-scenes-2017-development",
    destination_folder=os.path.join("background", "tut-scenes-2017-dev"),
    classes_kept=["home", "office", "library"],
    rm_original_tut=True,
):
    """ Fonction to copy a only some classes of TUT into a new folder.
    Args:
        tut_basedir: str, the path where TUT database has been extracted
        destination_folder: str, the path where to store the filtered TUT version
            (in desed: basedir_soundbank/audio/train/background/tut-scenes-2017-dev)
        classes_kept: list, list of classes to be kept from TUT.
        rm_original_tut: bool, whether to keep the original database too or not.

    Returns:
    """
    logger = create_logger(
        __name__ + "/" + inspect.currentframe().f_code.co_name,
        terminal_level=logging.INFO,
    )
    logger.info("Filtering SINS...")

    df = pd.read_csv(os.path.join(tut_basedir, "meta.txt"), sep="\t", header=None)
    df["filename"] = df[0].apply(lambda x: os.path.basename(x))
    df = df[df[1].isin(classes_kept)]

    _copy_files_kept(df, os.path.join(tut_basedir, "audio"), destination_folder)

    if rm_original_tut:
        shutil.rmtree(tut_basedir)


def get_backgrounds_train(basedir_soundbank, sins=True, tut=False, keep_original=False):
    """ Download the background files of the DESED soundbank.
    (These files were not included in the Zenodo because of redistributing license issues.)
    Args:
        basedir_soundbank: str, the base folder of DESED dataset.
        sins: bool, download part of sins database as backgrounds.
        tut: bool, download part of TUT database as backgrounds.
        keep_original: bool, whether to keep the original databases too (sins, tut)

    Returns:
    """
    destination_folder = os.path.join(basedir_soundbank, "audio", "train", "soundbank")
    if sins:
        sins_path = download_sins(destination_folder)
        filter_sins(
            sins_path,
            destination_folder=os.path.join(destination_folder, "background", "sins"),
            rm_original_sins=not keep_original,
        )

    if tut:
        tut_path = download_tut(destination_folder)
        filter_tut(
            tut_path,
            destination_folder=os.path.join(
                destination_folder, "background", "tut-scenes-2017-dev"
            ),
            rm_original_tut=not keep_original,
        )


def download_zenodo_soundbank(destination_folder):
    """ Be careful, there are only the foregrounds of training.
    Args:
        destination_folder: str, the path of the root of the soundbank (will create the structure inside)

    Returns:
    """
    create_folder(destination_folder)
    zip_meta_tut = "https://zenodo.org/record/4307908/files/DESED_synth_soundbank.tar.gz?download=1"
    download_and_unpack_archive(zip_meta_tut, destination_folder)


def split_desed_soundbank_train_val(basedir):
    """ Split the training into training and validation (pre-made, 90%/10%) of backgrounds and foregrounds
    Args:
        basedir: str, path where the soundbank is downloaded (parent folder of "audio")

    Returns:

    """
    logger = create_logger(
        __name__ + "/" + inspect.currentframe().f_code.co_name,
        terminal_level=logging.INFO,
    )
    fname_valid = (
        "https://zenodo.org/record/4307908/files/soundbank_validation.tsv?download=1"
    )
    fpath = os.path.join(basedir, "soundbank_validation.tsv")
    download_file_from_url(fname_valid, fpath)
    df = pd.read_csv(fpath, sep="\t")
    for fpath in df.filepath:
        source_path = os.path.join(basedir, fpath.replace("validation", "train"))
        if os.path.exists(source_path):
            destination_path = os.path.join(basedir, fpath)
            create_folder(os.path.dirname(destination_path))
            shutil.move(source_path, destination_path)
    logger.info("Soundbank splitted in train and validation (90%/10%)")


def unsplit_desed_soundbank(basedir):
    """ UnSplit the the soundbank from training and validation (pre-made, 90%/10%) to training only folder.
    Args:
        basedir: str, path where the soundbank is downloaded (parent folder of "audio")

    Returns:

    """
    logger = create_logger(
        __name__ + "/" + inspect.currentframe().f_code.co_name,
        terminal_level=logging.INFO,
    )
    validation_path = os.path.join(basedir, "audio", "validation")
    for rootdir, subdirs, files in os.walk(validation_path):
        for fname in files:
            source_file = os.path.join(rootdir, fname)
            destination_file = source_file.replace("validation", "train")
            create_folder(os.path.dirname(destination_file))
            shutil.move(source_file, destination_file)
    shutil.rmtree(validation_path)
    logger.info("Unsplitted soundbank, validation moved back to train")


def download_fsd50k(destination_folder, gtruth_only=False):
    """ Download FSD50k dataset from Zenodo.
    Args:
        destination_folder: str, path where the FSD50k is extracted.
    """
    logger = create_logger(
        __name__ + "/" + inspect.currentframe().f_code.co_name,
        terminal_level=logging.INFO,
        )
    create_folder(destination_folder)
    if not gtruth_only:
        archive_folder = os.path.join("tmp_fsd50k")
        create_folder(archive_folder)
        # Train
        for id in ["01", "02", "03", "04", "05", "ip"]:
            logger.info(f"Downloading zip file: FSD50K.dev_audio.z{id}")
            url_dev = f"https://zenodo.org/record/4060432/files/FSD50K.dev_audio.z{id}?download=1"
            download_file_from_url(url_dev, os.path.join(archive_folder, f"FSD50K.dev_audio.z{id}"))
        logger.info("Unpacking files")
        subprocess.call(["zip", "-s", "0", os.path.join(archive_folder,'FSD50K.dev_audio.zip'),
                         "--out", os.path.join(archive_folder, 'unsplit_dev.zip')])
        shutil.unpack_archive(os.path.join(archive_folder, 'unsplit_dev.zip'), destination_folder)

        # Eval
        for id in ["01", "ip"]:
            logger.info(f"Downloading zip file: FSD50K.eval_audio.z{id}")
            url_eval = f"https://zenodo.org/record/4060432/files/FSD50K.eval_audio.z{id}?download=1"
            download_file_from_url(url_eval, os.path.join(archive_folder, f"FSD50K.eval_audio.z{id}"))
        logger.info("Unpacking files")
        subprocess.call(["zip", "-s", "0", os.path.join(archive_folder,'FSD50K.eval_audio.zip'),
                         "--out", os.path.join(archive_folder, 'unsplit_eval.zip')])
        shutil.unpack_archive(os.path.join(archive_folder, 'unsplit_eval.zip'), destination_folder)

    url_doc = "https://zenodo.org/record/4060432/files/FSD50K.doc.zip?download=1"
    url_gtruth = "https://zenodo.org/record/4060432/files/FSD50K.ground_truth.zip?download=1"
    url_meta = "https://zenodo.org/record/4060432/files/FSD50K.metadata.zip?download=1"
    for url in [url_doc, url_gtruth, url_meta]:
        download_and_unpack_archive(url, destination_folder, archive_format="zip")


def download_fuss(destination_folder):
    """ Download FUSS freesound data. These data are a subset of FSD50k, where each file should be a single event.
    Args:
        destination_folder: str, the folder in which to extract FUSS data.
    """
    url = "https://zenodo.org/record/3743844/files/FUSS_fsd_data.tar.gz?download=1"
    download_and_unpack_archive(url, destination_folder)


def download_desed_soundbank(
    basedir,
    sins_bg=True,
    tut_bg=True,
    split_train_valid=True,
    keep_original_sins_tut=False,
):
    """ Download the soundbank.
    Args:
        basedir: str, the dirname where to store the soundbank.
        sins_bg: bool, whether to download SINS backgrounds (default in 2019-2020).
        tut_bg: bool, whether to download 'TUT Acoustic scenes 2017, Development dataset' backgrounds or not
            (appeared in DCASE task 4 2020).
        split_train_valid: bool, whether to split the training foregrounds and backgrounds in training and validation
            (90%/10%). Default since DCASE task 4 2020.
        keep_original_sins_tut: bool, whether to keep the original versions of TUT and SINS.
    """
    print("downloading soundbank (foregrounds)...")
    download_zenodo_soundbank(basedir)
    print("Downloading backgrounds...")
    get_backgrounds_train(
        basedir, sins_bg, tut_bg, keep_original=keep_original_sins_tut
    )
    if split_train_valid:
        print("Splitting soundbank train into train and validation (90%/10%)...")
        split_desed_soundbank_train_val(basedir)