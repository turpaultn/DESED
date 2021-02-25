# Examples to use the repo
* Real data are downloaded once and used for your models.
* Synthetic soundscapes are generated using Scaper [1](#1) and you can generate your own !

## Download

### Real data
```python
import desed
desed.download_real("./data/dataset")
```

### Soundbank
```python
import desed
desed.download_soundbank("./data/soundbank", split_train_valid=True)
```
`split_train_valid` allows to use the pregenerated split train/valid (90%/10%) next to evaluation folder.
Otherwise, you only get train and evaluation folders.

## Soundscapes
![soundbank-diagram][img-soundbank]
### Reproduce an existing set
* See `generate_dcase_task4_20XX.py` 

### Create new synthetic data*
* See `generated_soundscapes/`

*Note: the soundbank has to be downloaded*


## Generating new soundscapes

Data are generated using [Scaper][scaper].
In the following you have example of how to use it.
For more information do not hesitate to check their [docs][scaper-doc].


### Scripts to generate soundscapes
Examples of how to generate new sounds in the same way as the Desed_synthetic dataset:
 * [generate_basic_co-occurence.py], uses `event_occurences_train.json` for co-occurrence of events.
 * [generate_eval_FBSNR.py] generates similar subsets with different foreground-background sound to noise ratio (fbsnr): 30dB, 24dB, 15dB, 0dB.
 Uses `event_occurences_eval.json` for occurence and co-occurrence of events.  
 * [generate_eval_var_onset.py] generates subsets with a single event per file, the difference between subsets is
  the onset position:
    1. Onset between 0.25s and 0.75s. 
    2. Onset between 5.25s and 5.75s. 
    3. Onset between 9.25s and 9.75s.
 * [generate_eval_long_short.py] generates subsets with a long event in the background and short events in the foreground, 
 the difference beteen subsets is the FBSNR: 30dB, 15dB, 0dB. 

When a script is generating multiple audio subfolders but only one metadata TSV file, 
it means it is the same csv for the different cases.
Example: when modifying the FBSNR, we do not change the labels (onset, offsets). 

### MWE
Minimal example of usage to generate training set on default parameters:
```python
from desed import SoundscapesGenerator
from desed.post_process import rm_high_polyphony, post_process_txt_labels
import json

sg = SoundscapesGenerator(duration=10.0,
                          fg_folder="synthetic/audio/train/soundbank/foreground",
                          bg_folder="synthetic/audio/train/soundbank/foreground",
                          ref_db=-55,
                          samplerate=16000)

with open("synthetic/code/event_occurences/event_occurences_train.json") as json_file:
    co_occur_dict = json.load(json_file)
out_folder = "dataset/audio/train/generated_soundscapes"

sg.generate_by_label_occurence(label_occurences=co_occur_dict,
                               number=200,
                               out_folder=out_folder)

rm_high_polyphony(out_folder, 3)
post_process_txt_labels(out_folder, 
			output_folder=out_folder, 
			output_tsv="dataset/metadata/train/generated_soundscapes.tsv")
```

## Description of dcase task 4 2019-2020 generated soundscapes
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
      Generating different subsets, not explained in detail here.


## Licenses
The python code is publicly available under the MIT license, see the LICENSE file. 
The matlab code is taken from the Audio degradation toolbox [[6]](#6), see the LICENSE file.

The different datasets contain a license file at their root for the attribution of each file.

The different platform used are: Freesound [[4]](#4)[[5]](#5), Youtube, MUSAN [[3]](#3) and SINS [[2]](#2).  

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


[scaper]: https://github.com/justinsalamon/scaper
[scaper-doc]: https://scaper.readthedocs.io/en/latest/
[website-dcase]: http://dcase.community/challenge2019/task-sound-event-detection-in-domestic-environments


[generate_eval_FBSNR.py]: ./generate_soundscapes/generate_eval_FBSNR.py
[generate_eval_long_short.py]: ./generate_soundscapes/generate_eval_long_short.py
[generate_basic_co-occurence.py]: ./generate_soundscapes/generate_basic_co-occurence.py
[generate_eval_var_onset.py]: ./generate_soundscapes/generate_eval_var_onset.py
[img-soundbank]: ../img/soundbank_diagram.png
[readme-root]: ../README.md