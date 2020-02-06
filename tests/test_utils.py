# -*- coding: utf-8 -*-
#########################################################################
# Initial software
# Copyright Nicolas Turpault, Romain Serizel, Justin Salamon, Ankit Parag Shah, 2019, v1.0
# This software is distributed under the terms of the License MIT
#########################################################################
import os.path as osp
import pandas as pd
import shutil
import glob
import os
import json
import scaper
from desed.utils import post_processing_annotations, rm_high_polyphony, create_folder, pprint, choose_cooccurence_class,\
    choose_file, add_event
import pytest


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
    assert choose_cooccurence_class(params["Blender"]) in ["Blender", "Cat", "Dishes"], "Wrong class given"


def test_choose_file():
    label_pth = os.path.join(absolute_dir_path, "material", "soundbank", "background", "label")
    fpath = os.path.join(absolute_dir_path, "material", "soundbank", "background", "label", "noise-free-sound-0055.wav")
    assert choose_file(label_pth) == fpath


def test_add_event():
    fg_folder = os.path.join(absolute_dir_path, "material", "soundbank", "foreground")
    bg_folder = os.path.join(absolute_dir_path, "material", "soundbank", "background")
    sc = scaper.Scaper(1, fg_folder, bg_folder)
    sc = add_event(sc, "label")
    sc = add_event(sc, "label_nOff")
    sc = add_event(sc, "label_nOn")
    sc = add_event(sc, "label_nOn_nOff")
    # Todo, check it generates well with the good labels and files


def test_postprocessing():
    """ Test the preprocessing method
    Returns:
    Should output Fixed 3 problems
    """
    folder = osp.join(absolute_dir_path, "material", "post_processing")
    checked_folder = osp.join(absolute_dir_path, "generated", "post_processing")
    out_tsv = osp.join(absolute_dir_path, "generated", "post.tsv")

    post_processing_annotations(folder, output_folder=checked_folder,
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

    assert check.all(axis=None), "Problem with post_processing_annotations"


def test_high_polyphony():
    pol_dir = osp.join(absolute_dir_path, "generated", "polyphony")
    if osp.exists(pol_dir):
        shutil.rmtree(pol_dir)
    shutil.copytree(osp.join(absolute_dir_path, "material", "post_processing"), pol_dir)
    ll = glob.glob(osp.join(pol_dir, "*.jams"))
    assert len(ll) == 2

    save_name = os.path.join(absolute_dir_path, "generated", "final.tsv")
    rm_high_polyphony(pol_dir, 2, save_name)

    ll = glob.glob(osp.join(pol_dir, "*.jams"))
    assert len(ll) == 1, f"Problem rm_high_polyphony {len(ll)} != 1"


if __name__ == '__main__':
    test_add_event()
