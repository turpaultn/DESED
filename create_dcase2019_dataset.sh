#!/bin/bash
cd real
./create_dcase2019_dataset.sh

cd ../synthetic/
./create_dcase2019_dataset.sh

cd ../