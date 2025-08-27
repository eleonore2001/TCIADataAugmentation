#!/bin/bash

# Initializaiton of variables. Preference for environment variables (default otherwise)
SLICER_PATH="${SLICER_PATH:-/opt/Slicer-5.9.0-2025-06-27-linux-amd64/Slicer}"
THISSCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATASET_DIR="${DATSET_DIR:-~/Downloads/TCIA/Colorectal-Liver-Metastases-November-2022-manifest/Colorectal-Liver-Metastases/CRLM-CT-1}"
OUTPUT_DIR="${OUTPUT_DIR:-~/Downloads/TCIA_Nifti/CRLM-CT-1}"

# Define orientation and direction arrays (Bash syntax)
L_ORIENTATION=("x" "y" "z")
L_DIRECTION=("up" "down")
MAGNITUDE=700
DURATION=7




# Loop from 1 to 198
for i in {1..198}; do
    echo "Processing file index: $i"
    first_time=True

    for orientation in "${L_ORIENTATION[@]}"; do
        for direction in "${L_DIRECTION[@]}"; do
            echo " -> orientation=$orientation, direction=$direction, first_time=$first_time"

               $SLICER_PATH --exit-after-startup \
                --python-code "
i=$i;
magnitude=$MAGNITUDE;
duration=$DURATION;
orientation='$orientation';
direction='$direction';
firstTime=$first_time;
outputFolder
exec(open('${THISSCRIPT_PATH}/TCIA_data_augmentation.py').read())"
            first_time=False
        done
    done

    echo "Completed processing for index $i"
done
