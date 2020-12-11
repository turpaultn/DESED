#!/bin/bash

#Uncomment this part to run the script line by line
#echo "Press CTRL+C to proceed after each command."
#set -x #Prints commands and their arguments s they are executed
#trap read debug

# Change with your own environment
CONDA_ENV=python

# Create directory, and copy data in right folders to have a unique directory with dcase2019 data
ROOTDIR=$1
mkdir -p ${ROOTDIR}

# If not already done
echo "download real data audio files ... ~23GB"
${CONDA_ENV} code/download_real.py --dataset_folder="." -m "."

# Copy or move data
cp -r metadata ${ROOTDIR}/
cp -r missing_files ${ROOTDIR}/
echo "moving real audio files"
mkdir -p ${ROOTDIR}/audio/
mv audio/* ${ROOTDIR}/audio/
