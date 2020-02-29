import os
import numpy as np

import soundfile
from desed.utils import create_folder
from scaper import Scaper


absolute_dir_path = os.path.abspath(os.path.dirname(__file__))


def test_short_background_only():
    foreground_fd = os.path.join(absolute_dir_path, "material", "soundbank", "foreground")
    background_fd = os.path.join(absolute_dir_path, "material", "soundbank", "background")

    sc = Scaper(10, foreground_fd, background_fd)
    sc.add_background(("const", "label"),
                      ("const",os.path.join(background_fd, "label", "noise-free-sound-0055.wav")),
                      ("const", 0))
    fname = "test_bg"
    fpath = os.path.join(absolute_dir_path, "generated", "short_bg_scaper", fname)
    create_folder(os.path.dirname(fpath))
    sc.generate(f"{fpath}.wav", f"{fpath}.jams")

    audio_g, sr_g = soundfile.read(f"{fpath}.wav")
    audio_s, sr_s = soundfile.read(os.path.join(absolute_dir_path, "material", "scaper", f"{fname}.wav"))
    assert np.allclose(audio_g, audio_s)


def test_short_background_fg_events():
    foreground_fd = os.path.join(absolute_dir_path, "material", "soundbank", "foreground")
    background_fd = os.path.join(absolute_dir_path, "material", "soundbank", "background")
    sc = Scaper(10, foreground_fd, background_fd)
    sc.add_background(("const", "label"),
                      ("const", os.path.join(background_fd, "label", "noise-free-sound-0055.wav")),
                      ("const", 0))
    fname = "test_bg_fg"
    fpath = os.path.join(absolute_dir_path, "generated", "short_bg_scaper", fname)
    sc.add_event(("const", "label"),
                 ("const", os.path.join(foreground_fd, "label", "26104_0.wav")),
                 ("const", 0), ("const", 5), ("const", 5), ("const", 6), ("const", 0), ("const", 1))

    sc.generate(f"{fpath}.wav", f"{fpath}.jams")

    audio_g, sr_g = soundfile.read(f"{fpath}.wav")
    audio_s, sr_s = soundfile.read(os.path.join(absolute_dir_path, "material", "scaper", f"{fname}.wav"))
    assert np.allclose(audio_g, audio_s)
