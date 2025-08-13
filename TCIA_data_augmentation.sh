#!/bin/bash

SLICER_PATH="/opt/Slicer-5.9.0-2025-06-27-linux-amd64/Slicer"

# Define orientation and direction arrays (Bash syntax)
L_orientation=("x" "y" "z")
L_direction=("up" "down")
magnitude=700
duration=7

# Loop from 1 to 198
for i in {1..198}; do
    echo "Processing file index: $i"
    first_time=True 

    for orientation in "${L_orientation[@]}"; do
        for direction in "${L_direction[@]}"; do
            echo " -> orientation=$orientation, direction=$direction, first_time=$first_time"
            
               $SLICER_PATH --exit-after-startup \
                --python-code "
i=$i; 
magnitude=$magnitude; 
duration=$duration; 
orientation='$orientation'; 
direction='$direction'; 
first_time=$first_time; 
exec(open('/home/eleonore/TCIADataAugmentation/scripts/TCIA_data_augmentation.py').read())"
            first_time=False
        done
    done

    echo "Completed processing for index $i"
done



