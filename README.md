<p align="center">
	<a href="https://project.inria.fr/desed/" rel="desed website"><img src="./img/Desed.png" alt="desed-logo" /></a>
</p>

# Desed dataset
Domestic environment sound event detection (DESED) dataset utilities. 
Mix of recorded and synthetic data (used in DCASE task 4 since 2019).

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)


*If you use this dataset, do not hesitate to update [the list](#list-of-papers-and-code-using-desed) 
of papers below with your paper by doing a pull request. 
If you use and like this work, you can [cite it](#citing-us) :blush:*

**Table of contents**
  - [Links](#links)
  - [Description](#description)
  - [Recorded soundscapes](#1-recorded-soundscapes-aka-real-data)
    - [Download](#11-download)
      - [Training and validation](#111-training-and-validation)
      - [Public evaluation](#112-public-evaluation)
  - [Synthetic soundbank/soundscapes](#2-synthetic-soundbanksoundscapes)
    - [Download soundbank](#21-download-soundbank)
    - [Soundscapes (existing set or generate new)](#22-soundscapes-existing-set-or-generate-new)
  - [DCASE Task 4](#dcase-task-4)
    - [Download](#download)
    - [Description](#description-of-dcase-2019-and-2020)
  - [Important updates](#important-updates)
  - [List of papers/code using DESED](#list-of-papers-and-code-using-desed)
  - [FAQ](#faq)
  - [Citing us](#citing-us)
  - [References](#references)
      
## Installation
#### Recommended install
Take into account your changes of the code in the `desed/` folder.
- `git clone https://github.com/turpaultn/DESED`
- `cd DESED`
- `pip install -e .`

*In this case, all your changes in `desed` folder will be taken into account*

#### Use desed in other projects
Copying code from `synthetic/code/` or `real/code/` folders without changing `desed/` content
- `pip install desed@git+https://github.com/turpaultn/DESED`


## Links
* Website: [https://project.inria.fr/desed/][website]
* Zenodo datasets: [DESED_synthetic][desed-synthetic], [DESED_public_eval][desed-public-eval]
* Papers:
	* [Turpault et al.][paper-description] Description of DESED dataset + official results of DCASE 2019 task 4. 
	* [Serizel et al.][paper-eval] Robustness of DCASE 2019 systems on synthetic evaluation set.

## Description
There are 3 different datasets: 
* Recorded soundscapes (a.k.a., real). 
* Synthetic soundbank + DCASE task 4 soundscapes: [DESED_synthetic][desed-synthetic]
* Public evaluation (recorded soundscapes) (a.k.a., Youtube in DCASE19, Vimeo is not available): [DESED public eval][desed-public-eval]

*All these datasets contain an "audio" folder associated with a "metadata" folder 
so they can all be grouped together by merging them*

This repo allows you: 
* Download the three datasets (different methods).
* Create new synthetic soundscapes from synthetic soundbank (generate new mixtures using [Scaper][scaper] [[1]](#1)).

DESED dataset is for now composed of 10 event classes in domestic environment.
<p align="center">
<img src="./img/DESED_house_small.png" width="50%">
</p>

**Overview**:
* Recorded soundscapes:
	* Verified and unverfied subset of [Audioset][audioset].
		* Unlabel_in_domain data: Unverified data have their label discarded: *14412 files*.
		* Weakly labeled data: training data have their labels verified at the clip level: *1578 files*.
		* Validation data have their labels with time boundaries (strong labels): *1168 files*.
		* Evaluation public files: 692 Youtube files (to be released soon ...) 
* Synthetic soundbank:
	* Background files are extracted from SINS [[2]](#2), MUSAN [[3]](#3) or Youtube and have been selected because they 
	contain a very low amount of our sound event classes.
	* Foreground files are extracted from Freesound [[4]](#4)[[5]](#5) and manually verified to check the quality 
	and segmented to remove silences.
	* Mixtures are described in [Generating new synthetic soundscapes](#gendata) below.
	* Soundbank:
		* Training: *2060 background files* (SINS) and *1009 foreground files* (Freesound).
		* Eval: *12* (Freesound) + *5* (Youtube) *background files* and *314 foreground files* (Freesound). 

* DCASE 2019
	* It uses synthetic soundbank, recorded soundscapes, and public evaluation data (a.k.a., Youtube eval during DCASE19).
	* If you want more information about DCASE19 dataset visit [DCASE 2019 task 4 web page][website-dcase19-t4]
	* If you only want to download DCASE19 files, go to [dcase2019 task 4](#dcase2019-task-4).
	
![dcase19-diagram][img-desed2019]

## 1. Recorded soundscapes (a.k.a., Real data)
### 1.1 Download
#### 1.1.1 Training and validation
See instructions in the [real folder][real_folder].

### 1.1.2 Public evaluation
The evaluation data are in the following repo: **[DESED_public_eval][desed-public-eval]**.

It corresponds to "youtube" subset in the [desed eval paper][paper-description].

* Download DESED_public_eval.tar.gz
* `tar -xzvf DESED_public_eval.tar.gz`
* To move it to dcase2019, merge `dataset/` with `dcase2019/dataset`.

*Note: the Vimeo subset in [desed eval paper][paper-description] is not available.*


## 2. Synthetic soundbank/soundscapes
![soundbank-diagram][img-soundbank]

### 2.1 Download soundbank
See in [./desed/desed/download_soundbank.py] for more options
```python
import desed
desed.download_soundbank("./")
```

See instructions in the [synthetic folder][synthetic_folder].

<a id="gendata"></a>
### 2.2 Soundscapes (existing set or generate new)

See instructions in the [synthetic folder][synthetic_folder].

#### Folders structure after download
After downloading the data (see below) you should have this tree:
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
    │       └── synthetic                       (Generated soundscapes)
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


## DCASE task 4

### Download
#### DCASE19 task 4
Recommended to open `synthetic/create_dcase2019_dataset.sh` and 
`real/create_dcase2019_dataset.sh` and launch line by line in case of bugs.

Otherwise launch `sh create_dcase2019_dataset.sh`.

#### DCASE20 Task 4
Recorded (real) soundscapes are similar 2019.

Recommended to open `synthetic/create_dcase2020_dataset.sh` and 
`real/create_dcase2019_dataset.sh` and launch line by line in case of bugs.

Otherwise launch `sh create_dcase2020_dataset.sh`.

### Description of dcase 2019 and 2020

DESED is the full set in DCASE 2019 task 4 but only a subset of DCASE 2020 task 4 dataset (FUSS is the other part).
The task is dealing on sound event detection using DESED, and on source separation using a dataset provided by Google.
See [DCASE 2020 task 4 web page][website-dcase20-t4] for more info.

* **Recorded soundscapes**
    * **Training**: 1578 weakly labeled clips, 14412 unlabeled clips.
    * **Validation**: 1168 strongly labeled clips.
    * **Public Evaluation**: 692 Youtube files (reported as "eval youtube" in papers).
    * **Challenge Evaluation**: Youtube and Vimeo files.

* **Synthetic** 2019
    * **Training**: There are 2060 background files from SINS and 1009 foreground from Freesound.
      We generated 2045 10s files with a FBSNR between 6dB to 30dB.
    * **Evaluation**: 	There are 12 (Freesound) + 5 (Youtube) background files and 314 foreground files.
      Generating different subsets to test robustness against some parameters.

      Taking a background sound and multiple foreground sounds and associating them in different conditions:
        * Varying the foreground-background signal to noise ratio (FBSNR).
        * Varying the onsets: Generating foreground sounds only at the beginning, middle or end of the 10 seconds.
        * Using long 'foreground' event classes as background, and short events as foreground.
        * Degrading the final 10s mixtures.

* **Synthetic** 2020
	* **Training**: There are 2060 background files from SINS and 1009 foreground from Freesound.
	We generated 2584 10s files with a FBSNR between 6dB to 30dB. Files are reverberated using 
	room impulse responses (RIR) from [FUSS][fuss_zenodo] dataset.
	* **Evaluation**: 	There are 12 (Freesound) + 5 (Youtube) background files and 314 foreground files. 

After running the script `create_dcase2019_dataset.sh`, you should have a folder called `dcase2019`.
After running the script `create_dcase2020_dataset.sh`, you should have a folder called `dataset`.
Organised in that way:
```
dataset
├── audio
│   ├── train
│   │   ├── synthetic20 (called synthetic in 2019)
│	│   │   └── soundscapes
│   │   ├── unlabel_in_domain
│   │   └── weak
│   └── validation
└── metadata
    ├── eval
    ├── train
    └── validation
```

** After running the script `create_dcase2019_dataset.sh`, you should have a folder called `dcase2019`in that way**

## FAQ
* Why don't we have a single dataset repository ?

The synthetic sounbank or recorded soundscapes can be used independently for different purposes. 
For example, one can create new synthetic soundscapes and evaluate his system on synthetic data only to focus on a specific problem.

* Why audio is not always included in the repository ?

Because of licenses issues. (Example of SINS in the training soundbank)
We do not have the problem for evaluation data because we try to overcome the problem after running into this issue.

* I have a problem downloading the recorded soundscapes. How do I do ?

If you're in a country with youtube restrictions, you can try to use a VPN and the --proxy option from youtube-dl.
You can also try to upgrade youtube-dl since it is regularly updated. 
Finally, if you succeeded to download most of the files, you can send the missing files as stated in the `real/README.md.

* How do I evaluate and compare my system with other methods using this dataset ?

In [this paper][paper-description] you can refer to the column 'Youtube' and for further study, you can
cite the DESED public evaluation set. 


## List of papers and code using DESED
Feel free to add your paper in the file [list_papers_using_desed.md][list_papers_md] if you use the dataset and have a result on the public evaluation set:

<!-- include list_papers_using_desed.md -->
Paper                                                                       | Code
--------------------------------------------------------------------------- | ---------------------------
[Turpault et al.](https://hal.inria.fr/hal-02160855), DCASE workshop 2019.  | https://github.com/turpaultn/DCASE2019_task4
[Serizel et al.](https://hal.inria.fr/hal-02355573), ICASSP 2020            | https://github.com/turpaultn/DESED
[Turpault et al.](https://hal.inria.fr/hal-02467401), ICASSP 2020           | https://github.com/turpaultn/walle
[Turpault et al.](https://hal.inria.fr/hal-02891665), preprint              | https://github.com/turpaultn/dcase20_task4/tree/papers_code
[Turpault et al.](https://hal.inria.fr/hal-02891700), preprint              | https://github.com/turpaultn/dcase20_task4/tree/papers_code


<!-- end -->

*Note: to add it to README.md before doing the pull request, run `python generate_table.py`*

## Important updates
- 7th December 2020, v1.2.2, ease the download of soundbank (with or without pre-split validation)
- 23th April 2020, v1.2.0, update the generation procedure (`add_fg_event_non_noff`) to use all parts of files longer than 
the duration of the soundscapes created + Add possibility to use only background from certain labels (i.e: sins or tut).
- 18th March 2020, v.1.1.7, update DESED_synth_dcase20_train_jams.tar of DESED_synth. They use pitch shifting, 
while the others didn't. These are the final JAMS used for dcase2020 baseline. Also commenting reverb since not used 
for the baseline.


## Licenses
The python code is publicly available under the MIT license, see the LICENSE file. 
The matlab code is taken from the Audio degradation toolbox [[6]](#6), see the LICENSE file.

The different datasets contain a license file at their root for the attribution of each file.

The different platform used are: Freesound [[4]](#4)[[5]](#5), Youtube, MUSAN [[3]](#3) and SINS [[2]](#2).  

##  Citing us
If you use this repository, like it, and you want to cite us, please cite these papers:

- N. Turpault, R. Serizel, A. Parag Shah, J. Salamon. 
Sound event detection indomestic environments with weakly labeled data and soundscape synthesis. 
Workshop on Detectionand Classification of Acoustic Scenes and Events, Oct 2019, New York City, USA.

- R. Serizel, N. Turpault, A. Shah, J. Salamon. 
Sound event detection in synthetic domestic environments. 
ICASSP, May 2020, Barcelona, Spain.

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

<a id="5">[5]</a> E. Fonseca, J. Pons, X. Favory, F. Font, D. Bogdanov, A. Ferraro, S. Oramas, A. Porter & X. Serra. 
Freesound Datasets: A Platform for the Creation of Open Audio Datasets.
In Proceedings of the 18th International Society for Music Information Retrieval Conference, Suzhou, China, 2017.

 <a id="5">[6]</a> M. Mauch and S. Ewert, “The Audio Degradation Toolbox and its Application to Robustness Evaluation”. 
In Proceedings of the 14th International Society for Music Information Retrieval Conference (ISMIR 2013), Curitiba, Brazil, 2013.

[audioset]: https://research.google.com/audioset/index.html
[desed-logo]: ./img/Desed.png
[desed-synthetic]: https://zenodo.org/record/3702397
[desed-public-eval]: https://zenodo.org/record/3588172
[fuss_zenodo]: https://zenodo.org/record/3694384/
[img-desed2019]: ./img/desed_block_diagram.png
[img-soundbank]: ./img/soundbank_diagram.png
[list_papers_md]: ./list_papers_using_desed.md
[paper-description]: https://hal.inria.fr/hal-02160855
[paper-eval]: https://hal.inria.fr/hal-02355573
[paper-turpault-icassp20]: https://hal.inria.fr/hal-02467401
[real_folder]: ./real
[scaper]: https://github.com/justinsalamon/scaper
[synthetic_folder]: ./synthetic
[website]: https://project.inria.fr/desed/
[website-dcase19-t4]: http://dcase.community/challenge2019/task-sound-event-detection-in-domestic-environments
[website-dcase20-t4]: http://dcase.community/challenge2020/task-sound-event-detection-and-separation-in-domestic-environments
