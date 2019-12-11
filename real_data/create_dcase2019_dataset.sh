#!/bin/bash

# Change with your own environment
CONDA_ENV=python

# Create directory, and copy data in right folders to have a unique directory with dcase2019 data
ROOTDIR=../dcase2019/dataset
mkdir -p ${ROOTDIR}

# If not already done
#echo "download real data audio files ... ~23GB"
#cd src
#${CONDA_ENV} download_real_data.py
#cd ..

# Copy or move data
cp -r metadata ${ROOTDIR}/
cp -r missing_files ${ROOTDIR}/
echo "moving real audio files"
mkdir -p ${ROOTDIR}/audio/
mv audio/* ${ROOTDIR}/audio/