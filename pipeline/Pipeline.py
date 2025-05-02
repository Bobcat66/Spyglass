
import cv2
import numpy as np
import cscore
from utils.vtypes import *
from configuration.config_types import CameraConfig, FieldConfig
from pipeline.ApriltagDetector import ApriltagDetector
from pipeline import annotator, pnpsolvers
from typing import Tuple

class Pipeline:
    """
    A base class for pipelines.
    """
    def __init__(
        self,
        name: str,
    ):
        self.name = name

    def process(self, frame: cv2.Mat) -> PipelineResult:
        """
        Run the pipeline.
        """
        raise NotImplementedError("Pipeline.run() must be implemented by subclasses.")
    
class ApriltagPipeline(Pipeline):
    """
    A pipeline for detecting and solving AprilTags. Expects a grayscale frame
    """
    def __init__(
        self,
        name: str,
        camConf: CameraConfig,
        fieldConf: FieldConfig,
        detector: ApriltagDetector,
    ):
        self.name = name
        self._camConf = camConf
        self._fieldConf = fieldConf
        super.__init__(name)
        self._detector = detector
        self._solver = pnpsolvers.GeneralPnPSolver(camConf, fieldConf)
        self._fidSolver = pnpsolvers.FiducialPnPSolver(camConf, fieldConf)
    
    def process(self,frame: cv2.Mat) -> PipelineResult:
        """
        Run the pipeline.
        """
        # Process the frame
        fiducials = self._detector.detect(frame)
        nTagResult = self._solver.solve(fiducials)
        singleTagResults: List[Tuple[SingleTagPoseResult,Fiducial]] = []
        for fiducial in fiducials:
            stres = self._fidSolver.solve(fiducial)
            if stres != None:
                singleTagResults.append(stres)
        # Annotate the frame
        annotatedFrame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        annotator.drawFiducials(annotatedFrame, fiducials)
        distResults = List[TagDistResult]
        for result in singleTagResults:
            annotator.drawSingleTagPose(annotatedFrame, result, self._fieldConf, self._camConf)
            distResults.append(TagDistResult(
                result[1].id,
                result[1].corners,
                result[1].decisionMargin,
                result[1].hammingDist,
                np.linalg.norm(result[0].tvecs_0 if result[0].error_0 <= result[0].error_1 else result[0].tvecs_1)
            ))
        return PipelineResult(annotatedFrame,nTagResult,distResults,annotatedFrame)

#TODO: Add object detection pipeline
            

            

