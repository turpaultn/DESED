# Desed dataset
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Domestic environment sound event detection (DESED). 
Mix of real and synthetic data. (used in DCASE 2019 task 4).

*If you use this dataset, do not hesitate to update [the list](#listpapers) of papers below with your paper by doing 
a pull request. 
And please cite our papers in your work*

#### Requirements:
**python >= 3.6**, scaper >= 1.0.3, dcase-util >= 0.2.5, youtube-dl >= 2019.4.30, soundfile >= 0.10.1, 
numpy >= 1.15.4, pandas >= 0.24.0

**To use the code, clone the repo, and launch `pip install -e .` in the `DESED/` folder.**

### Links
Website: [https://project.inria.fr/desed/][website]

Zenodo datasets: [DESED_synthetic][desed-synthetic], [DESED_public_eval][desed-public-eval]

Papers:
* [Turpault et al.][paper-description] Description of DESED dataset + official results of DCASE 2019 task 4. 
* [Serizel et al.][paper-eval] Robustness of DCASE 2019 systems on synthetic evaluation set.

## Description
There are 3 different datasets: Real data, synthetic data, and evaluation data.

Link to the zenodo repos: **[DESED_synthetic][desed-synthetic]**, **[DESED public eval][desed-public-eval]**

*Common point of the different datasets: contain an audio folder and a metadata folder associated 
(they can all be grouped together)*

This repo allows you: 
* Download real data.
* Download synthetic data of Desed dataset (+ generated for dcase 2019 task 4) 
* Create new synthetic data (by generating new mixtures using [Scaper][scaper] [[1]](#1)).
* Download the public evaluation set (defined as Youtube in dcase 2019, Vimeo data is not available)

DESED dataset is for now composed of 10 event classes in domestic environment.
<p align="center">
<img src="./img/DESED_house_small.png" width="50%">
</p>

**Overview**:
* Real data:
	* Verified and unverfied subset of [Audioset][audioset].
		* Unlabel_in_domain data: Unverified data have their label discarded: *14412 files*.
		* Weakly labeled data: training data have their labels verified at the clip level: *1578 files*.
		* Validation data have their labels with time boundaries (strong labels): *1168 files*.
		* Evaluation public files: 692 Youtube files (to be released soon ...) 
* Synthetic data:
	* Background files are extracted from SINS [[2]](#2), MUSAN [[3]](#3) or Youtube and have been selected because they 
	contain a very low amount of our sound event classes.
	* Foreground files are extracted from Freesound [[4]](#4)[[5]](#5) and manually verified to check the quality 
	and segmented to remove silences.
	* Mixtures are described in [Generating new synthetic data](#generating-new-synthetic-data) below.
	* Sound bank:
		* Training: *2060 background files* (SINS) and *1009 foreground files* (Freesound).
		* Eval: *12* (Freesound) + *5* (Youtube) *background files* and *314 foreground files* (Freesound). 

* DCASE 2019
	* It uses synthetic data, real data, and public evaluation data (known as youtube eval) during the challenge.
	* If you want more information about dcase 2019 dataset visit [DCASE 2019 task 4 web page][website-dcase]
	* If you only want to download dcase2019 files, go to [dcase2019 task 4](#dcase2019-task-4).
	
![][img-desed2019]

## 1. Real data

### 1.1 Download 
#### 1.1.1 Training and validation
* Download the real data
	* Clone this repo
	* `pip install -e .`
	* `cd real/code`
	* `python download_real.py`
* To reproduce the dcase2019 dataset
	* Copy `audio/` and `metadata/` in `dcase2019/dataset/` 

* Get the missing files: Send a mail with the csv files in the `missing_files` folder to
[Nicolas](mailto:nicolas.turpault@inria.fr) (and [Romain](mailto:romain.serizel@loria.fr))

#### 1.1.2 Public evaluation
The evaluation data are in the following repo: **[DESED_public_eval][desed-public-eval]**.

It corresponds to "youtube" subset in the [desed eval paper][paper-description].

* Download DESED_public_eval.tar.gz
* `tar -xzvf DESED_public_eval.tar.gz`
* To move it to dcase2019, merge `dataset/` with `dcase2019/dataset`.

*Note: the Vimeo subset in [desed eval paper][paper-description] is not available.*

## 2. Synthetic data

### 2.1 Download
##### 2.1.1 *User who just wants to download the dcase2019 synthetic evaluation set*
	* Download `DESED_synth_eval_dcase2019.tar.gz` from **[DESED_synthetic][desed-synthetic]**.
	* `DESED_synth_eval_dcase2019.tar.gz` to extract it.

##### 2.1.2 *User who wants to reproduce dcase2019 dataset* (smaller download (when distortion would be in python))
	* clone this repo
	* `pip install -e .` (if not already done)
	* `cd synthetic/`
	* `sh create_dcase2019_dataset.sh`. (Recommended to run commands line by line in case of bugs)
	* Be careful, the distortions done on Matlab are up to you to create, it will be updated later to do it in python. 
	For now, uncomment corresponding lines in `create_dcase2019_dataset.sh` to download the eval set 
	to get the distortions data. 
	
##### 2.1.3 *User who wants to create new synthetic data*
	* clone this repo
	* `pip install -e .` (if not already done)
	* Download `DESED_synth_soundbank.tar.gz` from **[DESED_synthetic][desed-synthetic]**.
	* `tar -xzvf DESED_synth_soundbank.tar.gz` to extract it.
	* `cd synthetic/code`
	* `python get_background_training.py` to download SINS background files.
	* See examples of code to create files in this repo in `synthetic/code`. 
	Described in [Generating new synthetic data](#gendata) below.
	
<a id="gendata"></a>
### 2.2 Generating new synthetic data
![generate][img-soundbank]

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

*Note: The training soundbank can be divided in a training/validation soundbank if you want to create validation data*

### After downloading architecture
**After downloading the data (see below) you should have this tree:**
```
├── real                                   
│   ├── audio
│   │   ├── train
│   │   │   ├── unlabel_in_domain
│   │   │   └── weak
│   │   └── validation
│   ├── metadata
│   │   ├── train
│   │   └── validation
│   └── code
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
    └── code                                    (Example of code to regenerate the dcase2019 dataset or generate new mixtures)
```

## DCASE2019 task 4
#### Download
Recommended to open `synthetic/create_dcase2019_dataset.sh` and 
`real/create_dcase2019_dataset.sh` and launch line by line in case of bugs.

Otherwise launch `sh create_dcase2019_dataset.sh`.

#### Description of Desed for dcase2019 task 4
[DCASE 2019 task 4 web page][website-dcase]

* **Real data**
	* **Training**: 1578 weakly labeled clips, 14412 unlabeled clips
	* **Public Evaluation**: 692 Youtube files (reported as "eval youtube" in papers)
	* **Challenge Evaluation**: Youtube and Vimeo files.

* **Synthetic**
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
dcase2019/
└── dataset
    ├── audio
    │   ├── eval
    │   │   ├── 500ms
    │   │   ├── 5500ms
    │   │   ├── 9500ms
    │   │   ├── fbsnr_0dB
    │   │   ├── fbsnr_15dB
    │   │   ├── fbsnr_24dB
    │   │   ├── fbsnr_30dB
    │   │   ├── ls_0dB
    │   │   ├── ls_15dB
    │   │   └── ls_30dB
    │   ├── train
    │   │   ├── synthetic
    │   │   ├── unlabel_in_domain
    │   │   └── weak
    │   └── validation
    └── metadata
        ├── eval
        ├── train
        └── validation
```

## FAQ
* Why don't we have a single dataset repository ?

The synthetic data or real data can be used independently for different purposes. One can create new synthetic data and
evaluate his system on synthetic data only to focus on a specific problem.

* Why audio is not always included in the repository ?

Because of licenses issues. (Example of SINS in the training soundbank)
We do not have the problem for evaluation data because we try to overcome the problem after running into this issue.

* I have a problem downloading the real dataset. How do I do ?
If you're in a country with youtube restrictions, you can try to use a VPN and the --proxy option from youtube-dl.
You can also try to upgrade youtube-dl since it is regularly updated. Finally, if you succeeded to download most of the files, you can send the missing files as stated before in this page.

* How do I evaluate and compare my system with other methods using this dataset ?

In [this paper][paper-description] you can refer to the column 'Youtube' and for further study, you can
cite the DESED public evaluation set. 

Feel free to add your paper in the list below if you use the dataset and have a result on the public evaluation set:

<a id="listpapers">List of papers using the dataset:</a>
* [Turpault et al.][paper-description]
* [Serizel et al.][paper-eval]


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

[audioset]: https://research.google.com/audioset/index.html
[desed-synthetic]: https://zenodo.org/record/3588151
[desed-public-eval]: https://zenodo.org/record/3588172
[img-desed2019]: ./img/desed_block_diagram.png
[img-soundbank]: ./img/soundbank_diagram.png
[paper-eval]: https://hal.inria.fr/hal-02355573
[paper-description]: https://hal.inria.fr/hal-02160855
[scaper]: https://github.com/justinsalamon/scaper
[website]: https://project.inria.fr/desed/
[website-dcase]: http://dcase.community/challenge2019/task-sound-event-detection-in-domestic-environments
