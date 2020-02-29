# -*- coding: utf-8 -*-
"""class and functions to generate synthetic data using loops"""
from os import path as osp
import inspect

import numpy as np
import pandas as pd
from scaper import generate_from_jams

from .logger import create_logger
from .post_process import _post_process_labels_file, get_labels_from_jams
from .soundscape import Soundscape
from .utils import create_folder


class SoundscapesGenerator:
    def __init__(self, duration, fg_folder, bg_folder, ref_db=-55, samplerate=16000, random_state=None):
        self.duration = duration
        self.ref_db = ref_db
        self.fg_folder = fg_folder
        self.bg_folder = bg_folder
        self.samplerate = samplerate
        self.random_state = random_state

    def generate(self, number, outfolder, min_events, max_events,
                 labels=('choose', []), source_files=('choose', []), sources_time=('const', 0),
                 events_start=('truncnorm', 5.0, 2.0, 0.0, 10.0), events_duration=('uniform', 0.25, 10.0),
                 snrs=('const', 30), pitch_shifts=('uniform', -3.0, 3.0), time_stretches=('uniform', 1, 1),
                 txt_file=True, save_isolated_events=False, **kwargs):
        """ Generate

        Args:
            number: int, number of audio clips to create.
            outfolder: str, path to extract generate file
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
            txt_file: bool, whether or not to save the .txt file.
            save_isolated_events: bool, whether or not to save isolated events in a separate folder
            kwargs: arguments accepted by Scaper.generate

        Returns:
            None
        """
        logger = create_logger(__name__ + "/" + inspect.currentframe().f_code.co_name)
        params = {
            'labels': labels,
            'source_files': source_files,
            'sources_time': sources_time,
            'events_start': events_start,
            'events_duration': events_duration,
            'snrs': snrs,
            'pitch_shifts': pitch_shifts,
            'time_stretches': time_stretches
        }

        for n in range(number):
            logger.debug('Generating soundscape: {:d}/{:d}'.format(n + 1, number))
            # create a scaper
            n_events = np.random.randint(min_events, max_events + 1)
            self._generate_one_bg_multi_fg(out_folder=outfolder,
                                           filename=n,
                                           n_fg_events=n_events,
                                           **params,
                                           txt_file=txt_file,
                                           save_isolated_events=save_isolated_events,
                                           **kwargs)

    def _generate_one_bg_multi_fg(self, out_folder, filename, n_fg_events,
                                  labels=('choose', []),
                                  source_files=('choose', []), sources_time=('const', 0),
                                  events_start=('truncnorm', 5.0, 2.0, 0.0, 10.0),
                                  events_duration=("uniform", 0.25, 10.0),
                                  snrs=("uniform", 6, 30), pitch_shifts=('uniform', -3.0, 3.0),
                                  time_stretches=('uniform', 1, 1), reverb=0.1,
                                  txt_file=True,
                                  save_isolated_events=False, isolated_events_path=None,
                                  **kwargs):
        """ Generate a clip with a background file and multiple foreground files.
        Args:
            out_folder: str, path to extract generate file
            filename: str, name of the generated file, without extension (.wav, .jams and .txt will be created)
            n_fg_events: int, the number of foreground events to add
            labels: tuple or list, distribution to choose foreground events or list of events.*
            source_files: tuple or list, distribution to choose source files or list of source files.*
            sources_time: tuple or list, distribution to choose source start time or list of sources start time.*
            events_start: tuple or list, distribution to choose events start time or list of events start time.*
            events_duration: tuple or list, distribution to choose events duation or list of events duration.*
            snrs: tuple or list, distribution to choose foreground to background SNRs or list of SNRs.*
            pitch_shifts: tuple or list, distribution to choose pitch shift or list of pitch shifts.*
            time_stretches: tuple or list, distribution to choose time stretches or list of time stretches.*
            reverb: float, the reverb to be applied to the foreground events
            txt_file: bool, whether or not to save the .txt file.
            save_isolated_events: bool, whether or not to save isolated events in a separate folder
            isolated_events_path: str, only useful when save_isolated_events=True. Give the path to the events folders.
                If None, a folder is created next to the audio files.
            kwargs: arguments accepted by Scaper.generate

            * All arguments with asterix, if tuple given, see Scaper for distribution allowed.
        Returns:
            None
        """
        sc = Soundscape(self.duration, self.fg_folder, self.bg_folder, self.ref_db, self.samplerate,
                        random_state=self.random_state)
        sc.add_random_background()

        params = {"label": labels, "source_file": source_files, "source_time": sources_time, "event_time": events_start,
                  "event_duration": events_duration, "snr": snrs, "pitch_shift": pitch_shifts,
                  "time_stretch": time_stretches}
        # Make sure that if we give a list of tuple for a parameter that the length of the list
        # is matching the number of foreground events
        for i in range(n_fg_events):
            event_params = {}
            for key in params:
                if type(params[key]) is tuple:
                    param = params[key]
                elif type(params[key]) is list:
                    assert len(params[key]) == n_fg_events
                    param = params[key][i]
                else:
                    raise NotImplementedError("Params of events is tuple(same for all) or "
                                              "list (different for each event)")
                event_params[key] = param

            sc.add_event(**event_params)

        # generate
        audiofile = osp.join(out_folder, f"{filename}.wav")
        jamsfile = osp.join(out_folder, f"{filename}.jams")
        if txt_file:
            # Can be useless if you want background annotation as well, see post_processing_annotations.
            txtfile = osp.join(out_folder, f"{filename}.txt")
        else:
            txtfile = None
        if save_isolated_events and isolated_events_path is None:
            isolated_events_path = osp.join(out_folder, f"{filename}_events")

        sc.generate(audio_path=audiofile, jams_path=jamsfile,
                    reverb=reverb,
                    txt_path=txtfile,
                    save_isolated_events=save_isolated_events,
                    isolated_events_path=isolated_events_path,
                    **kwargs)

    def generate_by_label_occurence(self, label_occurences, number, out_folder, min_events=0, max_events=None,
                                    save_isolated_events=False,
                                    **kwargs):
        """

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
        log = create_logger(__name__ + "/" + inspect.currentframe().f_code.co_name)
        n = 0
        for class_lbl in label_occurences.keys():
            log.debug('Generating soundscape: {:d}/{:d}'.format(n + 1, number))
            class_params = label_occurences[class_lbl]
            for i in range(int(number * class_params['proba'])):
                sc = Soundscape(self.duration, self.fg_folder, self.bg_folder, self.ref_db, self.samplerate,
                                random_state=self.random_state)
                sc.generate_co_occurence(co_occur_params=class_params["co-occurences"],
                                         label=class_lbl,
                                         out_folder=out_folder,
                                         filename=n,
                                         min_events=min_events,
                                         max_events=max_events,
                                         save_isolated_events=save_isolated_events,
                                         **kwargs)

                n += 1


def generate_tsv_from_jams(list_jams, tsv_out, post_process=True, background_label=False):
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
    final_df = pd.DataFrame()
    for jam_file in list_jams:
        print(jam_file)
        fbase = osp.basename(jam_file)
        df, length = get_labels_from_jams(jam_file, background_label=background_label, return_length=True)

        if post_process:
            df, _ = _post_process_labels_file(df, length)

        df["filename"] = f"{osp.splitext(fbase)[0]}.wav"
        final_df = final_df.append(df[['filename', 'onset', 'offset', 'event_label']], ignore_index=True)

    final_df = final_df.sort_values(by=["filename", "onset"])
    final_df.to_csv(tsv_out, sep="\t", index=False, float_format="%.3f")


def generate_files_from_jams(list_jams, out_folder, out_folder_jams=None,
                             save_isolated_events=False, isolated_events_path=None,
                             overwrite_exist_audio=False,
                             **kwargs):
    """ Generate audio files from jams files generated by Scaper

    Args:
        list_jams: list, list of jams filepath generated by Scaper.
        out_folder: str, output path to save audio files.
        out_folder_jams: str, path to write the jams (could be modified by fg_path and bg_path for example),
            if None, jams not saved
        save_isolated_events: bool, whether or not to save isolated events in a separate folder
        isolated_events_path: str, only useful when save_isolated_events=True. Give the path to the events folders.
            If None, a folder is created next to the audio files.
        overwrite_exist_audio: bool, whether to regenerate existing audio files or not
        kwargs: dict, scaper.generate_from_jams params (fg_path, bg_path, ...)
    Returns: None

    """
    logger = create_logger(__name__ + "/" + inspect.currentframe().f_code.co_name)
    logger.info(f"generating audio files to {out_folder}")
    create_folder(out_folder)
    for n, jam_file in enumerate(list_jams):
        logger.debug(jam_file)
        audiofile = osp.join(out_folder, f"{osp.splitext(osp.basename(jam_file))[0]}.wav")
        if not osp.exists(audiofile) or overwrite_exist_audio:
            if out_folder_jams is not None:
                jams_outfile = osp.join(out_folder_jams, osp.basename(jam_file))
            else:
                jams_outfile = None
            generate_from_jams(jam_file, audiofile, jams_outfile=jams_outfile,
                               save_isolated_events=save_isolated_events,
                               isolated_events_path=isolated_events_path,
                               **kwargs)

        if n % 200 == 0:
            logger.info(f"generating {n} / {len(list_jams)} files (updated every 200)")
    logger.info("Done")
