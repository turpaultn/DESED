#!/bin/bash

wget -O DESED_synth_soundbank.tar.gz https://zenodo.org/record/3571305/files/DESED_synth_soundbank.tar.gz?download=1
tar -xzvf DESED_synth_soundbank.tar.gz

wget -O DESED_synth_dcase2019jams.tar.gz https://zenodo.org/record/3571305/files/DESED_synth_dcase2019jams.tar.gz?download=1
tar -xzvf DESED_synth_dcase2019jams.tar.gz

# To download distortions evaluation data.
#echo "Temporary... everything except distortions will be overwritten, comment the 2 next lines if distortions not needed"
#wget -O DESED_synth_eval_dcase2019.tar.gz https://zenodo.org/record/3571305/files/DESED_synth_eval_dcase2019.tar.gz?download=1
#tar -xzvf DESED_synth_eval_dcase2019.tar.gz

# Change with your own environment
CONDA_ENV=python

# Create directory, and copy data in right folders to have a unique directory with dcase2019 data
ROOTDIR=../dcase2019/dataset
mkdir -p ${ROOTDIR}

# Download and generate synthetic
cd src
# If you did not downlaod the synthetic training background yet
"Download SINS..."
${CONDA_ENV} get_background_training.py
echo "generate synthetic ... ~30min"
${CONDA_ENV} generate_wav.py
cd ..

# Metadata
mkdir -p ${ROOTDIR}/metadata/train
mkdir -p ${ROOTDIR}/metadata/eval
mv metadata/train/soundscapes/*.csv ${ROOTDIR}/metadata/train/
mv metadata/eval/soundscapes/*.csv ${ROOTDIR}/metadata/eval/

# Audio
mkdir -p ${ROOTDIR}/audio/train
mkdir -p ${ROOTDIR}/audio/eval
mv audio/train/synthetic ${ROOTDIR}/audio/train/
mv audio/eval/soundscapes/* ${ROOTDIR}/audio/eval/

