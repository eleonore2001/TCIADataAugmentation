import os
import slicer
import time
import qt
import sys
import vtk
import sitkUtils, SimpleITK as sitk
import numpy as np


# --- Helpers ---
def radius_from_mm(spacing, mm):
    if mm <= 0: return (0,0,0)
    return tuple(int(max(1, round(mm/s))) for s in spacing)

def voxels_from_mm3(spacing, mm3):
    if mm3 <= 0: return 0
    vox_mm3 = spacing[0]*spacing[1]*spacing[2]
    return max(1, int(round(mm3 / vox_mm3)))

def sitk_largest_island(mask, spacing, keepLargestOnly=True, minSizeMM3=0.0, medianMM=0.0, closingMM=0.0):
    # mask is a SimpleITK binary image (0/1) with correct spacing/origin/direction
    out = mask
    if medianMM > 0:
        out = sitk.Median(out, radius_from_mm(spacing, medianMM))
    if closingMM > 0:
        close = sitk.BinaryMorphologicalClosingImageFilter()
        close.SetForegroundValue(1)
        close.SetKernelType(sitk.sitkBall)
        close.SetKernelRadius(radius_from_mm(spacing, closingMM))
        out = close.Execute(out)

    cc = sitk.ConnectedComponent(out)
    if keepLargestOnly:
        rel = sitk.RelabelComponent(cc, sortByObjectSize=True)
        kept = sitk.BinaryThreshold(rel, 1, 1, 1, 0)
    else:
        min_vox = voxels_from_mm3(spacing, minSizeMM3)
        rel = sitk.RelabelComponent(cc, minimumObjectSize=int(min_vox), sortByObjectSize=True)
        kept = sitk.BinaryThreshold(rel, 1, 2**31-1, 1, 0)
    return sitk.Cast(kept, sitk.sitkUInt8)

def clean_segment_inplace(segNode, segmentID):
    # Ensure binary labelmap representation is available
    segNode.CreateBinaryLabelmapRepresentation()

    # Export just this segment into a temporary labelmap node (in-memory)
    ids = vtk.vtkStringArray(); ids.InsertNextValue(segmentID)
    lm = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
    slicer.modules.segmentations.logic().ExportSegmentsToLabelmapNode(segNode, ids, lm, None)

    # Pull as SimpleITK (preserves spacing/origin/direction)
    img = sitkUtils.PullVolumeFromSlicer(lm)
    img = sitk.Cast(img, sitk.sitkUInt16)
    spacing = img.GetSpacing()

    # Make binary mask (>0), run largest-island, push result back into same labelmap node
    mask = sitk.NotEqual(img, 0)
    kept = sitk_largest_island(mask, spacing,
                               keepLargestOnly=keepLargestOnly,
                               minSizeMM3=minSizeMM3,
                               medianMM=medianMM,
                               closingMM=closingMM)
    sitkUtils.PushVolumeToSlicer(kept, targetNode=lm)

    # Update the original segment from the temp labelmap
    try:
        # Preferred (fast, no segment churn)
        arr = slicer.util.arrayFromVolume(lm)
        slicer.util.updateSegmentBinaryLabelmapFromArray((arr>0).astype(np.uint8), segNode, segmentID, lm)
    except AttributeError:
        # Fallback: replace the segment by importing this binary as a new segment
        seg = segNode.GetSegmentation().GetSegment(segmentID)
        oldName, oldColor = seg.GetName(), seg.GetColor()
        segNode.GetSegmentation().RemoveSegment(segmentID)
        slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(lm, segNode)
        newID = segNode.GetSegmentation().GetNthSegmentID(segNode.GetSegmentation().GetNumberOfSegments()-1)
        newSeg = segNode.GetSegmentation().GetSegment(newID)
        newSeg.SetName(oldName); newSeg.SetColor(oldColor)

    # Cleanup temporary node
    slicer.mrmlScene.RemoveNode(lm)




# def save_scene(outputDir,modifiedseg_filename, modifiedvolume_filename):

#     segmentationNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")

#     if first_time :
#     #that code is to save the non modified segmentation in a way that's easier to compare than to modified one
#     #the segmentation obtained thanks to the DICOM to NIFTI script is not so good (according to my knowledge at least !)
#         labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
#         slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(segmentationNode, labelmapVolumeNode)
#         filename = "Segmentation_100.nii.gz"
#         filepath = os.path.join(outputDir, filename)
#         os.makedirs(outputDir, exist_ok=True)
#         slicer.util.saveNode(labelmapVolumeNode, filepath)

#     segmentationNode.HardenTransform()

#     labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
#     slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(segmentationNode, labelmapVolumeNode)
#     filename = modifiedseg_filename
#     filepath = os.path.join(outputDir, filename)
#     os.makedirs(outputDir, exist_ok=True)
#     slicer.util.saveNode(labelmapVolumeNode, filepath)

#     volumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
#     volumeNode.HardenTransform()

#     filename = modifiedvolume_filename
#     filepath = os.path.join(outputDir, filename)
#     slicer.util.saveNode(volumeNode, filepath)

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
            if orientation == "x" and direction == "positive":
                endPoint = [center[0]+ 10, center[1], center[2]]  # Example gravity vector
            if orientation == "x" and direction == "negative":
                endPoint = [center[0]- 10, center[1], center[2]]  # Example gravity vector
            if orientation == "y" and direction == "positive":
                endPoint = [center[0], center[1] + 10, center[2]]  # Example gravity vector
            if orientation == "y" and direction == "negative":
                endPoint = [center[0], center[1] - 10, center[2]]  # Example gravity vector
            if orientation == "z" and direction == "positive":
                endPoint = [center[0], center[1], center[2] + 10]  # Example gravity vector
            if orientation == "z" and direction == "negative":
                endPoint = [center[0], center[1], center[2] - 10]  # Example gravity vector

            gravityVector.AddControlPoint(startPoint)
            gravityVector.AddControlPoint(endPoint)

        sparseGrid.getParameterNode().gravityVector = gravityVector

# def create_model(reductionFactorValue): #creates and cleans the 3D model used by Slicer SOFA
#     slicer.modules.segmentations.logic().ExportVisibleSegmentsToModels(slicer.util.getNode("Segmentation"),True)
#     inputModel = slicer.util.getNode("Liver")
#     outputModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode')
#     outputModel.SetName('liver_dec')
#     logic_surface = slicer.util.getModuleLogic('SurfaceToolbox')
#     logic_surface.clean(inputModel,outputModel)
#     slicer.app.processEvents()
#     logic_surface.decimate(outputModel, outputModel, reductionFactor=reductionFactorValue, decimateBoundary=True, lossless=False, aggressiveness=7.0)
#     slicer.app.processEvents()
#     logic_surface.smooth(outputModel, outputModel, method='Taubin', iterations=30, laplaceRelaxationFactor=0.5, taubinPassBand=0.1, boundarySmoothing=True)
#     slicer.app.processEvents()

# def run_sparsegrid(orientation,direction):
#     sparseGrid = slicer.util.getModuleLogic('SparseGridSimulation')
#     sparseGrid_widget = slicer.util.getModuleWidget('SparseGridSimulation')


#     liver_modelnode = slicer.util.getNode("liver_dec")
#     sparseGrid.getParameterNode().modelNode = liver_modelnode
#     addGravityVector(orientation,direction)

#     sparseGrid.addBoundaryROI()
#     roiNode = slicer.util.getNode('MarkupsROI')
#     currentSize = roiNode.GetSize()
#     newHeight = currentSize[2] * 0.1
#     roiNode.SetSize(currentSize[0], currentSize[1], newHeight)
#     currentCenter = roiNode.GetCenter()
#     heightDifference = (currentSize[2] - newHeight) / 2
#     roiNode.SetCenter(currentCenter[0], currentCenter[1], currentCenter[2] - heightDifference)
#     #if you want to play with it a bit you just have to change where you add / substract the "heightDifference" parameter


#     sparseGrid.addSparseGridModelNode()
#     sparseGrid.addGridTransformNode()

#     sparseGrid_widget.startSimulation()

# def transform_volume_seg():
#     transformNode = slicer.util.getNode('Grid Transform')
#     segmentationNode = slicer.util.getNode('Segmentation')
#     segmentationNode.SetAndObserveTransformNodeID(transformNode.GetID())
#     volumeNodes = slicer.util.getNodesByClass('vtkMRMLScalarVolumeNode')
#     volumeNode = volumeNodes[0]
#     volumeNode.SetAndObserveTransformNodeID(transformNode.GetID())


# ############################
# ENTRY POINT
# ############################

# --- Load volume and segmentation ---
volumeNode=slicer.util.loadVolume(inputVolumePath)
segmentationNode=slicer.util.loadSegmentation(inputSegmentationPath)

# # --- Clean the labelmap (largest island) ---
# keepLargestOnly = True         # True = keep only largest component
# minSizeMM3 = 5.0               # remove islands smaller than this (0=off) AFTER keeping largest
# medianMM = 1.0                 # optional median smoothing before CC (0=off)
# closingMM = 0.0                # optional closing (careful: may expand); 0=off

# segmentation = segmentationNode.GetSegmentation()
# segmentIDs = [segmentation.GetNthSegmentID(i) for i in range(segmentation.GetNumberOfSegments())]

# for sid in segmentIDs:
#     print(f"[largest-island] Cleaning segment: {segmentation.GetSegment(sid).GetName()}")
#     clean_segment_inplace(segmentationNode, sid)

# print("Done cleaning segment")

# --- Convert clean segmentation to mesh ---

slicer.modules.segmentations.logic().ExportVisibleSegmentsToModels(segmentationNode, True)
inputModel = slicer.util.getNode("Segment_1")
outputModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode')
surfaceToolboxLogic = slicer.util.getModuleLogic('SurfaceToolbox')
#slicer.app.processEvents()
surfaceToolboxLogic.clean(inputModel,outputModel)
#slicer.app.processEvents()
surfaceToolboxLogic.decimate(outputModel, outputModel, reductionFactor=0.9, decimateBoundary=True, lossless=False, aggressiveness=7.0)
slicer.app.processEvents()
# surfaceToolboxLogic.smooth(outputModel, outputModel, method='Taubin', iterations=30, laplaceRelaxationFactor=0.5, taubinPassBand=0.1, boundarySmoothing=True)
# slicer.app.processEvents()
# surfaceToolboxLogic.remesh(outputModel,outputModel,subdivide=1)
# slicer.util.saveNode(outputModel, "/tmp/a.vtk")

print("Done converting to triangular mesh")

# --- Run sparse grid simulation ---

sparseGrid = slicer.util.getModuleLogic('SparseGridSimulation')
sparseGrid_widget = slicer.util.getModuleWidget('SparseGridSimulation')

sparseGrid.getParameterNode().modelNode = outputModel
addGravityVector(orientation,direction)

sparseGrid.addBoundaryROI()
roiNode = slicer.util.getNode('R')
currentSize = roiNode.GetSize()
newHeight = currentSize[2] * 0.1
roiNode.SetSize(currentSize[0], currentSize[1], newHeight)
currentCenter = roiNode.GetCenter()
heightDifference = (currentSize[2] - newHeight) / 2
roiNode.SetCenter(currentCenter[0], currentCenter[1], currentCenter[2] - heightDifference)

sparseGrid.addSparseGridModelNode()
sparseGrid.addGridTransformNode()

sparseGrid.startSimulation()

# --- Save the transformed volumes ---
transformNode = sparseGrid.getParameterNode().gridTransformNode
volumeNode.SetAndObserveTransformNodeID(transformNode.GetID())
volumeNode.HardenTransform()
slicer.util.saveNode(volumeNode, outputVolumePath)

labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(segmentationNode, labelmapVolumeNode)
labelmapVolumeNode.SetAndObserveTransformNodeID(transformNode.GetID())
labelmapVolumeNode.HardenTransform()
slicer.util.saveNode(labelmapVolumeNode, outputSegmentationPath)
