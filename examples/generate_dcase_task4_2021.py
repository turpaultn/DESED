import glob

import pandas as pd
import numpy as np
import os
import scaper
import soundfile as sf
import copy
import scipy
import shutil
import random

import desed

seed = 2021
random.seed(seed)
np.random.seed(seed)


def create_non_target_fg_dir(
    meta_classes_dir, fsd50k_dir, fuss_dir, destination_folder, split="train"
):
    non_target_tsv = os.path.join(meta_classes_dir, "non_target_classes.tsv")
    mid_to_class_tsv = os.path.join(meta_classes_dir, "mid_to_class_name.tsv")
    fuss_dir_split = os.path.join(fuss_dir, "fsd_data", split, "sound")
    fuss_ids = [os.path.splitext(fname)[0] for fname in os.listdir(fuss_dir_split)]

    print("Creating non target dir ... Creating symlink from FUSS dataset")
    non_target_classes = pd.read_csv(non_target_tsv, sep="\t")
    converter = pd.read_csv(mid_to_class_tsv, sep="\t")
    fsd_gt_dev = pd.read_csv(
        os.path.join(fsd50k_dir, "FSD50K.ground_truth/dev.csv"), sep=","
    )

    # One class per row
    fsd_gt_dev["mids"] = fsd_gt_dev["mids"].str.split(",")
    fsd_gt_dev = fsd_gt_dev.explode("mids")

    # Retrieve non target classes from FUSS/FSD
    fuss_df = fsd_gt_dev[fsd_gt_dev["fname"].isin(fuss_ids)]
    non_target_fuss = fuss_df[fuss_df["mids"].isin(non_target_classes["mid"])]

    # Keep only files in the FSD corresponding set (train or valid)
    subset = "val" if split == "validation" else split
    non_target_fuss_subset = non_target_fuss[non_target_fuss["split"] == subset]

    # Move relevant non-target files
    class_list = non_target_fuss_subset["mids"].unique()
    for class_id in class_list:
        files = non_target_fuss[non_target_fuss["mids"] == class_id]["fname"]
        class_name = converter.loc[converter["mids"] == class_id, "labels"].values[
            0
        ]  # 0 because gives only one value
        out_dir = os.path.join(destination_folder, str(class_name))
        os.makedirs(out_dir, exist_ok=True)

        for file_id in files:
            fname = str(file_id) + ".wav"
            out_fname = os.path.join(out_dir, fname)
            if not os.path.exists(out_fname):
                os.symlink(
                    os.path.abspath(os.path.join(fuss_dir_split, fname)), out_fname
                )


def _create_2021_soundbank_split(
    split,
    desed_soundbank_dir,
    meta_classes_dir,
    fsd50k_dir,
    fuss_dir,
    destination_folder,
):

    non_target_fg_dir = os.path.join(
        destination_folder, "audio", split, "soundbank", "non_target_fg"
    )
    target_fg_dir = os.path.join(
        destination_folder, "audio", split, "soundbank", "fg_target"
    )
    destination_fg_tgt_ntgt_dir = os.path.join(
        destination_folder, "audio", split, "soundbank", "fg_tgt_ntgt"
    )
    destination_bg_dir = os.path.join(
        destination_folder, "audio", split, "soundbank", "background"
    )

    print(
        f"Creating 2021 soundbank (split: {split})... Creating symlinks other datasets foregrounds, backgrounds"
    )
    os.makedirs(non_target_fg_dir, exist_ok=True)
    os.makedirs(target_fg_dir, exist_ok=True)
    os.makedirs(destination_fg_tgt_ntgt_dir, exist_ok=True)
    os.makedirs(destination_bg_dir, exist_ok=True)

    # #
    # Non target foregrounds
    create_non_target_fg_dir(
        meta_classes_dir=meta_classes_dir,
        fsd50k_dir=fsd50k_dir,
        fuss_dir=fuss_dir,
        destination_folder=non_target_fg_dir,
        split=split,
    )
    # #
    # Target foregrounds
    foreground_dir_desed = os.path.join(
        desed_soundbank_dir, "audio", split, "soundbank", "foreground"
    )
    for class_name in os.listdir(foreground_dir_desed):
        if "nO" in class_name:
            out_class_dir = os.path.join(target_fg_dir, class_name.split("_nO")[0])
        else:
            out_class_dir = os.path.join(target_fg_dir, class_name)
        os.makedirs(out_class_dir, exist_ok=True)

        files = glob.glob(os.path.join(foreground_dir_desed, class_name, "*.wav"))
        for file_name in files:
            basename = os.path.basename(file_name)
            if "nO" in class_name:
                fname_suffix = "_nO" + class_name.split("_nO")[1] + ".wav"
                dest_file = os.path.join(
                    out_class_dir, os.path.splitext(basename)[0] + fname_suffix
                )
            else:
                dest_file = os.path.join(out_class_dir, basename)

            if not os.path.exists(dest_file):
                os.symlink(os.path.abspath(file_name), dest_file)

    # #
    # Foregeround target and non target grouped in a folder
    # target foregrounds from DESED
    for class_name in os.listdir(target_fg_dir):
        dest_class_dir = os.path.join(destination_fg_tgt_ntgt_dir, class_name)
        os.makedirs(dest_class_dir, exist_ok=True)

        files = glob.glob(os.path.join(target_fg_dir, class_name, "*.wav"))
        for file_name in files:
            dest_file = os.path.join(dest_class_dir, os.path.basename(file_name))
            if not os.path.exists(dest_file):
                os.symlink(os.path.abspath(file_name), dest_file)

    # foreground from FUSS
    list_classes_dir = [
        d
        for d in os.listdir(non_target_fg_dir)
        if os.path.isdir(os.path.join(non_target_fg_dir, d))
    ]
    for class_dir in list_classes_dir:
        dest_dir = os.path.join(destination_fg_tgt_ntgt_dir, class_dir)
        if not os.path.exists(dest_dir):
            os.symlink(
                os.path.abspath(os.path.join(non_target_fg_dir, class_dir)), dest_dir
            )

    # background from DESED
    background_dir = os.path.join(
        desed_soundbank_dir, "audio", split, "soundbank", "background"
    )
    # os.symlink(background_dir, destination_bg_dir)
    for rootdir, dirs, files in os.walk(background_dir):
        for subdir in dirs:
            if not os.path.exists(os.path.join(destination_bg_dir, subdir)):
                os.symlink(
                    os.path.abspath(os.path.join(rootdir, subdir)),
                    os.path.join(destination_bg_dir, subdir),
                )

    return {
        "background": destination_bg_dir,
        "fg_tgt_ntgt": destination_fg_tgt_ntgt_dir,
        "fg_target": target_fg_dir,
        "fg_non_target": non_target_fg_dir,
    }


def create_2021_soundbank(
    desed_soundbank_dir, meta_classes_dir, fsd50k_dir, fuss_dir, destination_folder
):
    """ Generate the 2021 soundbank from the dataset it is composed of. We generate symbolic links for each file
    to avoid copies.

    Args:
        desed_soundbank_dir: str, the folder of the downloaded desed soundbank.
        meta_classes_dir:
        fsd50k_dir:
        fuss_dir:
        destination_folder:

    Returns:

    """

    print(
        "Creating 2021 soundbank ... Creating symlinks from soundbank and non_target_dir"
    )
    os.makedirs(destination_folder, exist_ok=True)

    soundbank_dirs = {"soundbank": destination_folder}
    for split in ["train", "validation"]:
        soundbank_dirs[split] = _create_2021_soundbank_split(
            split,
            desed_soundbank_dir=desed_soundbank_dir,
            meta_classes_dir=meta_classes_dir,
            fsd50k_dir=fsd50k_dir,
            fuss_dir=fuss_dir,
            destination_folder=destination_folder,
        )

    return soundbank_dirs


def draw_file_nb(series_class):
    """ Get the number of fpreground events from statistics.

    Args:
        series_class: pd.Series, the statistics to draw from.

    Returns:
        int, the number of events.
    """
    # from scaper
    trunc_min = series_class["min"]
    trunc_max = series_class["max"]
    sigma = series_class["std"]
    mu = series_class["mean"]
    a, b = (trunc_min - mu) / float(sigma), (trunc_max - mu) / float(sigma)
    sample = scipy.stats.truncnorm.rvs(a, b, mu, sigma)
    return np.int(np.around(np.array(sample).item()))


def get_checked_event_parameters(sc, event_parameters):
    """ Adapt the event_parameters to the foreground chosen.
    Args:
        sc: scaper.Scaper object.
        event_parameters: dict, the original event_parameters to give to sc.add_event().

    Returns:
        dict, the modified event_parameters to give to sc.add_event().
    """
    mod_event_parameters = copy.deepcopy(event_parameters)
    event = sc._instantiate_event(sc.fg_spec[0])
    mod_event_parameters["label"] = ("const", event.label)
    mod_event_parameters["source_file"] = ("const", event.source_file)
    file_duration = sf.info(event.source_file).duration
    mod_event_parameters["event_duration"] = ("const", file_duration)
    if "_nOn_nOff" in event.source_file:
        src_time = np.random.uniform(np.maximum(file_duration - sc.duration, 0))
        mod_event_parameters["source_time"] = ("const", src_time)
        mod_event_parameters["event_time"] = ("const", 0)
        mod_event_parameters["event_duration"] = ("const", sc.duration)
    elif "_nOn" in event.source_file:
        src_time = np.random.uniform(np.maximum(file_duration - sc.duration, 0))
        event_duration = np.minimum(sc.duration, file_duration - src_time)
        mod_event_parameters["source_time"] = ("const", src_time)
        mod_event_parameters["event_time"] = ("const", 0)
        mod_event_parameters["event_duration"] = ("const", event_duration)
    elif "_nOf" in event.label:
        event_duration_min = mod_event_parameters["event_time"][3]
        event_time = np.random.uniform(
            max(0, sc.duration - file_duration, sc.duration - event_duration_min)
        )
        mod_event_parameters["event_time"] = ("const", event_time)
        mod_event_parameters["event_duration"] = ("const", sc.duration - event_time)
    return mod_event_parameters


def add_bg(sc):
    """ Choose a background and add it to a scaper object (check the duration).
    Args:
        sc: scaper.Scaper, a scaper object to add a background to.

    Returns:
        scaper.Scaper object with the background added.

    """
    sc.add_background(
        label=("choose", []), source_file=("choose", []), source_time=("const", 0)
    )
    bg_instance = sc._instantiate()["annotations"][0]["data"][0][2]
    bg_file = bg_instance["source_file"]
    bg_lbl = bg_instance["label"]
    file_duration = sf.info(bg_file).duration
    sc.reset_bg_event_spec()
    sc.add_background(
        label=("const", bg_lbl),
        source_file=("const", bg_file),
        source_time=("uniform", 0, file_duration - sc.duration),
    )
    return sc


def instantiate_soundscape(
    sc, event_parameters, event_dist, stats_events_per_file, event_cooc
):
    """ Instantiate a soundscape without generating it. Allows to control the different parameters needed for the
    soundscape.

    Args:
        sc: scaper.Scaper object.
        event_parameters: dict, the parameters to give to sc.add_event()
        event_dist: pd.DataFrame, an "event_class" column associated to an "event_prob" column to get distribution
            of initial class in each soundscapes.
        stats_events_per_file: pd.DataFrame, the stats of number of events depending on the initial class in the
            soundscape.
        event_cooc: pd.DataFrame, the proba of co-occurence of each events (not just the initial ones).

    Returns:
        scaper.Scaper object instantiated with the soundscape to create.
    """
    events_list = {}
    sc.reset_bg_event_spec()
    sc.reset_fg_event_spec()
    tgt_classes = event_dist["event_class"].tolist()
    # normalize according to present classes
    tgt_dist = event_dist["event_prob"] / event_dist["event_prob"].sum()
    tgt_dist = tgt_dist.tolist()

    event_parameters["label"] = ("choose_weighted", tgt_classes, tgt_dist)
    sc.add_event(**event_parameters)
    events_list[0] = get_checked_event_parameters(sc, event_parameters)
    event_class = events_list[0]["label"][1]

    class_stats = stats_events_per_file.loc[stats_events_per_file["event_class"] == event_class].iloc[0]
    nb_events = draw_file_nb(class_stats)
    event_cooc = event_cooc[event_class]
    event_cooc_dist = (
        event_cooc.to_frame()
        .reset_index()
        .rename(columns={"label": "event_class", event_class: "event_prob"})
    )
    classes = event_cooc_dist["event_class"].tolist()

    # normalize according to present classes
    event_cooc_dist = (
        event_cooc_dist["event_prob"] / event_cooc_dist["event_prob"].sum()
    )
    event_cooc_dist = event_cooc_dist.tolist()

    event_parameters["label"] = ("choose_weighted", classes, event_cooc_dist)

    # Instantiate the event to sample concrete values
    for i in range(1, nb_events):
        # Add a an event based on the probabilistic template
        sc.reset_fg_event_spec()
        sc.add_event(**event_parameters)
        events_list[i] = get_checked_event_parameters(sc, event_parameters)

    sc.reset_fg_event_spec()
    for i in range(len(events_list)):
        event_parameters = events_list[i]
        sc.add_event(**event_parameters)

    sc = add_bg(sc)
    return sc


def sort_sources(sources_folder, target_classes):
    """ Sort the sources of each soundscape into subfolders (targets, non_targets, background)
    Args:
        sources_folder: str, the folder in which the sources have been extracted.
        target_classes: list, the list of target classes.

    Returns:

    """
    print("|".join(target_classes))
    for file_id in os.listdir(sources_folder):
        file_sources_dir = os.path.join(sources_folder, file_id)
        df = pd.DataFrame(os.listdir(file_sources_dir), columns=["src_id"])
        df = df[df["src_id"].str.split("[.]").str[1].isin(["wav"])]
        targets = df[df["src_id"].str.contains("|".join(target_classes))]
        bg = df[df["src_id"].str.split("[_.]").str[0].isin(["background0"])]
        tgt_dir = os.path.join(file_sources_dir, ("targets"))
        non_tgt_dir = os.path.join(file_sources_dir, ("non_targets"))
        bg_dir = os.path.join(file_sources_dir, ("background"))
        if not os.path.exists(tgt_dir):
            os.mkdir(tgt_dir)
        if not os.path.exists(non_tgt_dir):
            os.mkdir(non_tgt_dir)
        if not os.path.exists(bg_dir):
            os.mkdir(bg_dir)
        for file in targets["src_id"]:
            shutil.move(os.path.join(file_sources_dir, file), tgt_dir)
        for file in bg["src_id"]:
            shutil.move(os.path.join(file_sources_dir, file), bg_dir)
        df = pd.DataFrame(os.listdir(file_sources_dir), columns=["src_id"])
        df = df[df["src_id"].str.split("[_.]").str[2].isin(["wav"])]
        for file in df["src_id"]:
            shutil.move(os.path.join(file_sources_dir, file), non_tgt_dir)


def generate_soundscapes(
    n_soundscapes,
    target_nb_events,
    event_cooc,
    fg_path,
    bg_path,
    out_dcase2021_soundscapes,
    out_sources_dir=None,
    out_metadata_tsv=None,
    target_classes=['Alarm_bell_ringing', 'Blender', 'Cat', 'Dishes', 'Dog', 'Electric_shaver_toothbrush',
                    'Frying', 'Running_water', 'Speech', 'Vacuum_cleaner']
):
    """ Generate soundscapes for 2021 set

    Args:
        n_soundscapes: int, number of soundscapes to be generated.
        target_nb_events: pd.DataFrame, a dataframe containing the number of events, and their stats (mean, min, etc..),
            it is used to compute the probas per class.
        event_cooc: pd.DataFrame, a dataframe containing the co-occurence of events to have in the dataset.
        fg_path: str, the path to the foreground folder to use (contains subfolders for each class)
        bg_path: str, the path to the background folder to use (contains subfolders for each class)
        out_dcase2021_soundscapes: str, the path to the folder which will contain the output soundscapes and their
            informations (.wav, .jams and .txt)
        out_sources_dir: str, the path to the folder which will contain the sources (the background/foregrounds files)
            of each soundscapes in the format to be added (padding, snr, etc. applied)
        out_metadata_tsv: str, the path to the output metadata (.tsv) file containing the labels of the soundscapes.
        target_classes: list, the list of target classes to keep in the metadata tsv file, the other classes are
            discarded.

    Returns:

    """

    os.makedirs(out_dcase2021_soundscapes, exist_ok=True)
    if out_sources_dir is not None:
        os.makedirs(out_sources_dir, exist_ok=True)

    events_probas = target_nb_df[["event_class"]]
    events_probas["event_prob"] = target_nb_df["count"] / target_nb_df["count"].sum()

    classes = os.listdir(fg_path)
    classes = event_cooc.columns.intersection(classes).tolist()
    event_cooc = event_cooc[event_cooc["label"].isin(classes)]
    event_cooc.set_index("label", inplace=True)
    event_cooc = event_cooc[classes]
    classes_event_dist = events_probas[
        events_probas["event_class"].isin(classes)
    ].reset_index(drop=True)

    # Soundscapes parameters
    ref_db = -50
    duration = 10.0
    event_time_dist = "truncnorm"
    event_time_mean = 5.0
    event_time_std = 2.0
    event_time_max = 10.0

    source_time_dist = "const"
    source_time = 0.0

    event_duration_min = 0.25

    snr_dist = "uniform"
    snr_min = 6
    snr_max = 30

    pitch_dist = "uniform"
    pitch_min = -3.0
    pitch_max = 3.0

    time_stretch_dist = "uniform"
    time_stretch_min = 1
    time_stretch_max = 1

    sc = scaper.Scaper(duration, fg_path, bg_path, random_state=seed)
    sc.protected_labels = []
    sc.ref_db = ref_db

    event_parameters = {
        "label": ("choose", ([])),
        "source_file": ("choose", []),
        "source_time": (source_time_dist, source_time),
        "event_time": (
            event_time_dist,
            event_time_mean,
            event_time_std,
            event_duration_min,
            event_time_max,
        ),
        "event_duration": ("const", 0.1),
        "snr": (snr_dist, snr_min, snr_max),
        "pitch_shift": (pitch_dist, pitch_min, pitch_max),
        "time_stretch": (time_stretch_dist, time_stretch_min, time_stretch_max),
    }

    # Generated soundscapes
    for i in range(n_soundscapes):

        events = instantiate_soundscape(
            sc, event_parameters, classes_event_dist, target_nb_events, event_cooc
        )

        audiofile = os.path.join(out_dcase2021_soundscapes, f"{i:d}.wav")
        jamsfile = os.path.join(out_dcase2021_soundscapes, f"{i:d}.jams")
        txtfile = os.path.join(out_dcase2021_soundscapes, f"{i:d}.txt")

        if out_sources_dir is not None:
            save_isolated_events = True
            isolated_events_path = os.path.join(out_sources_dir, "{:d}".format(i))
        else:
            save_isolated_events = False
            isolated_events_path = None

        _ = events.generate(
            audiofile,
            jamsfile,
            allow_repeated_label=True,
            allow_repeated_source=True,
            reverb=0.1,
            disable_sox_warnings=True,
            no_audio=False,
            txt_path=txtfile,
            save_isolated_events=save_isolated_events,
            isolated_events_path=isolated_events_path,
        )

    if out_sources_dir is not None:
        sort_sources(classes_event_dist, target_classes)

    if out_metadata_tsv is not None:
        list_jams = glob.glob(os.path.join(out_folder, "*.jams"))
        metadata_df = desed.generate_df_from_jams(list_jams)
        metadata_df = metadata_df[metadata_df.event_label.isin(target_classes)]
        metadata_df.to_csv(out_metadata_tsv, sep="\t", index=False, float_format="%.3f")


if __name__ == "__main__":
    bdir = "../data"
    # Existing/downloaded paths
    desed_soundbank_folder = os.path.join(bdir, "soundbank")
    fsd50k_folder = os.path.join(bdir, "fsd50k")
    fuss_folder = os.path.join(bdir, "FUSS")
    # Sepcific dcase21
    meta_classes_folder = os.path.join(bdir, "meta_infos")

    # Download if not exists the different datasets
    if not os.path.exists(desed_soundbank_folder):
        desed.download_desed_soundbank(desed_soundbank_folder)
    if not os.path.exists(fsd50k_folder):
        desed.download_fsd50k(fsd50k_folder, gtruth_only=True)
    if not os.path.exists(fuss_folder):
        desed.download_fuss(fuss_folder)

    if not os.path.exists(meta_classes_folder):
        url_meta = (
            "https://zenodo.org/record/4568876/files/meta_infos_2021.tar.gz?download=1"
        )
        desed.download.download_and_unpack_archive(url_meta, meta_classes_folder)

    # Output paths
    dcase21_soundbank_folder = os.path.join(bdir, "dcase2021", "soundbank")
    dcase21_dataset_folder = os.path.join(bdir, "dcase2021", "dataset")

    # Just in case the desed soundbank is not splitted into train/validation yet
    if not os.path.exists(os.path.join(desed_soundbank_folder, "audio", "validation")):
        desed.download.split_desed_soundbank_train_val(desed_soundbank_folder)

    # #########
    # Organise soundbank
    # #########
    sb_paths = create_2021_soundbank(
        desed_soundbank_dir=desed_soundbank_folder,
        meta_classes_dir=meta_classes_folder,
        fsd50k_dir=fsd50k_folder,
        fuss_dir=fuss_folder,
        destination_folder=dcase21_soundbank_folder,
    )

    # ############
    # Create soundscapes
    # ############
    target_nb_df = pd.read_csv(
        os.path.join(meta_classes_folder, "target_nb.tsv"), sep="\t"
    )
    event_cooc_df = pd.read_csv(
        os.path.join(meta_classes_folder, "event_cooc.tsv"), sep="\t"
    )

    for split_subset in ["train", "validation"]:
        number = 10000 if split_subset == "train" else 2500

        fg_folder = sb_paths[split_subset]["fg_tgt_ntgt"]
        # fg_folder = sb_paths[split]["fg_target"]
        bg_folder = sb_paths[split_subset]["background"]

        # sources_folder = os.path.join(dcase21_dataset_folder, "audio", split, "synthetic21_" + split, "sources")
        sources_folder = None
        out_folder = os.path.join(
            dcase21_dataset_folder,
            "audio",
            split_subset,
            "synthetic21_" + split_subset,
            "soundscapes",
        )
        out_tsv = os.path.join(
            dcase21_dataset_folder,
            "metadata",
            split_subset,
            "synthetic21_" + split_subset,
            "soundscapes.tsv",
        )

        generate_soundscapes(
            number,
            target_nb_events=target_nb_df,
            event_cooc=event_cooc_df,
            fg_path=fg_folder,
            bg_path=bg_folder,
            out_dcase2021_soundscapes=out_folder,
            out_sources_dir=sources_folder,
            out_metadata_tsv=out_tsv
        )