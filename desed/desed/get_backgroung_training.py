import warnings

from .download_soundbank import get_backgrounds_train


def get_background_training(basedir, sins=True, tut=False, keep_original=False):
    warnings.warn("Depreciated, use get_backgrounds_train from download_soundbank")
    get_backgrounds_train(basedir, sins, tut, keep_original)
