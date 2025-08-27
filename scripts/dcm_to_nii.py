#!/usr/bin/env python3
import os
import subprocess
import argparse


# Paths to executables
dcm2niix_executable = "dcm2niix"  # Ensure dcm2niix is in your PATH
segimage2itkimage_executable = "/opt/dcmqi-1.3.4-linux/bin/segimage2itkimage"  # Update if necessary

def convert_volume(volume_input_dir, output_dir, patient_id):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_filename = f"{patient_id}_volume"
    command = [
        dcm2niix_executable,
        "-z", "y",          # Compress output using gzip
        "-f", output_filename,
        "-o", output_dir,
        volume_input_dir
    ]
    print(f"Converting volume for patient {patient_id}")
    try:
        subprocess.run(command, check=True)
        print(f"Volume conversion completed for patient {patient_id}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting volume for patient {patient_id}: {e}")

def convert_segmentation(seg_input_dir, output_dir, patient_id):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    command = [
        segimage2itkimage_executable,
        "--inputDICOM", seg_input_dir,
        "--outputDirectory", output_dir,
        "-t", "nrrd",             # Specify output format
        "--mergeSegments"         # Optional: merge all segments into one file
    ]
    print(f"Converting segmentation for patient {patient_id}")
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Segmentation conversion completed for patient {patient_id}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting segmentation for patient {patient_id}: {e}")
        print(f"Standard Output:\n{e.stdout.decode()}")
        print(f"Standard Error:\n{e.stderr.decode()}")


# #################
# ENTRY POINT
# #################

parser = argparse.ArgumentParser(
                    prog='dcm_to_nii',
                    description='Utility script for converting segmentations and volumes from DICOM to NIFTI',
                    epilog='This is an internal tool and it is heavily reliant on the intended dataset to use. Use it with caution for other purposes')
parser.add_argument('-i', '--input_dir', 'Directory containing the original dataset (DICOM)', required=True)
parser.add_argument('-o', '--output_dir', 'Directory to write the conversion results', required=True)

args = parser.parse_args()

print("Input directory: ", args.input_dir)
print("Output directory: ", args.output_dir)

# Iterate over patient folders
for patient_folder in sorted(os.listdir(args.input_dir)):
    patient_path = os.path.join(args.input_dir, patient_folder)
    if not os.path.isdir(patient_path):
        continue

    print(f"\nProcessing patient: {patient_folder}")

    # Iterate over study folders
    for study_folder in os.listdir(patient_path):
        study_path = os.path.join(patient_path, study_folder)
        if not os.path.isdir(study_path):
            continue

        segmentation_folder = None
        volume_folder = None

        # Iterate over series folders within the study
        for series_folder in os.listdir(study_path):
            series_path = os.path.join(study_path, series_folder)
            if not os.path.isdir(series_path):
                continue

            # Identify segmentation and volume folders
            if "Segmentation" in series_folder or "SEG" in series_folder:
                segmentation_folder = series_path
                print(f"Found segmentation folder: {segmentation_folder}")
            else:
                # You may need to refine this condition based on your dataset structure
                volume_folder = series_path
                print(f"Found volume folder: {volume_folder}")

        output_dir = os.path.join(args.output_dir, patient_folder)

        if volume_folder:
            convert_volume(volume_folder, output_dir, patient_folder)
        else:
            print(f"No volume folder found for patient {patient_folder}")

        if segmentation_folder:
            convert_segmentation(segmentation_folder, output_dir, patient_folder)
        else:
           print(f"No segmentation folder found for patient {patient_folder}")
