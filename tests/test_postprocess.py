import glob
import os.path as osp
import os
import pandas as pd
import shutil

import pytest
from desed.post_process import post_process_txt_labels, rm_high_polyphony, get_data

absolute_dir_path = os.path.abspath(os.path.dirname(__file__))


def test_postprocessing():
    """ Test the preprocessing method
    Returns:
    Should output Fixed 3 problems
    """
    folder = osp.join(absolute_dir_path, "material", "post_processing")
    checked_folder = osp.join(absolute_dir_path, "generated", "post_processing")
    out_tsv = osp.join(absolute_dir_path, "generated", "post.tsv")

    post_process_txt_labels(folder, output_folder=checked_folder, output_tsv=out_tsv)
    df = pd.read_csv(out_tsv, sep="\t")
    print(df.to_dict())
    valid_df = pd.DataFrame(
        {
            "filename": {
                0: "5.wav",
                1: "5.wav",
                2: "7.wav",
                3: "7.wav",
                4: "7.wav",
                5: "7.wav",
                6: "7.wav",
                7: "7.wav",
            },
            "onset": {
                0: 0.008,
                1: 4.969,
                2: 2.183,
                3: 2.406,
                4: 3.099,
                5: 3.406,
                6: 3.684,
                7: 6.406,
            },
            "offset": {
                0: 5.546,
                1: 9.609,
                2: 2.488,
                3: 5.2,
                4: 3.36,
                5: 6.2,
                6: 5.624,
                7: 10.0,
            },
            "event_label": {
                0: "Cat",
                1: "Speech",
                2: "Dishes",
                3: "Speech",
                4: "Dishes",
                5: "Cat",
                6: "Dishes",
                7: "Frying",
            },
        }
    )
    check = df.round(3).sort_values("onset").reset_index(
        drop=True
    ) == valid_df.sort_values("onset").reset_index(drop=True)

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


def test_get_data():
    txt_file = osp.join(absolute_dir_path, "material", "post_processing", "5.txt")
    df, length_sec = get_data(
        osp.join(absolute_dir_path, "material", "post_processing", "7.jams")
    )
    assert length_sec is None
    assert (
        (
            df.round(3)
            == pd.DataFrame.from_dict(
                {
                    0: [2.183, 2.488, "Dishes"],
                    1: [3.099, 3.360, "Dishes"],
                    2: [3.684, 5.624, "Dishes"],
                    3: [6.406, 10.000, "Frying"],
                },
                orient="index",
                columns=["onset", "offset", "event_label"],
            )
        )
        .all()
        .all()
    )
    df, length_sec = get_data(txt_file)
    assert length_sec is None
    assert (
        (
            df.round(3)
            == pd.read_csv(
                txt_file, sep="\t", names=["onset", "offset", "event_label"]
            ).round(3)
        )
        .all()
        .all()
    )
    with pytest.raises(NotImplementedError) as e:
        get_data(
            osp.join(absolute_dir_path, "material", "post_processing", "5.txt"),
            background_label="label",
        )
