import json
import os
from desed.generate_synthetic import SoundscapesGenerator

absolute_dir_path = os.path.abspath(os.path.dirname(__file__))
fg_folder = os.path.join(absolute_dir_path, "material", "soundbank", "foreground")
bg_folder = os.path.join(absolute_dir_path, "material", "soundbank", "background")

sg = SoundscapesGenerator(1, fg_folder, bg_folder, random_state=2020)


def test_generate_simple():
    out_dir = os.path.join(absolute_dir_path, "generated", "soundgenerator", "simple")
    os.makedirs(out_dir, exist_ok=True)
    sg.generate(2, out_dir)


def test_generate_from_json():
    out_dir = os.path.join(absolute_dir_path, "generated", "soundgenerator", "occurences")
    os.makedirs(out_dir, exist_ok=True)
    param_json = os.path.join(absolute_dir_path, "material",
                              "event_occurences", "event_occurences_train.json")
    with open(param_json) as json_file:
        params = json.load(json_file)
    sg.generate_by_label_occurence(params, 2, out_dir)
