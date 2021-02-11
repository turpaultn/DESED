"""Sounscape is a subclass of scaper.Scaper to fulfill our specific needs and default values"""
import glob
import inspect
import numpy as np
import os
import shutil
import warnings
from os import path as osp

import scaper
import soundfile as sf

from .logger import create_logger, DesedWarning, DesedError
from .utils import choose_cooccurence_class, create_folder


class Soundscape(scaper.Scaper):
    """ Initialize scaper object with a reference dB and sr.
            Args:
                duration: float, in seconds, the duration of the generated audio clip.
                fg_path: str, path of foreground files (be careful, need subfolders, one per class or group)
                bg_path: str, path of background files (be careful, need subfolders, one per group)
                ref_db: float, the reference dB of the clip.
                samplerate: int, the sr of the final soundscape
                delete_if_exists: bool, whether to delete existing files and folders created with the same name.

            Returns:
                scaper.Scaper object
    """

    def __init__(
        self,
        duration,
        fg_path,
        bg_path,
        ref_db=-55,
        samplerate=16000,
        random_state=None,
        delete_if_exists=True,
    ):
        super(Soundscape, self).__init__(
            duration, fg_path, bg_path, random_state=random_state
        )
        self.ref_db = ref_db
        self.sr = samplerate
        if self.ref_db is not None:
            self.ref_db = ref_db
        if self.sr is not None:
            self.sr = samplerate
        self.delete_if_exists = delete_if_exists

    def add_random_background(self, label=None):
        """ Add a random background to a scaper object
        Args:
            label: str or list, possible labels are names the subfolders of self.bg_path. None can use them all.
        """
        # If str or None, keep it like this
        if label is not None:
            if isinstance(label, list):
                bg_label = self.random_state.choice(label)
            elif isinstance(label, str):
                bg_label = label
            else:
                raise NotImplementedError(
                    "Background label can only be a list of available labels or a string"
                )
        else:
            bg_label = "*"
        chosen_file = self._choose_file(osp.join(self.bg_path, bg_label))
        file_duration = sf.info(chosen_file).duration
        starting_source = min(
            self.random_state.rand() * file_duration,
            max(file_duration - self.duration, 0),
        )
        self.add_background(
            label=("const", chosen_file.split("/")[-2]),
            source_file=("const", chosen_file),
            source_time=("const", starting_source),
        )

    def add_fg_event_non_noff(
        self,
        label,
        snr=("uniform", 6, 30),
        pitch_shift=None,
        time_stretch=None,
        event_duration_min=0.25,
    ):
        """ add a single event to a scaper object given a class. Take into account if the event has an onset or offset
        Args:
            label: str, label of the event to add.
            snr: tuple, tuple accepted by Scaper().add_event()
            pitch_shift: tuple, tuple accepted by Scaper().add_event()
            time_stretch: tuple, tuple accepted by Scaper().add_event()
            event_duration_min: float, minimum duration of a foreground event (in second)

        Returns:
            sc, scaper.Scaper object with the event added.

        """
        logger = create_logger(__name__ + "/" + inspect.currentframe().f_code.co_name)
        label_path = os.path.join(self.fg_path, label)
        assert osp.exists(
            label_path
        ), f"The label provided ({label}) does not point to a valid folder: {label_path}"
        chosen_file = self._choose_file(os.path.join(self.fg_path, label))
        file_duration = round(
            sf.info(chosen_file).duration, 6
        )  # because Scaper uses sox with truncate 6 digits
        if "_nOn_nOff" in label:
            # If no onset and offset, the file should be bigger than the duration of the file
            logger.debug("no onset/offset")
            if file_duration - self.duration <= 0:
                warnings.warn(
                    "Event without onset and offset added not for the full time of the audio soundscape"
                )
                source_start = 0
            else:
                source_start = self.random_state.uniform(
                    0, file_duration - self.duration
                )

            self.add_event(
                label=("const", label),
                source_file=("const", chosen_file),
                source_time=("const", source_start),
                event_time=("const", 0),
                event_duration=("const", self.duration),
                snr=snr,
                pitch_shift=pitch_shift,
                time_stretch=time_stretch,
            )
        elif "_nOn" in label:
            logger.debug("no onset")
            if file_duration - event_duration_min <= 0:
                source_start = 0
            else:
                source_start = self.random_state.uniform(
                    0, file_duration - event_duration_min
                )
            self.add_event(
                label=("const", label),
                source_file=("const", chosen_file),
                source_time=("const", source_start),
                event_time=("const", 0),
                event_duration=(
                    "const",
                    np.minimum(self.duration, file_duration - source_start),
                ),
                snr=snr,
                pitch_shift=pitch_shift,
                time_stretch=time_stretch,
            )
        elif "_nOff" in label:
            logger.debug("no offset")
            event_start = self.random_state.uniform(
                max(0, self.duration - file_duration),
                self.duration - event_duration_min,
            )
            event_length = self.duration - event_start
            self.add_event(
                label=("const", label),
                source_file=("const", chosen_file),
                source_time=("const", 0),
                event_time=("const", event_start),
                event_duration=("const", event_length),
                snr=snr,
                pitch_shift=pitch_shift,
                time_stretch=time_stretch,
            )
        else:
            logger.debug("onset offset")
            if file_duration > self.duration:
                if file_duration // self.duration > 2:
                    choice = np.random.choice(
                        ["onset", "middle", "offset"], p=[0.375, 0.25, 0.375]
                    )
                else:
                    choice = np.random.choice(["onset", "offset"])
                logger.debug(f"choice: {choice}")
                if choice == "onset":
                    event_start = self.random_state.uniform(
                        0, self.duration - event_duration_min
                    )
                    length_possible = self.duration - event_start
                    event_length = (
                        file_duration
                        if file_duration < length_possible
                        else length_possible
                    )
                    source_start = 0
                elif choice == "offset":
                    event_start = 0
                    event_length = self.random_state.uniform(
                        0, self.duration - event_duration_min
                    )
                    source_start = file_duration - event_length
                else:
                    source_start = self.random_state.uniform(
                        self.duration, file_duration - self.duration
                    )
                    event_start = 0
                    event_length = self.duration
            else:
                event_start = self.random_state.uniform(
                    0, self.duration - event_duration_min
                )
                source_start = 0
                length_possible = self.duration - event_start
                event_length = (
                    file_duration
                    if file_duration < length_possible
                    else length_possible
                )
            logger.debug(
                f"event_start: {event_start}, length: {event_length}, source_start: {source_start}, "
                f"file_duration: {file_duration}"
            )

            self.add_event(
                label=("const", label),
                source_file=("const", chosen_file),
                source_time=("const", source_start),
                event_time=("const", event_start),
                event_duration=("const", event_length),
                snr=snr,
                pitch_shift=pitch_shift,
                time_stretch=time_stretch,
            )
        return self

    def _choose_file(self, class_path, non_noff=False):
        """ Choose randomly a file of a given class.
        Args:
            class_path: str, path of the class containing all the files of a certain class.

        Returns:
            str, path of the file.
        """
        event_files = sorted(glob.glob(os.path.join(class_path, "*")))
        if non_noff:
            event_files.append(glob.glob(os.path.join(class_path + "_nOn", "*")))
            event_files.append(glob.glob(os.path.join(class_path + "_nOff", "*")))
            event_files.append(glob.glob(os.path.join(class_path + "_nOn_nOff", "*")))
            event_files = sorted(event_files)

        event_files = [f for f in event_files if os.path.isfile(f)]
        assert len(event_files) > 0, (
            f"no event files to be chosen in this path: {os.path.join(class_path, '*')}"
            f" (pattern used by glob)"
        )
        ind = self.random_state.randint(0, len(event_files))
        return event_files[ind]

    def _remove(self, path):
        if osp.exists(path):
            if osp.isdir(path):
                shutil.rmtree(path)
            elif osp.isfile(path):
                os.remove(path)
            else:
                raise NotImplementedError("Can only remove files or folders")

    def generate_co_occurence(
        self,
        co_occur_params,
        label,
        out_folder,
        filename,
        min_events=1,
        max_events=None,
        reverb=None,
        save_isolated_events=False,
        snr=("uniform", 6, 30),
        pitch_shift=None,
        time_stretch=None,
        bg_labels=None,
        **kwargs,
    ):
        """ Generate a single file, using the information of onset or offset present
        (see DESED dataset and folders in soundbank foreground)
        Args:
            co_occur_params: dict, dict containing information about how to mix classes,
                and the probability of each class.
            label: str, the main foreground label of the generated file.
            out_folder: str, path to extract generate file
            filename: str, name of the generated file, without extension (.wav, .jams and .txt will be created)
            min_events: int, optional, the minimum number of events per files (default=1, >= 1)
                (Be careful, if max_events in label_occurences params is less than this it will raise an error)
                If defined in the label_occurences dict, this parameter corresponds to the number of cooccurences.
            max_events: int, optional, if defined, overwrite the value in label_occurences if defined
                (in label_occurences this parameter corresponds to the number of cooccurences).
            reverb: float, the reverb to be applied to the foreground events
            save_isolated_events: bool, whether or not to save isolated events in a subfolder
                (called <filename>_events by default)
            snr: tuple, tuple accepted by Scaper().add_event()
            pitch_shift: tuple, tuple accepted by Scaper().add_event()
            time_stretch: tuple, tuple accepted by Scaper().add_event()
            bg_labels: list or str, if None choose in all available files.
                If a name or list is given it has to match the name of a folder in 'background'. example: "sins"
            kwargs: arguments accepted by Scaper.generate
        Returns:
            None

        Examples:
            Example of co_occur_params dictionary::
                {
                  "max_events": 13,
                  "classes": [
                    "Alarm_bell_ringing",
                    "Dog",
                  ],
                  "probas": [
                    70,
                    30
                  ]
                }
            prob is the probability of this class (not used here)
        """
        create_folder(out_folder)
        self.add_random_background(bg_labels)

        # add main event, non_noff stands for no onset and no offset (accept label to have _nOn or _nOff specified).
        self.add_fg_event_non_noff(
            label, snr=snr, pitch_shift=pitch_shift, time_stretch=time_stretch
        )

        if max_events is None:
            max_events = co_occur_params.get("max_events")
            if max_events is None:
                raise DesedError("max_events has to be specified")
        else:
            max_events = max_events - 1

        if min_events is None:
            min_events = co_occur_params.get("min_events")
            if min_events is None:
                raise DesedError(
                    "min_events has to be specified in generate co occurence or in params"
                )
        else:
            min_events = min_events - 1

        # add random number of foreground events
        if min_events == max_events:
            n_events = min_events
        else:
            n_events = self.random_state.randint(min_events, max_events)
        for _ in range(n_events):
            chosen_class = choose_cooccurence_class(
                co_occur_params, random_state=self.random_state
            )
            self.add_fg_event_non_noff(
                chosen_class,
                snr=snr,
                pitch_shift=pitch_shift,
                time_stretch=time_stretch,
            )

        # Just in case an extension has been added
        ext = osp.splitext(filename)[-1]
        if ext in [".wav", ".jams", ".txt"]:
            filename = osp.splitext(filename)[0]

        # generate
        audio_file = osp.join(out_folder, f"{filename}.wav")
        jams_file = osp.join(out_folder, f"{filename}.jams")
        txt_file = osp.join(out_folder, f"{filename}.txt")

        if self.delete_if_exists:
            self._remove(audio_file)
            self._remove(jams_file)
            self._remove(txt_file)

        # To get isolated events in a subfolder
        isolated_events_path = kwargs.get("isolated_events_path")
        if save_isolated_events:
            if isolated_events_path is None:
                isolated_events_path = osp.join(out_folder, f"{filename}_events")
            if self.delete_if_exists:
                self._remove(isolated_events_path)
            else:
                if osp.exists(isolated_events_path):
                    warnings.warn(
                        f"The folder {isolated_events_path} already exists, it means there could be some "
                        f"unwanted audio files from previous generated audio files in it.",
                        DesedWarning,
                    )

        self.generate(
            audio_file,
            jams_file,
            reverb=reverb,
            txt_path=txt_file,
            save_isolated_events=save_isolated_events,
            isolated_events_path=isolated_events_path,
            **kwargs,
        )

    def generate_using_non_noff(
        self,
        label,
        list_labels,
        out_folder,
        filename,
        n_events,
        reverb=None,
        save_isolated_events=False,
        snr=("uniform", 6, 30),
        pitch_shift=None,
        time_stretch=None,
        bg_labels=None,
        **kwargs,
    ):
        """ Generate a single file, using the information of onset or offset present
        (see DESED dataset and folders in soundbank foreground)
        Args:
            label: str, the main foreground label of the generated file.
            list_labels: list, the list of available labels
            out_folder: str, path to extract generate file
            filename: str, name of the generated file, without extension (.wav, .jams and .txt will be created)
            n_events: int, the of events in the soundscape
            reverb: float, the reverb to be applied to the foreground events
            save_isolated_events: bool, whether or not to save isolated events in a subfolder
                (called <filename>_events by default)
            snr: tuple, tuple accepted by Scaper().add_event()
            pitch_shift: tuple, tuple accepted by Scaper().add_event()
            time_stretch: tuple, tuple accepted by Scaper().add_event()
            bg_labels: list, if None choose in all available files. If a name is given it has to match the name
                of a folder in 'background'. example: ["sins"]
            kwargs: arguments accepted by Scaper.generate
        Returns:
            None

        """
        create_folder(out_folder)
        self.add_random_background(bg_labels)

        if n_events > 0:
            # add main event, non_noff stands for no onset and no offset (accept label to have _nOn or _nOff specified).
            self.add_fg_event_non_noff(
                label, snr=snr, pitch_shift=pitch_shift, time_stretch=time_stretch
            )

            for _ in range(n_events - 1):
                chosen_class = self.random_state.choice(list_labels)
                self.add_fg_event_non_noff(
                    chosen_class,
                    snr=snr,
                    pitch_shift=pitch_shift,
                    time_stretch=time_stretch,
                )

        # Just in case an extension has been added
        ext = osp.splitext(filename)[-1]
        if ext in [".wav", ".jams", ".txt"]:
            filename = osp.splitext(filename)[0]

        # generate
        audio_file = osp.join(out_folder, f"{filename}.wav")
        jams_file = osp.join(out_folder, f"{filename}.jams")
        txt_file = osp.join(out_folder, f"{filename}.txt")

        if self.delete_if_exists:
            self._remove(audio_file)
            self._remove(jams_file)
            self._remove(txt_file)

        # To get isolated events in a subfolder
        isolated_events_path = kwargs.get("isolated_events_path")
        if save_isolated_events:
            if isolated_events_path is None:
                isolated_events_path = osp.join(out_folder, f"{filename}_events")
            if self.delete_if_exists:
                self._remove(isolated_events_path)
            else:
                if osp.exists(isolated_events_path):
                    warnings.warn(
                        f"The folder {isolated_events_path} already exists, it means there could be some "
                        f"unwanted audio files from previous generated audio files in it.",
                        DesedWarning,
                    )

        self.generate(
            audio_file,
            jams_file,
            reverb=reverb,
            txt_path=txt_file,
            save_isolated_events=save_isolated_events,
            isolated_events_path=isolated_events_path,
            **kwargs,
        )

    def generate_one_bg_multi_fg(
        self,
        out_folder,
        filename,
        n_fg_events,
        labels=("choose", []),
        source_files=("choose", []),
        sources_time=("const", 0),
        events_start=("truncnorm", 5.0, 2.0, 0.0, 10.0),
        events_duration=("uniform", 0.25, 10.0),
        snrs=("uniform", 6, 30),
        pitch_shifts=("uniform", -3.0, 3.0),
        time_stretches=("uniform", 1, 1),
        reverb=0.1,
        txt_file=True,
        save_isolated_events=False,
        isolated_events_path=None,
        bg_labels=None,
        **kwargs,
    ):
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
            bg_labels: list, if None choose in all available files. If a name is given it has to match the name
                of a folder in 'background'. example: ["sins"]
            kwargs: arguments accepted by Scaper.generate

            * All arguments with asterix, if tuple given, see Scaper for distribution allowed.
        Returns:
            None
        """
        create_folder(out_folder)
        self.add_random_background(bg_labels)

        params = {
            "label": labels,
            "source_file": source_files,
            "source_time": sources_time,
            "event_time": events_start,
            "event_duration": events_duration,
            "snr": snrs,
            "pitch_shift": pitch_shifts,
            "time_stretch": time_stretches,
        }
        # Make sure that if we give a list of tuple for a parameter that the length of the list
        # is matching the number of foreground events
        for i in range(n_fg_events):
            event_params = {}
            for key in params:
                if params[key] is None or isinstance(params[key], tuple):
                    param = params[key]
                elif type(params[key]) is list:
                    assert len(params[key]) == n_fg_events
                    if not isinstance(params[key][i], tuple):
                        param = ("const", params[key][i])
                    else:
                        param = params[key][i]
                else:
                    raise NotImplementedError(
                        "Params of events is tuple(same for all) or "
                        "list (different for each event)"
                    )
                event_params[key] = param

            self.add_event(**event_params)

        # generate
        audiofile = osp.join(out_folder, f"{filename}.wav")
        jamsfile = osp.join(out_folder, f"{filename}.jams")

        if self.delete_if_exists:
            self._remove(audiofile)
            self._remove(jamsfile)

        if txt_file:
            # Can be useless if you want background annotation as well, see post_processing_annotations.
            txtfile = osp.join(out_folder, f"{filename}.txt")
            if self.delete_if_exists:
                self._remove(txtfile)
        else:
            txtfile = None

        if save_isolated_events:
            if isolated_events_path is None:
                isolated_events_path = osp.join(out_folder, f"{filename}_events")
            if self.delete_if_exists:
                self._remove(isolated_events_path)

        self.generate(
            audio_path=audiofile,
            jams_path=jamsfile,
            reverb=reverb,
            txt_path=txtfile,
            save_isolated_events=save_isolated_events,
            isolated_events_path=isolated_events_path,
            **kwargs,
        )
