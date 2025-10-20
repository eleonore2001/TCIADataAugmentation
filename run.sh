#!/bin/bash

########################################
# INITIALIZATION OF VARIABLES
# Preference for environment variables (default otherwise)
########################################

# Applications
SLICER_PATH="${SLICER_PATH:-/opt/Slicer-5.9.0-2025-10-13-linux-amd64/Slicer}"
NBIA_DOWNLOADER_PATH="${NBIA_DOWNLOADER_PATH:-/opt/nbia-data-retriever/bin/nbia-data-retriever}"
SEGIMAGE2ITKIMAGE="/opt/dcmqi-1.3.4-linux/bin/segimage2itkimage"
DCM2NIIX="dcm2niix"

# Datasets
DATASET_MANIFEST="${DATASET_MANIFEST:-/data/Colorectal-Liver-Metastases-November-2022-manifest.tcia}"
DOWNLOAD_DATASET_AND_AGREE_LICENSE="${DOWNLOAD_DATASET_AND_AGREE_LICENSE:-0}"
CONVERT_DATASET="${CONVERT_DATASET:-1}"
INPUT_DIR="${INPUT_DIR:-/data/input}"
OUTPUT_DIR="${OUTPUT_DIR:-/data/output}"

# Simulation parameters
[ -z "${ORIENTATIONS+x}" ] && ORIENTATIONS=("x" "y" "z")
[ -z "${DIRECTIONS+x}" ] && DIRECTIONS=("positive" "negative")
MAGNITUDE="${MAGNITUDE:-700000}"
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
# CONVERT DATASET DICOM->NIFTI
########################################
if [ "${CONVERT_DATASET}" -eq "1" ]; then
   for item in $(find ${INPUT_DIR} -type d -name "CRLM-*"); do
       echo "Converting $item"

       patient=$(find "${item}" -mindepth 1 -maxdepth 1 -type d)
       echo $patient

       # Convert segmentation
       segmentation_dir=$(find "${patient}" -type d -name "*Segmentation*")
       mkdir -p "${segmentation_dir/${INPUT_DIR}/${OUTPUT_DIR}}"
       segmentation=$(find "${segmentation_dir}" -name "*.dcm")
       echo $segmentation
       ${SEGIMAGE2ITKIMAGE} --inputDICOM "${segmentation}" \
                            --outputDirectory "${segmentation_dir/${INPUT_DIR}/${OUTPUT_DIR}}" \
                            -t nii \
                            --mergeSegments # on overlapping segments this will produce different files
       # Convert volume
       volume_dir=$(find "${patient}" -maxdepth 2 -mindepth 1 -type d -not -name "*Segmentation*")
       mkdir -p "${volume_dir/${INPUT_DIR}/${OUTPUT_DIR}}"
       ${DCM2NIIX} -z y -f 1 -o "${volume_dir/${INPUT_DIR}/${OUTPUT_DIR}}" "${volume_dir}"
   done
fi

########################################
# PERFORM DATA AUGMENTATION
########################################


for patient in $(find ${OUTPUT_DIR} -type d -name "CRLM-*"); do
    echo "Augmenting $patient"

     volume_dir=$(find "${patient}" -maxdepth 2 -mindepth 2 -type d -not -name "*Segmentation*")
     volume=$(find "${volume_dir}" -name "1.nii.gz")

    segmentation_dir=$(find "${patient}" -type d -name "*Segmentation*")
    segmentation=$(find "${segmentation_dir}" -name "1.nii.gz")

    for orientation in "${ORIENTATIONS[@]}"; do
        for direction in "${DIRECTIONS[@]}"; do
            echo " -> orientation=$orientation, direction=$direction, first_time=$first_time"


            outputVolumePath="${volume/.nii.gz/_${orientation}_${direction}_${magnitude}_${DURATION}.nii.gz}"
            outputSegmentationPath="${segmentation/.nii.gz/_${orientation}_${direction}_${magnitude}_${DURATION}.nii.gz}"

            echo "///////////////////////////////////////////////"
            echo "${outputVolumePath}"
            echo "${outputSegmentationPath}"

            xvfb-run $SLICER_PATH --exit-after-startup \
                     --no-main-window \
                     --python-code "
inputVolumePath='${volume}';
inputSegmentationPath='${segmentation}';
outputVolumePath='${outputVolumePath}';
outputSegmentationPath='${outputSegmentationPath}';
orientation='$orientation';
magnitude=$MAGNITUDE;
duration=$DURATION;
direction='$direction';
exec(open('/TCIA_data_augmentation.py').read())"
        done
    done
done
