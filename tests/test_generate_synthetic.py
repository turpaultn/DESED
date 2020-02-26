import os
import jams

from desed.generate_synthetic import modify_bg_snr, generate_new_bg_snr_files, modify_fg_onset


absolute_dir_path = os.path.abspath(os.path.dirname(__file__))


def test_modify_bg_snr():
    jam_path = os.path.join(absolute_dir_path, "material", "5.jams")
    jam_obj = modify_bg_snr(15, jam_path)
    data = jam_obj["annotations"][0].data
    for cnt, obs in enumerate(data):
        if obs.value["role"] == "background":
            # Changing manually the jams to have the snr desired
            assert jam_obj["annotations"][0].data[cnt].value["snr"] == 15


def test_generate_new_bg_snr_files():
    in_dir = os.path.join(absolute_dir_path, "material")
    out_dir = os.path.join(absolute_dir_path, "generated", "new_snr")
    generate_new_bg_snr_files(15, in_dir, out_dir)


def test_fg_onset():
    jam_path = os.path.join(absolute_dir_path, "material", "5.jams")
    jam_obj = jams.load(jam_path)
    data = jam_obj["annotations"][0].data
    for cnt, obs in enumerate(data):
        if obs.value["role"] == "foreground":
            onset = obs.value["event_time"]

    jam_obj_gen = modify_fg_onset(0.2, jam_path)
    for cnt, obs in enumerate(jam_obj_gen["annotations"][0].data):
        if obs.value["role"] == "foreground":
            onset_gen = obs.value["event_time"]

    assert onset == (onset_gen - 0.2), "Wrong onset generated"
