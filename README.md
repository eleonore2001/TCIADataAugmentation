
# Data Augmentation for the TCIA dataset

This repository provides a containerized pipeline to augment data from the Colorectal-Liver TCIA dataset ([https://www.cancerimagingarchive.net/collection/colorectal-liver-metastases/](https://www.cancerimagingarchive.net/collection/colorectal-liver-metastases/)). This augmentation is made with the 3D Slicer + SlicerSOFA extension, using an external force to deform a model and transfer the deformation to medical images and segmentations.

## How it works

Clone this repository:

```bash
git clone https://github.com/OUH-MeshLab/TCIADataAugmentation ~/TCIADataAugmentation
```

Build the container (while here `podman` is used, `docker` can be used in a similar way):

```bash
cd ~/TCIADataAugmentation
podman build . -t tcia
```

Run the container:

```bash
podman run -v ~/data/input:/data/input -v ~/data/output:/data/output -e DOWNLOAD_DATASET_AND_AGREE_LICENSE=1 tcia
```

This command will (1) pull the dataset and save it to `~/data/input`; (2) perform a DICOM-NIFTI conversion and save it to '~/data/output'; and (3) start the simulation, which results will be stored in `~/data/output`. *NOTE: by setting `DOWNLOAD_DATASET_AND_AGREE_LICENSE=1` you are agreein to the TCIA dataset (check [https://www.cancerimagingarchive.net/collection/colorectal-liver-metastases/](https://www.cancerimagingarchive.net/collection/colorectal-liver-metastases/))

If the data was previously downloaded to `~/data/input` it is possible to set `DOWNLOAD_DATASET_AND_AGREE_LICENSE=0` to avoid re-downloads:

```bash
podman run -v ~/data/input:/data/input -v ~/data/output:/data/output -e DOWNLOAD_DATASET_AND_AGREE_LICENSE=0 tcia
```

If the data was previously converted`~/data/input` it is possible to set `CONVERT_DATASET=0` to avoid re-converting the dataset :

```bash
podman run -v ~/data/input:/data/input -v ~/data/output:/data/output -e DOWNLOAD_DATASET_AND_AGREE_LICENSE=0 -e CONVERT_DATASET=0 tcia
```



Beyond the DICOM-NIFTI conversion, the pipeline creates 3D surface models based on the segmentations of the liver / tumors. Using the Slicer SOFA extension these surface models are converted to a sparse grid representation (hexahedra). An external force is applied to the model in multiple configurations. The resulting transformation is retrieved and applied to the volume and the segmentation. 6 different vectors are applied to each volume / segmentations. It is possible to change two parameters  : the magnitude of the gravity vector and the time for which the simulation is running.


## Results
These are examples of how a volume and segmentations can be modified using theses scripts. I used a magnitude of 800 and a time of 10 seconds to achieve these results.

| Image 1 | Image 2 |
|---------|---------|
| ![Image 1](./scripts/image-1.png) | ![Image 2](./scripts/image-2.png) |
| **Original volume and segmentation** | **Deformation with a vector going towards right** |

| Image 3 | Image 4 |
|---------|---------|
| ![Image 3](./scripts/image-3.png)| ![Image 4](./scripts/image-4.png)|
| **Deformation with a vector going towards left** | **Deformation with a vector going up** |
