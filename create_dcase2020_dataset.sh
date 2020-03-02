#!/bin/bash
DATADIR=$(realpath dataset)

cd real
./create_dcase2019_dataset.sh ${DATADIR}

cd ../synthetic/
./create_dcase2020_dataset.sh

cd ../