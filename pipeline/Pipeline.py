
import cv2
import numpy as np
import cscore
from utils.vtypes import *
from configuration.config_types import CameraConfig, FieldConfig
from pipeline.ApriltagDetector import ApriltagDetector
from pipeline import annotator, pnpsolvers
from typing import Callable
from utils.misc import networktime

class Pipeline:
    """
    A base class for pipelines.
    """
    def __init__(
        self,
        name: str,
        camConf: CameraConfig,
        frameSupplier: cscore.VideoSource,
        pixelFormat: cscore.VideoMode.PixelFormat,
    ):
        self.name = name
        self._input = cscore.CvSink(name + "_input",pixelFormat)
        self._input.setSource(frameSupplier)
        self._output = cscore.CvSource(name + "_output", cscore.VideoMode.PixelFormat.kBGR, camConf.xres, camConf.yres)

    def run(self) -> None:
        """
        Run the pipeline.
        """
        raise NotImplementedError("Pipeline.run() must be implemented by subclasses.")
    
    def addSink(self, sink: cscore.VideoSink) -> None:
        """
        Add a sink to the pipeline's video output.
        :param sink: The sink to add.
        """
        sink.setSource(self._output)
    
class ApriltagPipeline(Pipeline):
    """
    A pipeline for detecting and solving AprilTags. Expects a grayscale source
    """
    def __init__(
        self,
        name: str,
        camConf: CameraConfig,
        fieldConf: FieldConfig,
        detector: ApriltagDetector,
        frameSupplier: cscore.VideoSource,
        resultConsumer: Callable[[int, NTagPoseResult, List[FiducialDistResult]], None]
    ):
        self.name = name
        self._camConf = camConf
        self._fieldConf = fieldConf
        super.__init__(name, camConf, frameSupplier, cscore.VideoMode.PixelFormat.kGray)
        self._resultConsumer = resultConsumer
        self._detector = detector
        self._solver = pnpsolvers.GeneralPnPSolver(camConf, fieldConf)
        self._fidSolver = pnpsolvers.FiducialPnPSolver(camConf, fieldConf)
    
    def run(self) -> None:
        """
        Run the pipeline.
        """
        frame = cv2.Mat(np.zeros((self._camConf.yres, self._camConf.xres, 1), dtype=np.uint8))
        while True:
            # Get the next frame from the camera
            time, frame = self._input.grabFrame(frame)
            if frame is None:
                continue
            # Process the frame
            fiducials = self._detector.detect(frame)
            nTagResult = self._solver.solve(fiducials)
            singleTagResults: List[SingleTagPoseResult] = []
            for fiducial in fiducials:
                stres = self._fidSolver.solve(fiducial)
                if stres != None:
                    singleTagResults.append(stres)
            self._resultConsumer(time,networktime(),nTagResult,singleTagResults)
            # Annotate the frame
            annotatedFrame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            annotator.drawFiducials(annotatedFrame, fiducials)
            for result in singleTagResults:
                annotator.drawSingleTagPose(annotatedFrame, result, self._fieldConf, self._camConf)
            self._output.putFrame(annotatedFrame)

#TODO: Add object detection pipeline
            

            

