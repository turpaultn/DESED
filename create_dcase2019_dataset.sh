#!/bin/bash
cd real_data
./create_dcase2019_dataset.sh

cd ../synthetic/
./create_dcase2019_dataset.sh

cd ../