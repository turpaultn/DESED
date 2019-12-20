import os.path as osp

absolute_dir_path = osp.abspath(osp.dirname(__file__))
audio_path = osp.join(absolute_dir_path, "..", "audio")
meta_path = osp.join(absolute_dir_path, "..", "metadata")

audio_path_eval = osp.join(audio_path, 'eval')
meta_path_eval = osp.join(meta_path, 'eval')
audio_path_train = osp.join(audio_path, 'train')
meta_path_train = osp.join(meta_path, 'train')
