# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

import cv2
import numpy as np
from utils.vtypes import *
from configuration.config_types import PipelineConfig, CameraIntrinsics
from pipeline.ApriltagDetector import ApriltagDetector
from pipeline.ObjectDetector import ObjectDetector
from pipeline import Annotator, pnpsolvers
from typing import Tuple
from time import perf_counter_ns
import logging
from configuration import Field

logger = logging.getLogger(__name__)
class Pipeline:

    def preprocess(self, frame: cv2.Mat) -> cv2.Mat:
        raise NotImplementedError("Pipeline.run() must be implemented by subclasses.")

    def process(self, frame: cv2.Mat) -> PipelineResult:
        """
        Run the pipeline.
        """
        raise NotImplementedError("Pipeline.run() must be implemented by subclasses.")

    def benchmark(self,frame: cv2.Mat) -> Tuple[int,PipelineResult]:
        t0 = perf_counter_ns()
        res = self.process(frame)
        t1 = perf_counter_ns()
        return t1-t0,res
    
    def deepBenchmark(self,frame: cv2.Mat) -> Tuple[List[int],PipelineResult]:
        """
        provides a more detailed benchmark, giving data on the performance of both the processing step and the postprocessing step
        """
        raise NotImplementedError("Pipeline.deepBenchmark() must be implemented by subclasses.")
    
class ApriltagPipeline(Pipeline):
    """
    A pipeline for detecting and solving AprilTags. Expects a grayscale frame
    """
    def __init__(
        self,
        detector: ApriltagDetector,
        solver: pnpsolvers.GeneralPnPSolver,
        fidSolver: pnpsolvers.FiducialPnPSolver,
        annotator: Annotator.Annotator,
        stream: bool
    ):
        self._detector = detector
        self._solver = solver
        self._fidSolver = fidSolver
        self._annotator = annotator
        self._stream = stream

    def preprocess(self, frame):
        return cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    
    def process(self,frame: cv2.Mat) -> PipelineResult:
        """
        Run the pipeline.
        """
        ppFrame = self.preprocess(frame)
        # Process the frame
        fiducials = self._detector.detect(ppFrame)
        nTagResult = self._solver.solve(fiducials)
        singleTagResults: List[Tuple[SingleTagPoseResult,Fiducial]] = []
        for fiducial in fiducials:
            stres = self._fidSolver.solve(fiducial)
            if stres != None:
                singleTagResults.append((stres,fiducial))
        
        distResults: List[TagDistResult] = []
        annotatedFrame = None
        if self._stream:
            annotatedFrame = cv2.cvtColor(ppFrame, cv2.COLOR_GRAY2BGR)
            self._annotator.drawFiducials(annotatedFrame, fiducials)
        for result in singleTagResults:
            if self._stream: self._annotator.drawSingleTagPose(annotatedFrame, result[0])
            distResults.append(TagDistResult(
                result[1].id,
                result[1].corners,
                result[1].decisionMargin,
                result[1].hammingDist,
                np.linalg.norm(result[0].tvecs_0 if result[0].error_0 <= result[0].error_1 else result[0].tvecs_1)
            ))

        apriltagResult = ApriltagResult(distResults,nTagResult)
        
        return PipelineResult(apriltagResult,None,annotatedFrame)

    def deepBenchmark(self, frame: cv2.Mat) -> Tuple[List[int],PipelineResult]:
        timestamps: List[int] = []

        
        timestamps.append(perf_counter_ns())
        ppFrame = self.preprocess(frame)
        timestamps.append(perf_counter_ns())
        # Process the frame
        fiducials = self._detector.detect(ppFrame)
        timestamps.append(perf_counter_ns())

        nTagResult = self._solver.solve(fiducials)
        timestamps.append(perf_counter_ns())

        singleTagResults: List[Tuple[SingleTagPoseResult,Fiducial]] = []
        for fiducial in fiducials:
            stres = self._fidSolver.solve(fiducial)
            if stres != None:
                singleTagResults.append((stres,fiducial))
        timestamps.append(perf_counter_ns())
        
        distResults: List[TagDistResult] = []
        annotatedFrame = None
        if self._stream:
            annotatedFrame = cv2.cvtColor(ppFrame, cv2.COLOR_GRAY2BGR)
            self._annotator.drawFiducials(annotatedFrame, fiducials)
        for result in singleTagResults:
            if self._stream: self._annotator.drawSingleTagPose(annotatedFrame, result[0])
            distResults.append(TagDistResult(
                result[1].id,
                result[1].corners,
                result[1].decisionMargin,
                result[1].hammingDist,
                np.linalg.norm(result[0].tvecs_0 if result[0].error_0 <= result[0].error_1 else result[0].tvecs_1)
            ))
        timestamps.append(perf_counter_ns())


        apriltagResult = ApriltagResult(distResults,nTagResult)
        return timestamps,PipelineResult(apriltagResult,None,annotatedFrame)

        
    
#TODO: Add object detection pipeline
            
class ObjDetectPipeline(Pipeline):
    def __init__(self, detector: ObjectDetector, stream: bool, grayscale: bool, annotator: Annotator.Annotator):
        self._detector = detector
        self._annotator = annotator
        self._grayscale = grayscale
        self._stream = stream
    
    def preprocess(self, frame: cv2.Mat) -> cv2.Mat:
        if self._grayscale:
            return cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        else:
            return frame.copy()

    def process(self,frame: cv2.Mat) -> PipelineResult:
        ppFrame = self.preprocess(frame)
        results = self._detector.detect(ppFrame)
        annotatedFrame: Union[cv2.Mat,None] = None
        if self._stream:
            annotatedFrame = cv2.cvtColor(ppFrame,cv2.COLOR_GRAY2BGR) if self._grayscale else ppFrame
            self._annotator.drawObjDetectResults(annotatedFrame,results,self._detector.getClassNames())
        return PipelineResult(None,results,annotatedFrame)
    
    def deepBenchmark(self, frame: cv2.Mat) -> Tuple[List[int],PipelineResult]:
        timestamps: List[int] = []
        timestamps.append(perf_counter_ns())
        ppFrame = self.preprocess(frame)
        timestamps.append(perf_counter_ns())
        results = self._detector.detect(ppFrame)
        timestamps.append(perf_counter_ns())
        annotatedFrame: Union[cv2.Mat,None] = None
        if self._stream:
            annotatedFrame = cv2.cvtColor(ppFrame,cv2.COLOR_GRAY2BGR) if self._grayscale else ppFrame
            self._annotator.drawObjDetectResults(annotatedFrame,results,self._detector.getClassNames())
        timestamps.append(perf_counter_ns())
        return timestamps, PipelineResult(None,results,annotatedFrame)
    
def buildPipeline(pipConf: PipelineConfig, intrinsics: CameraIntrinsics) -> Pipeline:
    match pipConf.type:
        case "apriltag":
            solver = pnpsolvers.GeneralPnPSolver(intrinsics,pipConf.apriltagConfig.excludeTagsPNP)
            fidSolver = pnpsolvers.FiducialPnPSolver(intrinsics)
            detector = ApriltagDetector()
            detector.addFamily(Field.getFamily())
            if pipConf.apriltagConfig is not None:
                if pipConf.apriltagConfig.detConfigs is not None:
                    detector.setConfig(pipConf.apriltagConfig.detConfigs)
                if pipConf.apriltagConfig.detQtps is not None:
                    detector.setQuadThresholdParameters(pipConf.apriltagConfig.detQtps)
            detector.setRejectlist(pipConf.apriltagConfig.excludeTags)
            annotator = Annotator.Annotator(intrinsics,pipConf.apriltagConfig.excludeTagsPNP)
            return ApriltagPipeline(pipConf.name,detector,solver,fidSolver,annotator,pipConf.stream)
        case "objdetect":
            detector = ObjectDetector(pipConf.objdetectConfig.model,intrinsics)
            annotator = Annotator.Annotator(intrinsics)
            return ObjDetectPipeline(detector,pipConf.stream,pipConf.grayscale,annotator)