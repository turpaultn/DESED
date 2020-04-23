import json
import os
import pandas as pd
import soundfile as sf
from desed.generate_synthetic import SoundscapesGenerator, generate_tsv_from_jams, generate_files_from_jams

absolute_dir_path = os.path.abspath(os.path.dirname(__file__))
fg_folder = os.path.join(absolute_dir_path, "material", "soundbank", "foreground")
bg_folder = os.path.join(absolute_dir_path, "material", "soundbank", "background")

sg = SoundscapesGenerator(1, fg_folder, bg_folder, random_state=2020)


def test_generate_simple():
    out_dir = os.path.join(absolute_dir_path, "generated", "soundgenerator", "simple")
    os.makedirs(out_dir, exist_ok=True)
    sg.generate(2, out_dir, txt_file=False)


def test_generate_balance():
    out_dir = os.path.join(absolute_dir_path, "generated", "soundgenerator", "simple")
    os.makedirs(out_dir, exist_ok=True)
    sg.generate_balance(2, out_dir, min_events=1, max_events=1, bg_labels=["label"])


def test_generate_per_label_occurence():
    out_dir = os.path.join(absolute_dir_path, "generated", "soundgenerator", "simple")
    os.makedirs(out_dir, exist_ok=True)
    event_occur_pth = os.path.join(absolute_dir_path, "material", "event_occurences", "event_occurences_train.json")
    with open(event_occur_pth) as json_file:
        co_occur_dict = json.load(json_file)
    sg.generate_by_label_occurence(co_occur_dict, 2,
                                   out_dir)


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
    assert (df_gen == df_mat).all().all()  # all on DataFrame and then on Series


def test_generate_files_from_jams():
    generate_files_from_jams([os.path.join(absolute_dir_path, "material", "5.jams")],
                             os.path.join(absolute_dir_path, "generated", "generated_from_jams"))


def test_random_state():
    rand_dir = os.path.join(absolute_dir_path, "generated", "random_state")
    rand_dir_rep = os.path.join(absolute_dir_path, "generated", "random_state_rep")
    sgrs = SoundscapesGenerator(10, fg_folder, bg_folder, random_state=2020)
    sgrs.generate(2, rand_dir)
    sgrs_rep = SoundscapesGenerator(10, fg_folder, bg_folder, random_state=2020)
    sgrs_rep.generate(2, rand_dir_rep)
    list_files = [os.path.join(rand_dir, "00.wav"), os.path.join(rand_dir, "01.wav")]
    list_files_rep = [os.path.join(rand_dir_rep, "00.wav"), os.path.join(rand_dir_rep, "01.wav")]
    for i in range(len(list_files)):
        aud, sr = sf.read(list_files[i])
        aud_r, sr_r = sf.read(list_files_rep[i])
        assert (aud == aud_r).all()
        assert sr == sr_r


def test_randomness():
    rand_dir = os.path.join(absolute_dir_path, "generated", "random")
    rand_dir_rep = os.path.join(absolute_dir_path, "generated", "random_rep")
    sgr = SoundscapesGenerator(1, fg_folder, bg_folder)
    sgr.generate(2, rand_dir, min_events=2, max_events=2,
                 events_start=('uniform', 0, 1), sources_time=[("const", 0), ("const", 0)])
    sgr_rep = SoundscapesGenerator(1, fg_folder, bg_folder)
    sgr_rep.generate(2, rand_dir_rep, min_events=2, max_events=2,
                     events_start=('uniform', 0, 1), sources_time=[0, 0])
    list_files = [os.path.join(rand_dir, "00.wav"), os.path.join(rand_dir, "01.wav")]
    list_files_rep = [os.path.join(rand_dir_rep, "00.wav"), os.path.join(rand_dir_rep, "01.wav")]
    for i in range(len(list_files)):
        aud, sr = sf.read(list_files[i])
        aud_r, sr_r = sf.read(list_files_rep[i])
        assert (aud != aud_r).any()
        assert sr == sr_r
test_randomness()