# -*- coding: utf-8 -*-
import logging
import os.path as osp
import pandas as pd
import shutil
import pytest
import functools
import glob
import os
import jams
import json

from desed.logger import create_logger
from desed.soundscape import Soundscape
from desed.utils import create_folder, pprint, choose_cooccurence_class
from desed.utils import change_snr, modify_fg_onset, modify_jams
from desed.post_process import rm_high_polyphony, post_process_txt_labels

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


def test_choose_file():
    sc = Soundscape(1, os.path.join(absolute_dir_path, "material", "soundbank", "foreground"),
                    os.path.join(absolute_dir_path, "material", "soundbank", "background"),
                    random_state=2020, delete_if_exists=True)
    label_pth = os.path.join(absolute_dir_path, "material", "soundbank", "background", "label")
    fpath = os.path.join(absolute_dir_path, "material", "soundbank", "background", "label", "noise-free-sound-0055.wav")
    assert sc._choose_file(label_pth) == fpath


def test_add_event():
    fg_folder = os.path.join(absolute_dir_path, "material", "soundbank", "foreground")
    bg_folder = os.path.join(absolute_dir_path, "material", "soundbank", "background")
    sc = Soundscape(1, fg_folder, bg_folder, random_state=2020, delete_if_exists=True)
    sc.add_fg_event_non_noff("label")
    sc.add_fg_event_non_noff("label_nOff")
    sc.add_fg_event_non_noff("label_nOn")
    sc.add_fg_event_non_noff("label_nOn_nOff")
    # Todo, check it generates well with the good labels and files


def test_postprocessing():
    """ Test the preprocessing method
    Returns:
    Should output Fixed 3 problems
    """
    folder = osp.join(absolute_dir_path, "material", "post_processing")
    checked_folder = osp.join(absolute_dir_path, "generated", "post_processing")
    out_tsv = osp.join(absolute_dir_path, "generated", "post.tsv")

    post_process_txt_labels(folder, output_folder=checked_folder,
                            output_tsv=out_tsv)
    df = pd.read_csv(out_tsv, sep="\t")
    print(df.to_dict())
    valid_df = pd.DataFrame({'filename': {0: '5.wav',
                                          1: '5.wav',
                                          2: '7.wav',
                                          3: '7.wav',
                                          4: '7.wav',
                                          5: '7.wav',
                                          6: '7.wav',
                                          7: '7.wav'},
                             'onset': {0: 0.008, 1: 4.969, 2: 2.183, 3: 2.406,
                                       4: 3.099, 5: 3.406, 6: 3.684, 7: 6.406},
                             'offset': {0: 5.546, 1: 9.609, 2: 2.488, 3: 5.2,
                                        4: 3.36, 5: 6.2, 6: 5.624, 7: 10.0},
                             'event_label': {0: 'Cat', 1: 'Speech', 2: 'Dishes', 3: 'Speech',
                                             4: 'Dishes', 5: 'Cat', 6: 'Dishes', 7: 'Frying'}}
                            )
    check = (df.round(3).sort_values("onset").reset_index(drop=True) == valid_df.sort_values("onset").reset_index(drop=True))

    assert check.all(axis=None), "Problem with post_processing_txt_annotations"


def test_high_polyphony():
    pol_dir = osp.join(absolute_dir_path, "generated", "polyphony")
    if osp.exists(pol_dir):
        shutil.rmtree(pol_dir)
    shutil.copytree(osp.join(absolute_dir_path, "material", "post_processing"), pol_dir)
    ll = glob.glob(osp.join(pol_dir, "*.jams"))
    assert len(ll) == 2

    save_name = os.path.join(absolute_dir_path, "generated", "final.tsv")
    rm_high_polyphony(pol_dir, 1, save_name)

    ll = glob.glob(osp.join(pol_dir, "*.jams"))
    assert len(ll) == 1, f"Problem rm_high_polyphony {len(ll)} != 1"


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


def test_logger():
    logger = create_logger("try", terminal_level=logging.DEBUG)
    logger.debug("this can be useful if there is a bug")


if __name__ == '__main__':
    test_choose_class()
