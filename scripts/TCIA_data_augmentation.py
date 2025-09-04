import os
from DICOMLib import DICOMUtils
import slicer
import time
import qt
import sys


def save_scene(outputDir,modifiedseg_filename, modifiedvolume_filename):

    segmentationNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")

    if first_time :
    #that code is to save the non modified segmentation in a way that's easier to compare than to modified one
    #the segmentation obtained thanks to the DICOM to NIFTI script is not so good (according to my knowledge at least !)
        labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
        slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(segmentationNode, labelmapVolumeNode)
        filename = "Segmentation_100.nii.gz"
        filepath = os.path.join(outputDir, filename)
        os.makedirs(outputDir, exist_ok=True)
        slicer.util.saveNode(labelmapVolumeNode, filepath)

    segmentationNode.HardenTransform()
    labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
    slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(segmentationNode, labelmapVolumeNode)
    filename = modifiedseg_filename
    filepath = os.path.join(outputDir, filename)
    os.makedirs(outputDir, exist_ok=True)
    slicer.util.saveNode(labelmapVolumeNode, filepath)

    volumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
    volumeNode.HardenTransform()

    filename = modifiedvolume_filename
    filepath = os.path.join(outputDir, filename)
    slicer.util.saveNode(volumeNode, filepath)

def addGravityVector(orientation,direction):
        sparseGrid = slicer.util.getModuleLogic('SparseGridSimulation')
        gravityVector = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', "Gravity")
        gravityVector.CreateDefaultDisplayNodes()
        modelNode = sparseGrid.getParameterNode().modelNode

        if modelNode and modelNode.GetPolyData():
            bounds = modelNode.GetPolyData().GetBounds()
            center = [(bounds[0] + bounds[1]) / 2.0,
                      (bounds[2] + bounds[3]) / 2.0,
                      (bounds[4] + bounds[5]) / 2.0]
            startPoint = [center[0], center[1], center[2]]
            if orientation == "x" and direction == "up":
                endPoint = [center[0]+ 10, center[1], center[2]]  # Example gravity vector
            if orientation == "x" and direction == "down":
                endPoint = [center[0]- 10, center[1], center[2]]  # Example gravity vector
            if orientation == "y" and direction == "up":
                endPoint = [center[0], center[1] + 10, center[2]]  # Example gravity vector
            if orientation == "y" and direction == "down":
                endPoint = [center[0], center[1] - 10, center[2]]  # Example gravity vector
            if orientation == "z" and direction == "up":
                endPoint = [center[0], center[1], center[2] + 10]  # Example gravity vector
            if orientation == "z" and direction == "down":
                endPoint = [center[0], center[1], center[2] - 10]  # Example gravity vector

            gravityVector.AddControlPoint(startPoint)
            gravityVector.AddControlPoint(endPoint)

        sparseGrid.getParameterNode().gravityVector = gravityVector

def create_model(reductionFactorValue): #creates and cleans the 3D model used by Slicer SOFA
    slicer.modules.segmentations.logic().ExportVisibleSegmentsToModels(slicer.util.getNode("Segmentation"),True)
    inputModel = slicer.util.getNode("Liver")
    outputModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode')
    outputModel.SetName('liver_dec')
    logic_surface = slicer.util.getModuleLogic('SurfaceToolbox')
    logic_surface.clean(inputModel,outputModel)
    slicer.app.processEvents()
    logic_surface.decimate(outputModel, outputModel, reductionFactor=reductionFactorValue, decimateBoundary=True, lossless=False, aggressiveness=7.0)
    slicer.app.processEvents()
    logic_surface.smooth(outputModel, outputModel, method='Taubin', iterations=30, laplaceRelaxationFactor=0.5, taubinPassBand=0.1, boundarySmoothing=True)
    slicer.app.processEvents()

def run_sparsegrid(orientation,direction):
    sparseGrid = slicer.util.getModuleLogic('SparseGridSimulation')
    sparseGrid_widget = slicer.util.getModuleWidget('SparseGridSimulation')


    liver_modelnode = slicer.util.getNode("liver_dec")
    sparseGrid.getParameterNode().modelNode = liver_modelnode
    addGravityVector(orientation,direction)

    sparseGrid.addBoundaryROI()
    roiNode = slicer.util.getNode('MarkupsROI')
    currentSize = roiNode.GetSize()
    newHeight = currentSize[2] * 0.1
    roiNode.SetSize(currentSize[0], currentSize[1], newHeight)
    currentCenter = roiNode.GetCenter()
    heightDifference = (currentSize[2] - newHeight) / 2
    roiNode.SetCenter(currentCenter[0], currentCenter[1], currentCenter[2] - heightDifference)
    #if you want to play with it a bit you just have to change where you add / substract the "heightDifference" parameter


    sparseGrid.addSparseGridModelNode()
    sparseGrid.addGridTransformNode()

    sparseGrid_widget.startSimulation()

def transform_volume_seg():
    transformNode = slicer.util.getNode('Grid Transform')
    segmentationNode = slicer.util.getNode('Segmentation')
    segmentationNode.SetAndObserveTransformNodeID(transformNode.GetID())
    volumeNodes = slicer.util.getNodesByClass('vtkMRMLScalarVolumeNode')
    volumeNode = volumeNodes[0]
    volumeNode.SetAndObserveTransformNodeID(transformNode.GetID())


# ############################
# ENTRY POINT
# ############################

# Load datasets
volume=slicer.util.loadVolume(volumePath)
segmentation=slicer.util.loadSegmentation(segmentationPath)


# logic = slicer.util.getModuleLogic('SparseGridSimulation')
# simulation_params = logic.getParameterNode()

# sparseGrid_widget = slicer.util.getModuleWidget('SparseGridSimulation')
# dic = {0.890 : [8, 43, 123, 149, 198], 0.899 : [162], 0.966 : [176],  0.934 : [22,31] , 0.936 : [101], 0.970 : [73],
#         0.988 : [13, 88, 105, 135, 138, 146], 0.980 : [33, 60, 75, 82, 113, 132, 145, 156, 158, 166, 184],
#         0.982 : [14, 110, 124, 142, 148, 150, 151, 172, 183, 185],
#         0.978 : [15, 18, 50, 70, 97, 106, 107, 108, 112, 140, 143, 144, 165, 180, 194, 196],
#         0.975 : [1, 10, 11, 19, 20, 37, 38, 39, 41, 42, 48, 55, 61, 64, 69, 91, 94, 111, 115, 119, 126, 128, 133, 159, 161, 174, 178, 179, 181, 190],
#         0.985 : [2, 4, 7, 9, 16, 21, 23, 26, 28, 29, 34, 35, 36, 44, 47, 52, 54, 59, 66, 77, 78, 83, 85, 90, 92, 93, 95, 100, 102, 103, 117, 118, 121, 122, 137, 157, 164, 167, 169, 171, 182, 186, 189, 192],
#         0.999 : [3, 5, 6, 12, 17, 25, 27, 30, 32, 40, 45, 46, 49, 51, 53, 56, 57, 58, 62, 63, 65, 67, 68, 71, 72, 74, 76, 79, 80, 81, 84, 86, 87, 89, 96, 98, 99, 104, 109, 114, 116, 120, 125, 127, 129, 130, 131,134, 136, 139, 141, 147, 152, 153, 154, 155, 160, 163, 168, 170, 173, 175, 177, 187, 188, 191, 193, 195, 197]}

# simulation_params.gravityMagnitude = magnitude
# if i ==24:   #the file CRLM-CT-024 is missing from the TCIA database
#     return

# parentPath = "/home/eleonore/Downloads/TCIA/Colorectal-Liver-Metastases-November-2022-manifest/Colorectal-Liver-Metastases/CRLM-CT-1"
# parentPath += str(i).zfill(3)
# subfolders = [f for f in os.listdir(parentPath) if os.path.isdir(os.path.join(parentPath, f))]

# child_path = os.path.join(parentPath, subfolders[0])
# loadedNodeIDs = []
# with DICOMUtils.TemporaryDICOMDatabase() as db:
#     subfolders_next = [f for f in os.listdir(child_path) if os.path.isdir(os.path.join(child_path, f))]

#     for f in subfolders_next:
#         child_path_next = os.path.join(child_path, f)
#         DICOMUtils.importDicom(child_path_next, db)

#     patientUIDs = db.patients()
#     for patientUID in patientUIDs:
#         loadedNodeIDs.extend(DICOMUtils.loadPatientByUID(patientUID))
#         slicer.app.processEvents()

#     for cle, liste_valeurs in dic.items():
#         if i in liste_valeurs:
#             x= cle


#     create_model(reductionFactorValue=x)
#     run_sparsegrid(orientation,direction)
#     transform_volume_seg()

#     start_time = time.time()
#     while time.time() - start_time < duration:
#         slicer.app.processEvents()
#         time.sleep(0.1)

#     sparseGrid_widget.stopSimulation()
#     sparseGrid_widget.cleanup()
#     newseg_filename = "Segmentation_modified" + "_ "+ orientation + "_" + direction + "_" + str(magnitude) + ".nii.gz"
#     newvolume_filename = "Volume_modified" + "_ "+ orientation + "_" + direction + "_" + str(magnitude) + ".nii.gz"

#     outputDir = "/home/eleonore/Downloads/TCIA_Nifti/CRLM-CT-1" + str(i).zfill(3)
#     save_scene(outputDir,newseg_filename,newvolume_filename)
#     slicer.mrmlScene.Clear(0)
