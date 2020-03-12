# Desed_synthetic
Synthetic data. (used in DCASE 2019/20 task 4).

Recreate dcase 2019 task 4 synthetic data or create new mixtures.

![soundbank-diagram][img-soundbank]

## Download

### 1. *User who just wants to download the dcase2019 synthetic evaluation set*
* Download `DESED_synth_eval_dcase2019.tar.gz` from **[DESED_synthetic][desed-synthetic]**.
* `DESED_synth_eval_dcase2019.tar.gz` to extract it.

### 2. *User who wants to reproduce dcase2019 dataset* (training + evaluation)
* clone this repo
* `pip install -e .` (if not already done)
* `cd synthetic/`
* `sh create_dcase2019_dataset.sh`. (Recommended to run commands line by line in case of bugs)
* Be careful, the distortions done on Matlab are up to you to create, it will be updated later to do it in python. 
For now, uncomment corresponding lines in `create_dcase2019_dataset.sh` to download the full eval set 
(including the distortions like 2.1.1).
	
### 3. *User who wants to reproduce dcase2020 dataset*
* clone this repo
* `pip install -e .` (if not already done)
* `cd synthetic/`
* `sh create_dcase2020_dataset.sh`. (Recommended to run commands line by line in case of bugs)

*Note: it also download and apply the RIRs from [fuss dataset][fuss_zenodo]*

### 4. *User who wants to create new synthetic data*
* clone this repo
* `pip install -e .` (if not already done)
* Download `DESED_synth_soundbank.tar.gz` from **[DESED_synthetic][desed-synthetic]**.
* `tar -xzvf DESED_synth_soundbank.tar.gz` to extract it.
* `cd synthetic/code`
* `python get_background_training.py` to download SINS background files.
* See examples of code to create files in this repo in `synthetic/code`. 
Described in [Generating new synthetic soundscapes](#gendata) below.


## Generating new soundscapes

Data are generated using [Scaper][scaper].
In the following you have example of how to use it.
For more information do not hesitate to check their [docs][scaper-doc].

Examples of how to generate new sounds in the same way as the Desed_synthetic dataset:
 * [generate_training.py], uses `event_occurences_train.json` for co-occurrence of events.
 * [generate_eval_FBSNR.py] generates similar subsets with different foreground-background sound to noise ratio (fbsnr): 30dB, 24dB, 15dB, 0dB.
 Uses `event_occurences_eval.json` for occurence and co-occurrence of events.  
 * [generate_eval_var_onset.py] generates subsets with a single event per file, the difference between subsets is
  the onset position:
    1. Onset between 0.25s and 0.75s. 
    2. Onset between 5.25s and 5.75s. 
    3. Onset between 9.25s and 9.75s.
 * [generate_eval_long_short.py] generates subsets with a long event in the background and short events in the foreground, 
 the difference beteen subsets is the FBSNR: 30dB, 15dB, 0dB. 
 * `generate_eval_distortion.py` generates distortion subsets, not yet in python, 
 see [generate_eval_distortion.m] for matlab code (will be updated later).
 * [generate_source_separation.py] generates soundscapes and save the isolated events to be used for source separation.

When a script is generating multiple subfolder but only one csv file, it means it is the same csv for the different cases.
Example: when modifying the FBSNR, we do not change the labels (onset, offsets). 

**Note: The training soundbank can be divided in a training/validation soundbank if you want to create validation data**

## DCASE
- 2019: see `create_dcase2019_dataset.sh` for download.
- 2020: see `create_dcase2020_dataset.sh` for download.


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


[fuss_zenodo]: https://zenodo.org/record/3694384/
[scaper]: https://github.com/justinsalamon/scaper
[scaper-doc]: https://scaper.readthedocs.io/en/latest/
[website-dcase]: http://dcase.community/challenge2019/task-sound-event-detection-in-domestic-environments


[./code/generate_eval_distortions.m]: ./code/generate_eval_distortions.m
[generate_eval_FBSNR.py]: ./code/generate_eval_FBSNR.py
[generate_eval_long_short.py]: ./code/generate_eval_long_short.py
[generate_training.py]: ./code/generate_training.py
[generate_eval_var_onset.py]: ./code/generate_eval_var_onset.py
[generate_source_separation.py]: ./code/generate_source_separation.py
[img-soundbank]: ../img/soundbank_diagram.png
[readme-root]: ../README.md