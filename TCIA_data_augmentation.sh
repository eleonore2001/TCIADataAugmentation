#!/bin/bash

# Path to your Slicer executable
SLICER_PATH="/opt/Slicer-5.9.0-2025-06-27-linux-amd64/Slicer"

# Path to your Python script
PYTHON_SCRIPT="/home/eleonore/TCIADataAugmentation/scripts/data_eleonore.py"

# Loop from 1 to 199
for i in {1..199}; do
    echo "Processing file index: $i"
    
    #  $SLICER_PATH --no-main-window --exit-after-startup \
    #     --python-code "i=$i; exec(open('/home/eleonore/TCIADataAugmentation/scripts/data_eleonore.py').read())"

    $SLICER_PATH --exit-after-startup \  
        --python-code "i=$i; exec(open('/home/eleonore/TCIADataAugmentation/scripts/data_eleonore.py').read())"
    
    
    echo "Completed processing for index $i"
done

