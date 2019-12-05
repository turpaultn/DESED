#!/bin/bash

# Change with your own environment
CONDA_ENV=python

# Create directory, and copy data in right folders to have a unique directory with dcase2019 data
ROOTDIR=../dcase2019/dataset
mkdir -p ${ROOTDIR}

# Download and generate synthetic
echo "generate synthetic ... ~30min"
cd src
# If you did not downlaod the synthetic training background yet
${CONDA_ENV} get_background_training.py
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

