# Desed_real
Real data. (used in DCASE task 4 2018 and 2019).

Contains the metadata to download the real data.

**If having a problem with the download (missing files folder or something else) please contact me**

#### Requirements:
**python >= 3.6**, 
dcase-util >= 0.2.5, youtube-dl >= 2019.4.30, pysoundfile >= 0.10.1, 
numpy >= 1.15.4, pandas >= 0.24.0

## Description
This repository gives the information and the [code](https://github.com/turpaultn/DESED) to download the real data 
used in DCASE 2019 task 4 (and 2018).

You can find information about this dataset in this paper: [link](https://hal.inria.fr/hal-02160855).
The evaluation part was submitted to ICASSP and will be updated later.

Overview:
* Real Data:
	* Verified and unverfied subset of [Audioset](https://research.google.com/audioset/index.html).
		* Unverified data have their label discarded (unlabel_in_domain data).
		* Training data have their labels verified at the clip level (weak labels)
		* Validation data have their labels with time boundaries (strong labels)

## Download
* Download `DESED_real_dcase2019_meta.tar.gz` from **[DESED_real](https://zenodo.org/record/3565749)**.
* `tar -xzvf DESED_real_dcase2019_meta.tar.gz` to extract it.
* `cd dcase2019/src`
* `python download_real_data.py`
* Send a mail with the csv files in the `real_data/missing_files` folder to [nicolas](nicolas.turpault@inria.fr) 
(and [romain](romain.serizel@loria.fr))

*Note: this includes only the training and validation part, the public evaluation will be released soon*

### After downloading architecture
**After downloading the data (see below) you should have this tree:**
```
└── real_data                                   (real data part of the dataset, audio files have to be downloaded)
   ├── audio                                   (Audio downloaded by `python download_real_data.py`)
   │   ├── train
   │   │   ├── weak
   │   │   └── unlabel_in_domain
   │   └── validation
   ├── metadata                                (CSV files describing the dataset)
   │   ├── train
   │   │   ├── weak.csv
   │   │   └── unlabel_in_domain.csv
   │   └── validation
   │       ├── eval_dcase2018.csv
   │       ├── test_dcase2018.csv
   │       └── validation.csv
   ├── src                                     (Source code to download real data)
   ├── create_dcase2019_dataset.sh             (Bash command to move the audio files in the dcase2019 folder)
   └── README.md
```

## Licenses
The python code is publicly available under the MIT license, see the LICENSE file. 

## Citing
If you use this repository, please cite this paper:
N. Turpault, R. Serizel, A. Parag Shah, J. Salamon. 
Sound event detection indomestic environments with weakly labeled data and soundscape synthesis. 
Workshop on Detectionand Classification of Acoustic Scenes and Events, Oct 2019, New York City, USA.

## References
<a id="1">[1]</a> J. Salamon, D. MacConnell, M. Cartwright, P. Li, and J. P. Bello. Scaper: A library for soundscape synthesis and augmentation
In IEEE Workshop on Applications of Signal Processing to Audio and Acoustics (WASPAA), New Paltz, NY, USA, Oct. 2017.