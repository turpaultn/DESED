import jams
import json
import os
import soundfile as sf

from desed.soundscape import Soundscape

import pytest

absolute_dir_path = os.path.abspath(os.path.dirname(__file__))
fg_folder = os.path.join(absolute_dir_path, "material", "soundbank", "foreground")
bg_folder = os.path.join(absolute_dir_path, "material", "soundbank", "background")
out_dir = os.path.join(absolute_dir_path, "generated", "soundscape")
os.makedirs(out_dir, exist_ok=True)
duration = 1


@pytest.fixture
def sc():
    soundscape = Soundscape(duration, fg_folder, bg_folder, random_state=2020, delete_if_exists=True)
    return soundscape


def test_generate_simple(sc):
    sc.add_random_background()
    for label in ["label", "label_nOn", "label_nOff", "label_nOn_nOff"]:
        sc.add_fg_event_non_noff(label)
    audio_path = os.path.join(out_dir, "soundscape_test.wav")
    jams_path = os.path.join(out_dir, "soundscape_test.jams")
    sc.generate(audio_path, jams_path, save_isolated_events=True)


def test_generate_from_json(sc):
    param_json = os.path.join(absolute_dir_path, "material",
                              "event_occurences", "event_occurences_train.json")
    with open(param_json) as json_file:
        params = json.load(json_file)
    sc.generate_co_occurence(params["label"]["co-occurences"], "label", out_dir, "0")


def get_dict_values(jams_path):
    jams_obj = jams.load(jams_path)
    ann = jams_obj.annotations.search(namespace='scaper')[0]
    assert len(ann.data) == 1
    dict_values = ann.data[0].value
    return dict_values


def test_add_label(sc):
    sc.add_fg_event_non_noff("label")
    jams_path = os.path.join(out_dir, "add_fg_label.jams")
    sc.generate(os.path.join(out_dir, "add_fg_label.wav"), jams_path, save_isolated_events=True)
    dict_values = get_dict_values(jams_path)
    assert dict_values["source_time"] == 0


def test_add_label_long(sc):
    sc.add_fg_event_non_noff("label_long")
    jams_path = os.path.join(out_dir, "add_fg_label_long.jams")
    sc.generate(os.path.join(out_dir, "add_fg_label_long.wav"), jams_path)

    dict_values = get_dict_values(jams_path)
    if dict_values["event_time"] == 0:  # offset
        assert dict_values["source_time"] > duration
        dur = sf.info(os.path.join(fg_folder, "label_long", "46129_3.wav")).duration
        if dict_values["event_duration"] == duration:  # middle
            assert duration < dict_values["source_time"] < dur
        else:
            assert round(dict_values["source_time"] + dict_values["event_duration"], 4) == round(dur, 4)
    else:  # onset
        assert dict_values["source_time"] == 0


def test_add_label_noff(sc):
    sc.add_fg_event_non_noff("label_nOff")
    jams_path = os.path.join(out_dir, "add_fg_label_nOff.jams")
    sc.generate(os.path.join(out_dir, "add_fg_label_nOff.wav"), jams_path)
    dict_values = get_dict_values(jams_path)
    assert dict_values["event_time"] + dict_values["event_duration"] == duration


def test_add_label_non(sc):
    sc.add_fg_event_non_noff("label_nOn")
    jams_path = os.path.join(out_dir, "add_fg_label_nOn.jams")
    sc.generate(os.path.join(out_dir, "add_fg_label_nOn.wav"), jams_path)
    dict_values = get_dict_values(jams_path)
    assert dict_values["event_time"] == 0


def test_add_label_non_noff(sc):
    sc.add_fg_event_non_noff("label_nOn_nOff")
    jams_path = os.path.join(out_dir, "add_fg_events.jams")
    sc.generate(os.path.join(out_dir, "add_fg_events.wav"), jams_path)
    dict_values = get_dict_values(jams_path)
    assert dict_values["event_time"] == 0
    assert dict_values["event_duration"] == duration
