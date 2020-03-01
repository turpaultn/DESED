import json
import os
import pandas as pd
from desed.generate_synthetic import SoundscapesGenerator, generate_tsv_from_jams, generate_files_from_jams

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
    sg.generate_by_label_occurence(params, 10, out_dir)


def test_generate_tsv_from_jams():
    list_jams = [os.path.join(absolute_dir_path, "material", "5.jams")]
    generated_tsv = os.path.join(absolute_dir_path, "generated", "generated_from_jams.tsv")
    generate_tsv_from_jams(list_jams, generated_tsv)
    df_gen = pd.read_csv(generated_tsv, sep="\t")
    df_mat = pd.read_csv(os.path.join(absolute_dir_path, "material", "generated_from_jams.tsv"), sep="\t")
    assert df_gen == df_mat


def test_generate_files_from_jams():
    generate_files_from_jams([os.path.join(absolute_dir_path, "material", "5.jams")],
                             os.path.join(absolute_dir_path, "generated", "generated_from_jams"))
