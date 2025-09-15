import slicer
import os

# Define the path to the Sofa extension tar package
sofa_tar_path = "/33918-linux-amd64-SlicerSOFA-git0aaef9e-2025-09-13.tar.gz"

# Define the path to the QuantitativeReporting extension tar package
quantitative_reporting_tar_path = "/30822-linux-amd64-QuantitativeReporting-gitd4892cf-2022-04-08.tar.gz"

# Check if the Sofa extension file exists
if not os.path.exists(sofa_tar_path):
    raise FileNotFoundError(f"Sofa extension archive not found at {sofa_tar_path}")

# Check if the QuantitativeReporting extension file exists
if not os.path.exists(quantitative_reporting_tar_path):
    raise FileNotFoundError(f"QuantitativeReporting extension archive not found at {quantitative_reporting_tar_path}")

# Get the Extensions Manager model
extensions_manager = slicer.app.extensionsManagerModel()

# Install the Sofa extension without dependencies
sofa_success = extensions_manager.installExtension(sofa_tar_path, False, True)  # archiveFile, installDependencies, waitForCompletion

# Install the QuantitativeReporting extension with dependencies
quant_reporting_success = extensions_manager.installExtension(quantitative_reporting_tar_path, True, True)  # installDependencies=True

# Check the installation status
if sofa_success and quant_reporting_success:
    print("Extensions installed successfully. Restart Slicer to load the extensions.")
    slicer.app.exit(0)
else:
    if not sofa_success:
        print(f"Failed to install the Sofa extension from {sofa_tar_path}. Check the log for more details.")
    if not quant_reporting_success:
        print(f"Failed to install the QuantitativeReporting extension from {quantitative_reporting_tar_path}. Check the log for more details.")
    slicer.app.exit(1)
