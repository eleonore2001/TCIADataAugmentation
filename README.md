# TCIA data augmentation with simulation

# Dataset
https://www.cancerimagingarchive.net/collection/colorectal-liver-metastases/

# Download the dataset (inside the container)

Prior to running the scripts you need to download the dataset:

``` sh
/opt/nbia-data-retriever/bin/nbia-data-retriever --cli /data/Colorectal-Liver-Metastases-November-2022-manifest.tcia -d ~/Downloads/TCIA
```

# Caveats

## Installation of the Quantitative Reporting Slicer extension des not seem to work fine. 
- Open Slicer inside the container and manually install the extension through the extension manager.

