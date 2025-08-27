#!/bin/bash

########################################
# INITIALIZATION OF VARIABLES
# Preference for environment variables (default otherwise)
########################################

# Applications
SLICER_PATH="${SLICER_PATH:-/opt/Slicer-5.9.0-2025-06-27-linux-amd64/Slicer}"
NBIA_DOWNLOADER_PATH="${NBIA_DOWNLOADER_PATH:-/opt/nbia-data-retriever/bin/nbia-data-retriever}"

# Datasets
DATASET_MANIFEST="${DATASET_MANIFEST:-/data/Colorectal-Liver-Metastases-November-2022-manifest.tcia}"
DOWNLOAD_DATASET_AND_AGREE_LICENSE="${DOWNLOAD_DATASET_AND_AGREE_LICENSE:-0}"
INPUT_DIR="${INPUT_DIR:-/data/input}"
OUTPUT_DIR="${OUTPUT_DIR:-/data/output}"

# Simulation parameters
[ -z "${ORIENTATIONS+x}" ] && ORIENTATIONS=("x" "y" "z")
[ -z "${DIRECTIONS+x}" ] && DIRECTIONS=("positive" "negative")
MAGNITUDE="${MAGNITUDE:-700}"
DURATION="${DURATION:-7}"

#THISSCRIPT_PATH="$(cd \"$(dirname \"${BASH_SOURCE[0]}\")\" && pwd)"

########################################
# CHECKS
########################################

# Check if SLICER_PATH is an existing executable
if [ ! -x "$SLICER_PATH" ]; then
    echo "Error: SLICER_PATH does not point to an existing executable."
    exit 1
fi

# Check if the input directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Input directory $INPUT_DIR does not exist."
    exit 1
fi

########################################
# DOWNLOAD DATASET
########################################
if [ "${DOWNLOAD_DATASET_AND_AGREE_LICENSE}" -eq "1" ]; then
    echo "Downloading original dataset. This may take a while..."
    ${NBIA_DOWNLOADER_PATH} --cli ${DATASET_MANIFEST} -d ${INPUT_DIR} --agree-to-license
else
    echo "Skipping downloading original dataset."
fi

########################################
# CONVERT DATASET NIFTI
########################################

for i in $(find -t d -name "CLRM-*"); do

    echo "Processing $i"
end
