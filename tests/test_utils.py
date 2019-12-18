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
from desed.utils import post_processing_annotations, rm_high_polyphony


def test_postprocessing(folder, checked_folder, out_csv):
    """ Test the preprocessing method
    Returns:
    Should output Fixed 3 problems
    """
    post_processing_annotations(folder, output_folder=checked_folder,
                                output_csv=out_csv)
    df = pd.read_csv(out_csv, sep="\t")
    print(df.to_dict())
    valid_df = pd.DataFrame({'filename': {0: 'material/post_processing/5.wav',
                                              1: 'material/post_processing/5.wav',
                                              2: 'material/post_processing/7.wav',
                                              3: 'material/post_processing/7.wav',
                                              4: 'material/post_processing/7.wav',
                                              5: 'material/post_processing/7.wav',
                                              6: 'material/post_processing/7.wav',
                                              7: 'material/post_processing/7.wav'},
                                 'onset': {0: 0.008, 1: 4.969, 2: 2.183, 3: 2.406,
                                           4: 3.099, 5: 3.406, 6: 3.684, 7: 6.406},
                                 'offset': {0: 5.546, 1: 9.609, 2: 2.488, 3: 5.2,
                                         4: 3.36, 5: 6.2, 6: 5.624, 7: 10.0},
                                 'event_label': {0: 'Cat', 1: 'Speech', 2: 'Dishes', 3: 'Speech',
                                           4: 'Dishes', 5: 'Cat', 6: 'Dishes', 7: 'Frying'}}
                            )
    check = (df.round(3) == valid_df)

    assert check.all(axis=None), "Problem with post_processing_annotations"


def test_high_polyphony(folder, n_pol):
    rm_high_polyphony(folder, max_polyphony=n_pol)


if __name__ == '__main__':
    pol_dir = osp.join("generated", "polyphony")
    if osp.exists(pol_dir):
        shutil.rmtree(pol_dir)
    shutil.copytree(osp.join("material", "post_processing"), pol_dir)
    ll = glob.glob(osp.join(pol_dir, "*.jams"))
    assert len(ll) == 2
    test_high_polyphony(pol_dir, 2)
    ll = glob.glob(osp.join(pol_dir, "*.jams"))
    assert len(ll) == 1, f"Problem rm_high_polyphony {len(ll)} != 1"
    test_postprocessing(osp.join("material", "post_processing"), osp.join("generated", "post_processing"),
                        out_csv=osp.join("generated", "post.csv"))
