#!/bin/bash

# Change with your own environment
CONDA_ENV=python
# Will put dcase2020 dataset in this folder
DATASET_DIR=$(realpath ../dataset)


############### Shouldn't have to change anything after this line

mkdir -p ${DATASET_DIR}
WORKDIR=$(pwd -P)

# If not already installed, install DESED
pip install desed@git+https://github.com/turpaultn/DESED
cd ..
echo "Download and extract soundbank"
wget -O DESED_synth_soundbank.tar.gz https://zenodo.org/record/3702397/files/DESED_synth_soundbank.tar.gz?download=1
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

cd ${DATASET_DIR}
echo "Getting jams for dcase 2020"
# Get jams file
wget -O DESED_synth_dcase20jams.tar.gz https://zenodo.org/record/3702397/files/DESED_synth_dcase20_train_jams.tar?download=1
tar -xzf DESED_synth_dcase20jams.tar.gz
rm DESED_synth_dcase20jams.tar.gz
echo "Done"

# Download and generate synthetic
cd ${WORKDIR}/code
echo "generate synthetic data from jams ... ~30min"
subset=train
echo "${subset} data ..."
${CONDA_ENV} generate_wav.py --jams_folder=${DATASET_DIR}/audio/${subset}/synthetic20/soundscapes \
--soundbank=${WORKDIR}/audio/${subset}/soundbank --out_audio_dir=${DATASET_DIR}/audio/${subset}/synthetic20/soundscapes \
--out_tsv=${DATASET_DIR}/metadata/${subset}/synthetic20/soundscapes.tsv --save_isolated
cd ..
echo "Done"


##########
# Reverberate with fuss
##########
cd ..
echo "Getting RIR data"
wget -O FUSS_rir_data.tar.gz https://zenodo.org/record/3694384/files/FUSS_rir_data.tar.gz?download=1
tar -xzf FUSS_rir_data.tar.gz
#rm FUSS_rir_data.tar.gz

echo "Cloning sound-separation repo"
git clone https://github.com/google-research/sound-separation.git

cd synthetic
echo "RIR coming from fuss"
SUBSET=train  # Here the subset is also used to define the subset of RIR to use
INPUT_PATH=${DATASET_DIR}/audio/${SUBSET}/synthetic20

# Reverb default path
RIR=../rir_data

REVERB_PATH=${INPUT_PATH}_reverb
MIX_INFO=${REVERB_PATH}/mix_info.txt
SRC_LIST=${REVERB_PATH}/src_list.txt
RIR_LIST=${REVERB_PATH}/rir_list.txt


NPROC=8 # Be careful, if you do not use the same number of processors, you won't reproduce the baseline data.
SCRIPTS_PATH=code

######## Under this line you should not have to change anything ###########

# Reverberate data using same RIR as Google baseline
python ${SCRIPTS_PATH}/reverberate_data.py --rir_folder=${RIR} --input_folder=${INPUT_PATH} \
--reverb_out_folder=${REVERB_PATH} --rir_subset=${SUBSET} \
--mix_info_file=${MIX_INFO}  --src_list_file=${SRC_LIST} --rir_list_file=${RIR_LIST} --nproc=${NPROC}