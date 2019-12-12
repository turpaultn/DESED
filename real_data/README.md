# Desed_real
Real data. (used in DCASE task 4 2018 and 2019).

Contains the metadata to download the real data.

#### Requirements:
**python >= 3.6**, 
dcase-util >= 0.2.5, youtube-dl >= 2019.4.30, pysoundfile >= 0.10.1, 
numpy >= 1.15.4, pandas >= 0.24.0

## Description
See [DESED README][desed-readme] in previous folder.

## Download
#### Real data (all users)
* Download the real data
	* Clone this repo
	* `cd real_data/src`
	* `python download_real_data.py`
* To reproduce the dcase2019 dataset
	* Copy `audio/` and `metadata/` in `dcase2019/dataset/` 

* Get the missing files: Send a mail with the csv files in the `missing_files` folder to 
[nicolas](nicolas.turpault@inria.fr) (and [romain](romain.serizel@loria.fr))

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

## DCASE2019 task 4
#### Download
Recommended to open [create_dcase2019_dataset.sh][create2019] and launch line by line in case of bugs.

Otherwise launch `sh create_dcase2019_dataset.sh`.

See previous folder for more info.

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

[create2019]: ./create_dcase2019_dataset.sh
[desed-readme]: ../README.md#description