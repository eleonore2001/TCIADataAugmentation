#!/bin/bash

SLICER_PATH="/opt/Slicer-5.9.0-2025-06-27-linux-amd64/Slicer"

# Define orientation and direction arrays (Bash syntax)
L_orientation=("x" "y" "z")
L_direction=("up" "down")

# Loop from 1 to 199
for i in {1..198}; do
    echo "Processing file index: $i"

    for orientation in "${L_orientation[@]}"; do
        for direction in "${L_direction[@]}"; do
            echo " -> orientation=$orientation, direction=$direction"
            
            $SLICER_PATH --exit-after-startup \
                --python-code "i=$i; orientation='$orientation'; direction='$direction'; exec(open('/home/eleonore/TCIADataAugmentation/scripts/TCIA_data_augmentation.py').read())"
        done
    done

    echo "Completed processing for index $i"
done
