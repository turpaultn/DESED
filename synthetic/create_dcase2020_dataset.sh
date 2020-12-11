#!/bin/bash

#Uncomment this part to run the script line by line
#echo "Press CTRL+C to proceed after each command."
#set -x #Prints commands and their arguments s they are executed
#trap read debug

# Change with your own environment
CONDA_ENV=python
# Path to root directory
ROOTDIR=$(realpath ..)
# Will put dcase2020 dataset in this folder
DATASET_DIR=${ROOT_DIR}/dataset
# The path to synthetic where the python files are
SYNTHETIC_DIR=${ROOT_DIR}/synthetic

# For reverberation computation
NPROC=8 # Be careful, if you do not use the same number of processors, you won't reproduce the baseline data.

############### Shouldn't have to change anything after this line
cd ${ROOT_DIR}
SCRIPTS_PATH=${SYNTHETIC_DIR}/code
mkdir -p ${DATASET_DIR}

# If not already installed, install DESED
pip install desed@git+https://github.com/turpaultn/DESED
echo "Download and extract soundbank"
wget -O DESED_synth_soundbank.tar.gz https://zenodo.org/record/4307908/files/DESED_synth_soundbank.tar.gz?download=1
tar -xzf DESED_synth_soundbank.tar.gz -C ${SYNTHETIC_DIR}
rm DESED_synth_soundbank.tar.gz
echo "Done"

# If you did not download the synthetic training background yet
echo "Download SINS background... (to add TUT, add the option --TUT)"
${CONDA_ENV} ${SCRIPTS_PATH}/get_background_training.py --basedir=${SYNTHETIC_DIR}
echo "Done"

echo "Getting jams for dcase 2020"
cd ${DATASET_DIR}
# Get jams file
wget -O DESED_synth_dcase20jams.tar.gz https://zenodo.org/record/3713328/files/DESED_synth_dcase20_train_jams.tar.gz?download=1
tar -xzf DESED_synth_dcase20jams.tar.gz
rm DESED_synth_dcase20jams.tar.gz
cd ${ROOT_DIR}
echo "Done"

# Download and generate synthetic
echo "generate synthetic data from jams ... ~30min"
subset=train
echo "${subset} data ..."
${CONDA_ENV} ${SCRIPTS_PATH}/generate_wav.py --jams_folder=${DATASET_DIR}/audio/${subset}/synthetic20/soundscapes \
--soundbank=${SYNTHETIC_DIR}/audio/${subset}/soundbank --out_audio_dir=${DATASET_DIR}/audio/${subset}/synthetic20/soundscapes \
--out_tsv=${DATASET_DIR}/metadata/${subset}/synthetic20/soundscapes.tsv --save_isolated
echo "Done"


##########
# Reverberate with fuss, could be uncommented if needed
##########
#echo "Getting RIR data"
#wget -O FUSS_rir_data.tar.gz https://zenodo.org/record/3694384/files/FUSS_rir_data.tar.gz?download=1
#tar -xzf FUSS_rir_data.tar.gz
##rm FUSS_rir_data.tar.gz
#
#echo "Cloning sound-separation repo"
#git clone https://github.com/google-research/sound-separation.git
#
#echo "RIR coming from fuss"
#SUBSET=train  # Here the subset is also used to define the subset of RIR to use
#INPUT_PATH=${DATASET_DIR}/audio/${SUBSET}/synthetic20
#
## Reverb default path
#RIR=${ROOT_DIR}/rir_data
#
#REVERB_PATH=${INPUT_PATH}_reverb
#MIX_INFO=${REVERB_PATH}/mix_info.txt
#SRC_LIST=${REVERB_PATH}/src_list.txt
#RIR_LIST=${REVERB_PATH}/rir_list.txt
#
#echo "number of processors is ${NPROC}, you can change it if you want"
######### Under this line you should not have to change anything ###########
#
## Reverberate data using same RIR as Google baseline
#python ${SCRIPTS_PATH}/reverberate_data.py --rir_folder=${RIR} --input_folder=${INPUT_PATH} \
#--reverb_out_folder=${REVERB_PATH} --rir_subset=${SUBSET} \
#--mix_info_file=${MIX_INFO}  --src_list_file=${SRC_LIST} --rir_list_file=${RIR_LIST} --nproc=${NPROC}
