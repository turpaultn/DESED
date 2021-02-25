# -*- coding: utf-8 -*-
import functools
import glob
import logging
import time
import argparse
import os.path as osp
import pandas as pd
from pprint import pformat

from desed.generate_synthetic import SoundscapesGenerator
from desed.utils import create_folder, modify_fg_onset, modify_jams
from desed.post_process import rm_high_polyphony, post_process_txt_labels
from desed.logger import create_logger
import config as cfg

# Minimal working example to test the instantiate event
import scaper
if __name__ == '__main__':
    LOG = create_logger(__name__, terminal_level=logging.INFO)
    LOG.info(__file__)
    t = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_folder', type=str,
                        default=osp.join(cfg.audio_path_eval, 'soundscapes_generated_var_onset'))
    parser.add_argument('--out_tsv_folder', type=str,
                        default=osp.join(cfg.meta_path_eval, 'soundscapes_generated_var_onset'))
    parser.add_argument('--number', type=int, default=1000)
    parser.add_argument('--fg_folder', type=str, default=osp.join(cfg.audio_path_eval, "soundbank", "foreground_on_off"))
    parser.add_argument('--bg_folder', type=str, default=osp.join(cfg.audio_path_eval, "soundbank", "background"))
    args = parser.parse_args()
    pformat(vars(args))

    # General output folder, in args
    base_out_folder = args.out_folder
    create_folder(base_out_folder)

    out_tsv_folder = args.out_tsv_folder
    create_folder(out_tsv_folder)

    # ################
    # Varying onset of a single event
    # ###########

    # SCAPER SETTINGS
    sg = SoundscapesGenerator(duration=10.0,
                              fg_folder=args.fg_folder,
                              bg_folder=args.bg_folder)
    n_soundscapes = args.number

    # source_time_dist = 'const'
    # source_time = 0.0
    #
    # event_duration_dist = 'uniform'
    # event_duration_min = 0.25
    # event_duration_max = 10.0
    #
    # snr_dist = 'uniform'
    # snr_min = 6
    # snr_max = 30
    #
    # pitch_dist = 'uniform'
    # pitch_min = -3.0
    # pitch_max = 3.0
    #
    # time_stretch_dist = 'uniform'
    # time_stretch_min = 1
    # time_stretch_max = 1
    #
    # event_time_dist = 'truncnorm'
    # event_time_mean = 0.5
    # event_time_std = 0.25
    # event_time_min = 0.25
    # event_time_max = 0.750

    parameters_event_template = {
        "source_time": ('const', 0.0),
        "event_time": ("truncnorm", 0.5, 0.25, 0.25, 0.75),
        "event_duration": ("uniform", 0.25, 10.),
        "snr": ("uniform", 6, 30),
        'pitch_shift': ("uniform", -3., 3.),
        "time_stretch": ("const", 1)
    }

    bg_parameters_template = {
        "label": ("choose", []),
        "source_file": ("choose", []),
        "source_time": ("const", 0)
    }

    out_folder_500 = osp.join(base_out_folder, "500ms")
    create_folder(out_folder_500)

    sc_obj = scaper.Scaper(duration=20.0, fg_path=args.fg_folder,  bg_path=args.bg_folder)
    bg_parameters_template = {
        "label": ("choose", []),
        "source_file": ("choose", []),
        "source_time": ("const", 0)
    }
    bg_parameters = bg_parameters_template.copy()
    sc_obj.add_background(**bg_parameters)
    bg = sc_obj._instantiate_event(sc_obj.bg_spec[0], isbackground=True, allow_repeated_source=True)
    sc_obj.reset_bg_event_spec()



    # for cnt in range(number):
    #     self.logger.debug('Generating soundscape: {:d}/{:d}'.format(cnt + 1, number))
    #     # create a scaper
    #     n_events = self.random_state.randint(min_events, max_events + 1)
    #
    #     if start_from + cnt < 10:
    #         filename = "0" + str(start_from + cnt)
    #     else:
    #         filename = str(start_from + cnt)
    #
    #     sc = Soundscape(self.duration, self.fg_folder, self.bg_folder, self.ref_db, self.samplerate,
    #                     random_state=self.random_state, delete_if_exists=self.delete_if_exists)
    #     sc.generate_one_bg_multi_fg(out_folder=out_folder,
    #                                 filename=filename,
    #                                 n_fg_events=n_events,
    #                                 **params,
    #                                 txt_file=txt_file,
    #                                 save_isolated_events=save_isolated_events,
    #                                 bg_labels=bg_labels,
    #                                 **kwargs)
    #     if cnt % 200 == 0:
    #         self.logger.info(f"generating {cnt} / {number} files (updated every 200)")
    #
    #
    # # sg.generate(n_soundscapes, out_folder_500,
    # #             min_events=1, max_events=1, labels=('choose', []),
    # #             source_files=('choose', []),
    # #             sources_time=(source_time_dist, source_time),
    # #             events_start=(
    # #                 event_time_dist, event_time_mean, event_time_std, event_time_min, event_time_max),
    # #             events_duration=(event_duration_dist, event_duration_min, event_duration_max),
    # #             snrs=(snr_dist, snr_min, snr_max),
    # #             pitch_shifts=(pitch_dist, pitch_min, pitch_max),
    # #             time_stretches=(time_stretch_dist, time_stretch_min, time_stretch_max),
    # #             txt_file=True)
    #
    # rm_high_polyphony(out_folder_500, 2)
    # out_tsv = osp.join(out_tsv_folder, "500ms.tsv")
    # post_process_txt_labels(out_folder_500, output_folder=out_folder_500,
    #                         output_tsv=out_tsv)
    #
    # # Generate 2 variants of this dataset
    # jams_to_modify = glob.glob(osp.join(out_folder_500, "*.jams"))
    # # Be careful, if changing the values of the added onset value,
    # # you maybe want to rerun the post_processing_annotations to be sure there is no inconsistency
    #
    # # 5.5s onset files
    # out_folder_5500 = osp.join(base_out_folder, "5500ms")
    # add_onset = 5.0
    # modif_onset_5s = functools.partial(modify_fg_onset, slice_seconds=add_onset)
    # modify_jams(jams_to_modify, modif_onset_5s, out_folder_5500)
    # # we also need to generate a new DataFrame with the right values
    # df = pd.read_csv(out_tsv, sep="\t")
    # df["onset"] += add_onset
    # df["offset"] = df["offset"].apply(lambda x: min(x, add_onset))
    # df.to_csv(osp.join(out_tsv_folder, "5500ms.tsv"),
    #           sep="\t", float_format="%.3f", index=False)
    #
    # # 9.5s onset files
    # out_folder_9500 = osp.join(base_out_folder, "9500ms")
    # add_onset = 9.0
    # modif_onset_5s = functools.partial(modify_fg_onset, slice_seconds=add_onset)
    # modify_jams(jams_to_modify, modif_onset_5s, out_folder_5500)
    # df = pd.read_csv(out_tsv, sep="\t")
    # df["onset"] += add_onset
    # df["offset"] = df["offset"].apply(lambda x: min(x, add_onset))
    # df.to_csv(osp.join(out_tsv_folder, "9500ms.tsv"),
    #           sep="\t", float_format="%.3f", index=False)