# -*- coding: utf-8 -*-
"""class and functions to generate synthetic data using loops"""
import os
from os import path as osp
import inspect

import pandas as pd
from scaper import generate_from_jams

from .logger import create_logger
from .post_process import _post_process_labels_file, get_labels_from_jams
from .soundscape import Soundscape
from .utils import create_folder, _check_random_state


class SoundscapesGenerator:
    """ Helps to generate set of Soundscapes
    Args:
        duration: float, the duration desired of the generated soundscapes
        fg_folder: str, path to the "foreground" folder. Contains one subfolder for each label
        bg_folder: str, path to the "background" folder. Contains one subfolder for each label
        ref_db: float, the dB reference of audio files (See scaper)
        samplerate: int, the sample rate desired of the generated soundscapes (be careful of the soundscape sample rate)
        random_state: np.random.RandomState or int, the random_state wanted to be able to reproduce the dataset
        delete_if_exists: bool, whether to delete existing files and folders created with the same name.
    """

    def __init__(
        self,
        duration,
        fg_folder,
        bg_folder,
        ref_db=-55,
        samplerate=16000,
        random_state=None,
        delete_if_exists=True,
        logger=None,
    ):
        self.duration = duration
        self.ref_db = ref_db
        self.fg_folder = fg_folder
        self.bg_folder = bg_folder
        self.samplerate = samplerate
        self.random_state = _check_random_state(random_state)
        self.delete_if_exists = delete_if_exists
        self.logger = logger
        if self.logger is None:
            self.logger = create_logger(
                __name__ + "/" + inspect.currentframe().f_code.co_name
            )

    def generate(
        self,
        number,
        out_folder,
        min_events=1,
        max_events=5,
        labels=("choose", []),
        source_files=("choose", []),
        sources_time=("const", 0),
        events_start=("truncnorm", 5.0, 2.0, 0.0, 10.0),
        events_duration=("uniform", 0.25, 10.0),
        snrs=("const", 30),
        pitch_shifts=("uniform", -3.0, 3.0),
        time_stretches=None,
        save_isolated_events=False,
        bg_labels=None,
        txt_file=True,
        start_from=0,
        **kwargs,
    ):
        """ Generate

        Args:
            number: int, number of audio clips to create.
            out_folder: str, path to extract generate file
            min_events: int, the minimum number of foreground events to add (pick at random uniformly).
            max_events: int, the maximum number of foreground events to add (pick at random uniformly).

            labels: tuple or list, distribution to choose foreground events or list of events.*
            source_files: tuple or list, distribution to choose source files or list of source files.*
            sources_time: tuple or list, distribution to choose source start time or list of sources start time.*
            events_start: tuple or list, distribution to choose events start time or list of events start time.*
            events_duration: tuple or list, distribution to choose events duation or list of events duration.*
            snrs: tuple or list, distribution to choose foreground to background SNRs or list of SNRs.*
            pitch_shifts: tuple or list, distribution to choose pitch shift or list of pitch shifts.*
            time_stretches: tuple or list, distribution to choose time stretches or list of time stretches.*
            save_isolated_events: bool, whether or not to save isolated events in a separate folder
            bg_labels: list, if None choose in all available files. If a name is given it has to match the name
                of a folder in 'background'. example: ["sins"]

            txt_file: bool, whether or not to save the .txt file.
            start_from: int, the number to start from if file already created.
            kwargs: arguments accepted by Scaper.generate

            * tuple is in the form of a distribution accepted by scaper.
        Returns:
            None
        """
        create_folder(out_folder)
        params = {
            "labels": labels,
            "source_files": source_files,
            "sources_time": sources_time,
            "events_start": events_start,
            "events_duration": events_duration,
            "snrs": snrs,
            "pitch_shifts": pitch_shifts,
            "time_stretches": time_stretches,
        }

        for cnt in range(number):
            self.logger.debug(
                "Generating soundscape: {:d}/{:d}".format(cnt + 1, number)
            )
            # create a scaper
            n_events = self.random_state.randint(min_events, max_events + 1)

            if start_from + cnt < 10:
                filename = "0" + str(start_from + cnt)
            else:
                filename = str(start_from + cnt)

            sc = Soundscape(
                self.duration,
                self.fg_folder,
                self.bg_folder,
                self.ref_db,
                self.samplerate,
                random_state=self.random_state,
                delete_if_exists=self.delete_if_exists,
            )
            sc.generate_one_bg_multi_fg(
                out_folder=out_folder,
                filename=filename,
                n_fg_events=n_events,
                **params,
                txt_file=txt_file,
                save_isolated_events=save_isolated_events,
                bg_labels=bg_labels,
                **kwargs,
            )
            if cnt % 200 == 0:
                self.logger.info(
                    f"generating {cnt} / {number} files (updated every 200)"
                )

    def generate_balance(
        self,
        number,
        out_folder,
        min_events,
        max_events,
        list_labels=None,
        save_isolated_events=False,
        start_from=0,
        snr=("uniform", 6, 30),
        pitch_shift=None,
        time_stretch=None,
        bg_labels=None,
        **kwargs,
    ):
        """ Generate landscapes by taking into account the probabilities of labels and their co-occurence
        Args:

            number: int, the number of files to generate
            out_folder: str, the path of the folder where to save the generated files
            min_events: int, the minimum number of events per files
            max_events: int, the maximum number of labels per file
            list_labels: list of available labels (in foreground)
            save_isolated_events: bool, whether or not to save isolated events in a subfolder
                (called <filename>_events by default)
            start_from: int, if already created file, will start the filenames at the specified number
            snr: tuple, tuple accepted by Scaper().add_event()
            pitch_shift: tuple, tuple accepted by Scaper().add_event()
            time_stretch: tuple, tuple accepted by Scaper().add_event()
            bg_labels: list, if None choose in all available files. If a name is given it has to match the name
                of a folder in 'background'. example: ["sins"]
            kwargs: parametes accepted by Scaper().generate()
        """
        create_folder(out_folder)
        cnt = 0
        if list_labels is None:
            list_labels = []
            for pth in os.listdir(self.fg_folder):
                if osp.isdir(osp.join(self.fg_folder, pth)):
                    if "non" in pth.lower() or "noff" in pth.lower():
                        for pattern in ["_nOn", "_nOff", "_non", "_noff"]:
                            pth = pth.replace(pattern, "")
                    list_labels.append(pth)
            list_labels = sorted(set(list_labels))
            self.logger.debug(f"list of labels: {list_labels}")

        for label in list_labels:
            self.logger.debug(
                "Generating soundscape: {:d}/{:d}".format(cnt + 1, number)
            )
            number_per_class = max(1, round(number // len(list_labels)))
            for i in range(number_per_class):
                sc = Soundscape(
                    self.duration,
                    self.fg_folder,
                    self.bg_folder,
                    self.ref_db,
                    self.samplerate,
                    random_state=self.random_state,
                    delete_if_exists=self.delete_if_exists,
                )
                if start_from + cnt < 10:
                    filename = "0" + str(start_from + cnt)
                else:
                    filename = str(start_from + cnt)
                if min_events == max_events:
                    n_events = min_events
                else:
                    n_events = self.random_state.randint(min_events, max_events)
                sc.generate_using_non_noff(
                    label=label,
                    list_labels=list_labels,
                    out_folder=out_folder,
                    filename=filename,
                    n_events=n_events,
                    save_isolated_events=save_isolated_events,
                    snr=snr,
                    pitch_shift=pitch_shift,
                    time_stretch=time_stretch,
                    bg_labels=bg_labels,
                    **kwargs,
                )
                if cnt % 200 == 0:
                    self.logger.info(
                        f"generating {cnt} / {number} files (updated every 200)"
                    )
                cnt += 1
        if cnt != number:
            self.logger.warn(
                f"The number of generated examples ({cnt}) is different from the number asked ({number}) "
                f"because of probabilities of events."
            )

    def generate_by_label_occurence(
        self,
        label_occurences,
        number,
        out_folder,
        min_events=0,
        max_events=None,
        save_isolated_events=False,
        start_from=0,
        snr=("uniform", 6, 30),
        pitch_shift=None,
        time_stretch=None,
        bg_labels=None,
        **kwargs,
    ):
        """ Generate landscapes by taking into account the probabilities of labels and their co-occurence
        Args:
            label_occurences: dict, parameters of labels occurences (foreground labels)
            number: int, the number of files to generate
            out_folder: str, the path of the folder where to save the generated files
            min_events: int, optional, the minimum number of events per files (default=0)
                (Be careful, if max_events in label_occurences params is less than this it will raise an error)
                If defined in the label_occurences dict, this parameter overwrites it.
            max_events: int, optional, if defined, overwrite the value in label_occurences if defined.
            save_isolated_events: bool, whether or not to save isolated events in a subfolder
                (called <filename>_events by default)
            start_from: int, if already created file, will start the filenames at the specified number
            snr: tuple, tuple accepted by Scaper().add_event()
            pitch_shift: tuple, tuple accepted by Scaper().add_event()
            time_stretch: tuple, tuple accepted by Scaper().add_event()
            bg_labels: list, if None choose in all available files. If a name is given it has to match the name
                of a folder in 'background'. example: ["sins"]
            kwargs: parametes accepted by Scaper().generate()
        Returns:

        Examples:
            An example of a JSON looks like this:
            event_occurences.json
            {
              "Alarm_bell_ringing": {
                "proba" : 0.6,
                "co-occurences": {
                  "max_events": 13,
                  "classes": [
                    "Alarm_bell_ringing",
                    "Dog",
                  ],
                  "probas": [
                    70,
                    30
                  ]
                },
              "Dog": {
                "prob" : 0.4,
                "co-occurences": {
                "max_events": 14,
                "classes": [
                  "Alarm_bell_ringing",
                  "Dog",
                ],
                "event_prob": [
                  25,
                  75,
                ]
              }
            }
        """
        create_folder(out_folder)
        cnt = 0
        for label in label_occurences.keys():
            self.logger.debug(
                "Generating soundscape: {:d}/{:d}".format(cnt + 1, number)
            )
            label_params = label_occurences[label]
            for i in range(round(number * label_params["proba"])):
                sc = Soundscape(
                    self.duration,
                    self.fg_folder,
                    self.bg_folder,
                    self.ref_db,
                    self.samplerate,
                    random_state=self.random_state,
                    delete_if_exists=self.delete_if_exists,
                )
                if start_from + cnt < 10:
                    filename = "0" + str(start_from + cnt)
                else:
                    filename = str(start_from + cnt)

                sc.generate_co_occurence(
                    co_occur_params=label_params["co-occurences"],
                    label=label,
                    out_folder=out_folder,
                    filename=filename,
                    min_events=min_events,
                    max_events=max_events,
                    save_isolated_events=save_isolated_events,
                    snr=snr,
                    pitch_shift=pitch_shift,
                    time_stretch=time_stretch,
                    bg_labels=bg_labels,
                    **kwargs,
                )
                if cnt % 200 == 0:
                    self.logger.info(
                        f"generating {cnt} / {number} files (updated every 200)"
                    )
                cnt += 1
        if cnt != number:
            self.logger.warn(
                f"The number of generated examples ({cnt}) is different from the number asked ({number}) "
                f"because of probabilities of events."
            )


def generate_df_from_jams(list_jams, post_process=True, background_label=False):
    if len(list_jams) == 0:
        raise IndexError(
            "Cannot generate df from JAMS, the list of jams given is empty"
        )

    final_df = pd.DataFrame()
    for jam_file in list_jams:
        fbase = osp.basename(jam_file)
        df, length = get_labels_from_jams(
            jam_file, background_label=background_label, return_length=True
        )

        if post_process:
            df, _ = _post_process_labels_file(df, length)

        df["filename"] = f"{osp.splitext(fbase)[0]}.wav"
        final_df = final_df.append(
            df[["filename", "onset", "offset", "event_label"]], ignore_index=True
        )

    final_df = final_df.sort_values(by=["filename", "onset"])
    return final_df


def generate_tsv_from_jams(
    list_jams, tsv_out, post_process=True, background_label=False
):
    """ In scaper.generate they create a txt file for each audio file.
    Using the same idea, we create a single tsv file with all the audio files and their labels.
    Args:
        list_jams: list, list of paths of JAMS files. Assume WAV files have the same name as JAMS files.
        tsv_out: str, path of the tsv to be saved
        post_process: bool, post_process removes small blanks, clean the overlapping same events in the labels and
        make the smallest event 250ms long.
        background_label: bool, include the background label in the annotations.
        # source_sep_path: str, the path to save the csv of separated source files. Assume

    Returns:
        None
    """
    create_folder(osp.dirname(tsv_out))
    final_df = generate_df_from_jams(list_jams, post_process, background_label)
    final_df.to_csv(tsv_out, sep="\t", index=False, float_format="%.3f")


def generate_files_from_jams(
    list_jams,
    out_folder,
    fg_path=None,
    bg_path=None,
    out_folder_jams=None,
    save_isolated_events=False,
    overwrite_exist_audio=False,
    **kwargs,
):
    """ Generate audio files from jams files generated by Scaper

    Args:
        list_jams: list, list of jams filepath generated by Scaper.
        out_folder: str, output path to save audio files.
        fg_path: str, the path to the foreground events, if not specified, should match what specified in the JAMS.
        bg_path: str, the path to the background events, if not specified, should match what specified in the JAMS.
        out_folder_jams: str, path to write the jams (could be modified by fg_path and bg_path for example),
            if None, jams not saved
        save_isolated_events: bool, whether or not to save isolated events in a separate folder
        overwrite_exist_audio: bool, whether to regenerate existing audio files or not
        kwargs: dict, scaper.generate_from_jams params (fg_path, bg_path, ...)
    Returns: None

    """
    logger = create_logger(__name__ + "/" + inspect.currentframe().f_code.co_name)
    logger.info(f"generating audio files to {out_folder}")
    create_folder(out_folder)
    for n, jam_file in enumerate(list_jams):
        logger.debug(jam_file)
        audiofile = osp.join(
            out_folder, f"{osp.splitext(osp.basename(jam_file))[0]}.wav"
        )
        if not osp.exists(audiofile) or overwrite_exist_audio:
            if out_folder_jams is not None:
                jams_outfile = osp.join(out_folder_jams, osp.basename(jam_file))
            else:
                jams_outfile = None
            generate_from_jams(
                jam_file,
                audiofile,
                fg_path=fg_path,
                bg_path=bg_path,
                jams_outfile=jams_outfile,
                save_isolated_events=save_isolated_events,
                **kwargs,
            )

        if n % 200 == 0:
            logger.info(f"generating {n} / {len(list_jams)} files (updated every 200)")
    logger.info("Done")
