# -*- coding: utf-8 -*-
import os.path as osp

import pytest
import functools
import glob
import os
import jams
import json
import pandas as pd

from desed.soundscape import Soundscape
from desed.utils import create_folder, pprint, choose_cooccurence_class
from desed.utils import change_snr, modify_fg_onset, modify_jams
from desed.utils import download_file

absolute_dir_path = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture()
def rm_folder():
    os.removedirs(os.path.join(absolute_dir_path, "generated"))


def test_create_folder():
    to_create = os.path.join(absolute_dir_path, "generated", "tmp")
    create_folder(to_create)
    create_folder(to_create)


def test_pprint():
    pprint("Bonjour")


def test_choose_class():
    param_json = osp.join(absolute_dir_path, "material",
                          "event_occurences", "event_occurences_train.json")
    with open(param_json) as json_file:
        params = json.load(json_file)
    label = choose_cooccurence_class(params["label"]["co-occurences"])
    assert label in ["label", "label_nOn", "label_nOff", "label_nOn_nOff"], "Wrong class given"


def test_choose_class_random_state():
    param_json = osp.join(absolute_dir_path, "material",
                          "event_occurences", "event_occurences_train.json")
    with open(param_json) as json_file:
        params = json.load(json_file)
    label = choose_cooccurence_class(params["label"]["co-occurences"], random_state=2)
    label_rep = choose_cooccurence_class(params["label"]["co-occurences"], random_state=2)
    assert label == label_rep, "Random state not working, having different values"


def test_choose_file():
    sc = Soundscape(1, os.path.join(absolute_dir_path, "material", "soundbank", "foreground"),
                    os.path.join(absolute_dir_path, "material", "soundbank", "background"),
                    random_state=2020, delete_if_exists=True)
    label_pth = os.path.join(absolute_dir_path, "material", "soundbank", "background", "label")
    fpath = os.path.join(absolute_dir_path, "material", "soundbank", "background", "label", "noise-free-sound-0055.wav")
    assert sc._choose_file(label_pth) == fpath


def test_modify_bg_snr():
    jam_path = os.path.join(absolute_dir_path, "material", "5.jams")
    jam_obj = change_snr(jam_path, -15)
    data = jam_obj["annotations"][0].data
    for cnt, obs in enumerate(data):
        if obs.value["role"] == "foreground":
            # Changing manually the jams to have the snr desired
            assert jam_obj["annotations"][0].data[cnt].value["snr"] == 7.396362733436883 - 15


def test_generate_new_bg_snr_files():
    out_dir = os.path.join(absolute_dir_path, "generated", "new_snr")
    list_jams = glob.glob(os.path.join(absolute_dir_path, "material", "*.jams"))
    func_modify_snr15 = functools.partial(change_snr, db_change=15)
    modify_jams(list_jams, func_modify_snr15, out_dir)


def test_fg_onset():
    jam_path = os.path.join(absolute_dir_path, "material", "5.jams")
    jam_obj = jams.load(jam_path)
    data = jam_obj["annotations"][0].data
    for cnt, obs in enumerate(data):
        if obs.value["role"] == "foreground":
            onset = obs.value["event_time"]

    jam_obj_gen = modify_fg_onset(jam_path, 0.2)
    for cnt, obs in enumerate(jam_obj_gen["annotations"][0].data):
        if obs.value["role"] == "foreground":
            onset_gen = obs.value["event_time"]

    assert onset == (onset_gen - 0.2), "Wrong onset generated"


def test_download_file():
    fname_valid = "https://zenodo.org/record/4307908/files/soundbank_validation.tsv?download=1"
    fpath = os.path.join(absolute_dir_path, "generated", "utils", "soundbank_validation.tsv")
    create_folder(osp.dirname(fpath))
    download_file(fname_valid, fpath)
    material = os.path.join(absolute_dir_path, "material", "utils", "soundbank_validation.tsv")
    df_download = pd.read_csv(fpath)
    df_material = pd.read_csv(material)
    assert df_download.equals(df_material), "Wrong file downloaded, not matching: soundbank_validation.tsv"
