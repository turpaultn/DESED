import json
import os
from desed.soundscape import Soundscape


absolute_dir_path = os.path.abspath(os.path.dirname(__file__))
fg_folder = os.path.join(absolute_dir_path, "material", "soundbank", "foreground")
bg_folder = os.path.join(absolute_dir_path, "material", "soundbank", "background")
out_dir = os.path.join(absolute_dir_path, "generated", "soundscape")
os.makedirs(out_dir, exist_ok=True)

sc = Soundscape(1, fg_folder, bg_folder, random_state=2020, delete_if_exists=True)


def test_generate_simple():
    sc.add_random_background()
    for label in ["label", "label_nOn", "label_nOff", "label_nOn_nOff"]:
        sc.add_fg_event_non_noff(label)
    audio_path = os.path.join(out_dir, "soundscape_test.wav")
    jams_path = os.path.join(out_dir, "soundscape_test.jams")
    sc.generate(audio_path, jams_path, save_isolated_events=True)


def test_generate_from_json():
    param_json = os.path.join(absolute_dir_path, "material",
                              "event_occurences", "event_occurences_train.json")
    with open(param_json) as json_file:
        params = json.load(json_file)
    sc.generate_co_occurence(params["label"]["co-occurences"], "label", out_dir, "0")
