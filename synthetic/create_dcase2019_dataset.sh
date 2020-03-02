#!/bin/bash

# Change with your own environment
CONDA_ENV=python
# Create directory, and copy data in right folders to have a unique directory with dcase2019 data
ROOTDIR=$(realpath ../dcase2019/dataset)
mkdir -p ${ROOTDIR}

cd ..
echo "Download and extract soundbank"
wget -O DESED_synth_soundbank.tar.gz https://zenodo.org/record/3571305/files/DESED_synth_soundbank.tar.gz?download=1
tar -xzvf DESED_synth_soundbank.tar.gz
cd synthetic

cd code
# If you did not download the synthetic training background yet
echo "Download SINS..."
${CONDA_ENV} get_background_training.py
cd ..

# Get jams file
wget -O DESED_synth_dcase2019jams.tar.gz https://zenodo.org/record/3571305/files/DESED_synth_dcase2019jams.tar.gz?download=1
tar -xzvf DESED_synth_dcase2019jams.tar.gz

# To download distortions evaluation data.
#echo "Temporary... everything except distortions will be overwritten, comment the 2 next lines if distortions not needed"
#wget -O DESED_synth_eval_dcase2019.tar.gz https://zenodo.org/record/3571305/files/DESED_synth_eval_dcase2019.tar.gz?download=1
#tar -xzvf DESED_synth_eval_dcase2019.tar.gz

# Download and generate synthetic
cd code
echo "generate synthetic data from jams ... ~30min"
${CONDA_ENV} generate_wav_from_jams19.py
cd ..

# Metadata
mkdir -p ${ROOTDIR}/metadata/train
mkdir -p ${ROOTDIR}/metadata/eval
mv metadata/train/soundscapes/*.csv ${ROOTDIR}/metadata/train/
mv metadata/eval/soundscapes/*.csv ${ROOTDIR}/metadata/eval/

# Audio
mkdir -p ${ROOTDIR}/audio/train
mkdir -p ${ROOTDIR}/audio/eval
mv audio/train/synthetic/ ${ROOTDIR}/audio/train/
mv audio/eval/soundscapes/* ${ROOTDIR}/audio/eval/

