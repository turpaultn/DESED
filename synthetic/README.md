# Desed_synthetic
Synthetic data. (used in DCASE 2019 task 4).

Recreate dcase 2019 task 4 synthetic data or create new mixtures.

#### Requirements:
**python >= 3.6**, scaper >= 1.0.3,
numpy >= 1.15.4, pandas >= 0.24.0

## Description
This repository gives the information and the code to download the synthetic data, 
reproduce the dataset used in DCASE 2019 task 4 and examples of how you can create your own data 
(using [Scaper](https://github.com/justinsalamon/scaper) [[1]](#1)).

You can find information about this dataset in this paper: [link](https://hal.inria.fr/hal-02160855).
The evaluation part was submitted to ICASSP and will be updated later.

Overview:
* Background files are extracted from SINS [[2]](#2), MUSAN [[3]](#3) or Youtube and have been selected because they 
contain a very low amount of our sound event classes.
* Foreground files are extracted from Freesound [[4]](#4)[[5]](#5) and manually verified to check the quality 
and segmented to remove silences.
* Mixtures are described in [Generating new synthetic data](#gendata) below.
* Sound bank:
	* Training: *2060 background files* (SINS) and *1009 foreground files* (Freesound).
	* Eval: *12* (Freesound) + *5* (Youtube) *background files* and *314 foreground files* (Freesound). 


If you want to reproduce dcase 2019 dataset go to [**Desed for DCASE 2019 task 4**](#dcase2019) below, 
the download part is explained again.

##### Synthetic data (multiple kind of users), this is copied from the README of the repo

* *User who just wants to download dcase2019 dataset*
	* Download `DESED_synth_dcase2019.tar.gz` from **[DESED_synthetic](https://zenodo.org/record/3565667)**.
	* `tar -xzvf DESED_synth_dcase2019.tar.gz` to extract it.

* *User who wants to reproduce dcase2019 dataset* (smaller download)
	* Download `DESED_synth_dcase2019jams.tar.gz` from **[DESED_synthetic](https://zenodo.org/record/3565667)**.
	* `tar -xzvf DESED_synth_dcase2019jams.tar.gz` to extract it.
	* Download `DESED_synth_soundbank.tar.gz` from **[DESED_synthetic](https://zenodo.org/record/3565667)**.
	* `tar -xzvf DESED_synth_soundbank.tar.gz` to extract it.
	* `sh create_dcase2019_dataset.sh`. (Recommended to run commands line by line in case of bugs)
	* Be careful, the distortions done on Matlab are up to you to create, it will be updated later to do it in python.
	
* *User who wants to create new synthetic data*
	* Download `DESED_synth_soundbank.tar.gz ` from **[DESED_synthetic](https://zenodo.org/record/3565667)**.
	* `tar -xzvf DESED_synth_soundbank.tar.gz ` to extract it.
	* `cd synthetic/src`
	* `python get_background_training.py` to download SINS background files.
	* See examples of code to create files in this repo in `synthetic/src`. 
	Described in [Generating new synthetic data](#gendata) below.

### After downloading architecture
**After downloading the data (see below) you should have this tree:**
```
└── synthetic
    ├── audio
    │   ├── eval
    │   │   ├── distorted_fbsnr_30dB            (6 subfolders for each distortion, audio are directly given because a matlab code has been used to generate them) 
    │   │   └── soundbank                       (Raw (bank of) data that can be used to create synthetic data)
    │   │       ├── background                  (2 subfolders, youtube and freesound)
    │   │       ├── background_long             (5 subfolders)
    │   │       ├── foreground                  (18 subfolders)
    │   │       ├── foreground_on_off           (10 subfolders)
    │   │       └── foreground_short            (5 subfolders)
    │   └── train
    │       ├── soundbank                       (Raw (bank of) data that can be used to create synthetic data)
    │       │   ├── background
    │       │   │   └── sins                    (Has to be downloaded by: get_background_training.py)
    │       │   └── foreground                  (14 subfolders)
    │       └── synthetic
    ├── metadata
    │   ├── eval
    │   │   └── soundscapes                     (metadata to reproduce the wav files used in dcase2019)
    │   │       ├── 500ms
    │   │       ├── 5500ms
    │   │       ├── 9500ms
    │   │       ├── fbsnr_0dB
    │   │       ├── fbsnr_15dB
    │   │       ├── fbsnr_24dB
    │   │       ├── fbsnr_30dB
    │   │       ├── ls_0dB
    │   │       ├── ls_15dB
    │   │       └── ls_30dB
    │   └── train
    │       └── soundscapes                     (metadata to reproduce the wav files used in dcase2019)
    └── src                                     (Source code to regenerate the dcase2019 dataset or generate new mixtures)
```

## Generating new synthetic data, this is copied from the README of the repo
<a id="gendata"></a>
 To generate new sounds, in the same way as the Desed_synthetic dataset, you can use these files:
 * `generate_training.py`, uses `event_occurences_train.json` for co-occurrence of events.
 * `generate_eval_FBSNR.py` generates similar subsets with different foreground-background sound to noise ratio (fbsnr): 30dB, 24dB, 15dB, 0dB.
 Uses `event_occurences_eval.json` for occurence and co-occurrence of events.  
 * `generate_eval_var_onset.py` generates subsets with a single event per file, the difference between subsets is
  the onset position:
    1. Onset between 0.25s and 0.75s. 
    2. Onset between 5.25s and 5.75s. 
    3. Onset between 9.25s and 9.75s.
 * `generate_eval_long_short.py` generates subsets with a long event in the background and short events in the foreground, 
 the difference beteen subsets is the FBSNR: 30dB, 15dB, 0dB. 
 * `generate_eval_distortion.py` generates distortion subsets, not yet in python, 
 see `generate_eval_distortion.m` for matlab code (will be updated later).

When a script is generating multiple subfolder but only one csv file, it means it is the same csv for the different cases.
Example: when modifying the FBSNR, we do not change the labels (onset, offsets). 

##### Description of Desed for dcase2019 task 4
[DCASE 2019 task 4 web page](http://dcase.community/challenge2019/task-sound-event-detection-in-domestic-environments)

* **Training**: There are 2060 background files from SINS and 1009 foreground from Freesound.
We generated 2045 10s files with a FBSNR between 6dB to 30dB.
* **Evaluation**: 	There are 12 (Freesound) + 5 (Youtube) background files and 314 foreground files. 
Generating different subsets to test robustness against some parameters.

	Taking a background sound and multiple foreground sounds and associating them in different conditions:
	* Varying the foreground-background signal to noise ratio (FBSNR).
	* Varying the onsets: Generating foreground sounds only at the beginning, middle or end of the 10 seconds.
	* Using long 'foreground' event classes as background, and short events as foreground. 
	* Degrading the final 10s mixtures.


** After running the script `create_dcase2019_dataset.sh`, you should have a folder called `dcase2019`in that way**
```
└── dcase2019
    ├── dataset
    │   ├── audio
    │   │   ├── eval
    │   │   │   ├── 500ms
    │   │   │   ├── 5500ms
    │   │   │   ├── 9500ms
    │   │   │   ├── distorted_clipping
    │   │   │   ├── distorted_drc
    │   │   │   ├── distorted_highpass_filter
    │   │   │   ├── distorted_lowpass_filter
    │   │   │   ├── distorted_smartphone_playback
    │   │   │   ├── distorted_smartphone_recording
    │   │   │   ├── fbsnr_0dB
    │   │   │   ├── fbsnr_15dB
    │   │   │   ├── fbsnr_24dB
    │   │   │   ├── fbsnr_30dB
    │   │   │   ├── ls_0dB
    │   │   │   ├── ls_15dB
    │   │   │   └── ls_30dB
    │   │   ├── train
    │   │   │   └── synthetic
    │   │   └── validation
    │   └── metadata
    │       ├── eval
    │       └── train
    └── src
```


## Licenses
The python code is publicly available under the MIT license, see the LICENSE file. 
The matlab code is taken from the Audio degradation toolbox [[6]](#6), see the LICENSE file.

The different datasets contain a license file at their root for the attribution of each file.

The different platform used are: Freesound [[4]](#4)[[5]](#5), Youtube, MUSAN [[3]](#3) and SINS [[2]](#2).  

## Citing
If you use this repository, please cite this paper:
N. Turpault, R. Serizel, A. Parag Shah, J. Salamon. 
Sound event detection indomestic environments with weakly labeled data and soundscape synthesis. 
Workshop on Detectionand Classification of Acoustic Scenes and Events, Oct 2019, New York City, USA.

## References
<a id="1">[1]</a> J. Salamon, D. MacConnell, M. Cartwright, P. Li, and J. P. Bello. Scaper: A library for soundscape synthesis and augmentation
In IEEE Workshop on Applications of Signal Processing to Audio and Acoustics (WASPAA), New Paltz, NY, USA, Oct. 2017.

<a id="2">[2]</a> Gert Dekkers, Steven Lauwereins, Bart Thoen, Mulu Weldegebreal Adhana, Henk Brouckxon, Toon van Waterschoot, Bart Vanrumste, Marian Verhelst, and Peter Karsmakers.
The SINS database for detection of daily activities in a home environment using an acoustic sensor network.
In Proceedings of the Detection and Classification of Acoustic Scenes and Events 2017 Workshop (DCASE2017), 32–36. November 2017.

<a id="3">[3]</a> David Snyder and Guoguo Chen and Daniel Povey.
MUSAN: A Music, Speech, and Noise Corpus.
arXiv, 1510.08484, 2015.

<a id="4">[4]</a> F. Font, G. Roma & X. Serra. Freesound technical demo. In Proceedings of the 21st ACM international conference on Multimedia. ACM, 2013.
 <a id="5">[5]</a> E. Fonseca, J. Pons, X. Favory, F. Font, D. Bogdanov, A. Ferraro, S. Oramas, A. Porter & X. Serra. Freesound Datasets: A Platform for the Creation of Open Audio Datasets.
In Proceedings of the 18th International Society for Music Information Retrieval Conference, Suzhou, China, 2017.

 <a id="5">[6]</a> M. Mauch and S. Ewert, “The Audio Degradation Toolbox and its Application to Robustness Evaluation”. 
In Proceedings of the 14th International Society for Music Information Retrieval Conference (ISMIR 2013), Curitiba, Brazil, 2013.

