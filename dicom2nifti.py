import os
import subprocess

base_input_root = "/home/eleonore/Downloads/TCIA/Colorectal-Liver-Metastases-November-2022-manifest/Colorectal-Liver-Metastases"
base_output_root = "/home/eleonore/Downloads/TCIA_Nifti"

for i in range(1, 199):
    patientFolder = f"CRLM-CT-1{str(i).zfill(3)}"
    patientPath = os.path.join(base_input_root, patientFolder)

    if not os.path.isdir(patientPath):
        print(f"Skipping missing folder: {patientPath}")
        continue

    # Walk all subfolders recursively
    for root, dirs, files in os.walk(patientPath):
        dicom_files = [f for f in files if f.lower().endswith(".dcm")]
        if not dicom_files:
            continue  # No DICOMs in this folder, skip

        # Create output folder for this patient if it doesn't exist
        outputFolder = os.path.join(base_output_root, patientFolder)
        os.makedirs(outputFolder, exist_ok=True)

        print(f"Converting DICOMs in: {root}")
        subprocess.run([
            "dcm2niix",
            "-z", "y",
            "-o", outputFolder,
            "-f", "%p_%s",
            root
        ])

