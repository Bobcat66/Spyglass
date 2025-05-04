# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

import cv2
import numpy as np
from utils.vtypes import *
from configuration.config_types import CameraConfig, FieldConfig, PipelineConfig
from pipeline.ApriltagDetector import ApriltagDetector
from pipeline.ObjectDetector import ObjectDetector
from pipeline import annotator, pnpsolvers
from typing import Tuple
from time import perf_counter_ns
import logging

logger = logging.getLogger(__name__)
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

    def benchmark(self,frame: cv2.Mat) -> Tuple[int,PipelineResult]:
        t0 = perf_counter_ns()
        res = self.process(frame)
        t1 = perf_counter_ns()
        if verbose: logger.info(f"{self.name} benchmarked at {t1-t0/1e6:.3f} ms per cycle")
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
        name: str,
        detector: ApriltagDetector,
        solver: pnpsolvers.GeneralPnPSolver,
        fidSolver: pnpsolvers.FiducialPnPSolver,
        stream: bool,
        fieldConf: FieldConfig,
        camConf: CameraConfig
    ):
        super().__init__(name)
        self._detector = detector
        self._solver = solver
        self._fidSolver = fidSolver
        self._stream = stream
        self._fieldConf = fieldConf
        self._camConf = camConf
    
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
                singleTagResults.append((stres,fiducial))
        
        distResults: List[TagDistResult] = []
        annotatedFrame: Union[cv2.Mat,None] = None
        if self._stream:
            # Annotate the frame
            annotatedFrame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            annotator.drawFiducials(annotatedFrame, fiducials)
            for result in singleTagResults:
                annotator.drawSingleTagPose(annotatedFrame, result[0], self._fieldConf, self._camConf)
                distResults.append(TagDistResult(
                    result[1].id,
                    result[1].corners,
                    result[1].decisionMargin,
                    result[1].hammingDist,
                    np.linalg.norm(result[0].tvecs_0 if result[0].error_0 <= result[0].error_1 else result[0].tvecs_1)
                ))
        else:
            for result in singleTagResults:
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
        # Process the frame

        fiducials = self._detector.detect(frame)
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
        annotatedFrame: Union[cv2.Mat,None] = None
        if self._stream:
            # Annotate the frame
            annotatedFrame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            annotator.drawFiducials(annotatedFrame, fiducials)
            for result in singleTagResults:
                annotator.drawSingleTagPose(annotatedFrame, result[0], self._fieldConf, self._camConf)
                distResults.append(TagDistResult(
                    result[1].id,
                    result[1].corners,
                    result[1].decisionMargin,
                    result[1].hammingDist,
                    np.linalg.norm(result[0].tvecs_0 if result[0].error_0 <= result[0].error_1 else result[0].tvecs_1)
                ))
        else:
            for result in singleTagResults:
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
    def __init__(self,name: str, detector: ObjectDetector, stream: bool, grayscale: bool):
        super().__init__(name)
        self._detector = detector
        self._stream = stream
        self._grayscale = grayscale

    def process(self,frame: cv2.Mat) -> PipelineResult:
        results = self._detector.detect(frame)
        annotatedFrame: Union[cv2.Mat,None] = None
        if self._stream:
            annotatedFrame = cv2.cvtColor(frame,cv2.COLOR_GRAY2BGR) if self._grayscale else frame
            annotator.drawObjDetectResults(frame,results,self._detector.getClassNames())
        return PipelineResult(None,results,annotatedFrame)
    
    def deepBenchmark(self, frame: cv2.Mat) -> Tuple[List[int],PipelineResult]:
        timestamps: List[int] = []
        timestamps.append(perf_counter_ns())
        results = self._detector.detect(frame)
        timestamps.append(perf_counter_ns())
        annotatedFrame: Union[cv2.Mat,None] = None
        if self._stream:
            annotatedFrame = cv2.cvtColor(frame,cv2.COLOR_GRAY2BGR) if self._grayscale else frame
            annotator.drawObjDetectResults(frame,results,self._detector.getClassNames())
        timestamps.append(perf_counter_ns())
        
        return timestamps, PipelineResult(None,results,annotatedFrame)






    
def buildPipeline(pipConf: PipelineConfig, camConf: CameraConfig, fieldConf: FieldConfig) -> Pipeline:
    match pipConf.type:
        case "apriltag":
            solver = pnpsolvers.GeneralPnPSolver(camConf,fieldConf)
            fidSolver = pnpsolvers.FiducialPnPSolver(camConf,fieldConf)
            detector = ApriltagDetector()
            detector.addFamily(fieldConf.family)
            if pipConf.detConfigs is not None:
                detector.setConfig(pipConf.detConfigs)
            if pipConf.detQtps is not None:
                detector.setQuadThresholdParameters(pipConf.detQtps)
            return ApriltagPipeline(pipConf.name,detector,solver,fidSolver,pipConf.stream,fieldConf,camConf)
        case "objdetect":
            detector = ObjectDetector(camConf,pipConf.model)
            return ObjDetectPipeline(pipConf.name,detector,pipConf.stream,pipConf.grayscale)