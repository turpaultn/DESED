#!/bin/bash

# Change with your own environment
CONDA_ENV=python
# Will put dcase2020 dataset in this folder
ROOTDIR=$(realpath ../dataset)

mkdir -p ${ROOTDIR}
WORKDIR=$(pwd -P)

# If not already installed, install DESED
pip install desed@git+https://github.com/turpaultn/DESED
cd ..
echo "Download and extract soundbank"
wget -O DESED_synth_soundbank.tar.gz https://zenodo.org/record/3571305/files/DESED_synth_soundbank.tar.gz?download=1
tar -xzf DESED_synth_soundbank.tar.gz
rm DESED_synth_soundbank.tar.gz
cd synthetic
echo "Done"

cd code
# If you did not download the synthetic training background yet
echo "Download SINS background... (to add TUT, add the option --TUT)"
${CONDA_ENV} get_background_training.py
cd ..
echo "Done"

cd ${ROOTDIR}
echo "Getting jams for dcase 2020"
# Get jams file
wget -O DESED_synth_dcase20jams.tar.gz https://zenodo.org/record/3700195/files/DESED_synth_dcase20_train_jams.tar?download=1
tar -xzf DESED_synth_dcase20jams.tar.gz
rm DESED_synth_dcase20jams.tar.gz
echo "Done"

# Download and generate synthetic
cd ${WORKDIR}/code
echo "generate synthetic data from jams ... ~30min"
subset=train
echo "${subset} data ..."
${CONDA_ENV} generate_wav.py --jams_folder=${ROOTDIR}/audio/${subset}/synthetic20/soundscapes \
--soundbank=${WORKDIR}/audio/${subset}/soundbank --out_audio_dir=${ROOTDIR}/audio/${subset}/synthetic20/soundscapes \
--out_tsv=${ROOTDIR}/metadata/${subset}/synthetic20/soundscapes.tsv --save_isolated
cd ..
echo "Done"

echo "RIR not available yet, coming soon..."