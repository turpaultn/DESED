import os.path as osp

absolute_dir_path = osp.abspath(osp.dirname(__file__))
audio_path = osp.join(absolute_dir_path, "..", "audio")
base_path_eval = osp.join(audio_path, 'eval')
base_path_train = osp.join(audio_path, 'train')
