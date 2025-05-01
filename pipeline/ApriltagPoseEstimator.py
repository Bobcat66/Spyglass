import numpy as np
import cv2

from configuration.config_types import CameraConfig, FieldConfig
from pipeline import tagdetector
from pipeline import pnpsolvers
from typing import List, Union, Tuple
from utils.vtypes import *
from pipeline.ApriltagDetector import ApriltagDetector

class ApriltagPoseEstimator():
    '''
    Takes a greyscale image and returns a pose estimate based on the fiducials in the image
    '''
    def __init__(self,camConf: CameraConfig, fieldConf: FieldConfig):
        self._solver = pnpsolvers.GeneralPnPSolver(camConf, fieldConf)
        self._fidSolver = pnpsolvers.FiducialPnPSolver(camConf, fieldConf)
        self._detector = ApriltagDetector()
    
    def process(self, image: cv2.Mat) -> Tuple[Union[NTagPoseResult, None],List[SingleTagPoseResult]]:
        """
        Process a BGR image and return the pose of the fiducials in the image.
        :param image: The BGR image to process.
        :return: The pose of the fiducials in the image.
        """
        detections = self._detector.detect(image)
        result = self._solver.solve(detections)
        singleTagResults: List[SingleTagPoseResult] = []
        for detection in detections:
            stres = self._fidSolver.solve(detection)
            if stres != None:
                singleTagResults.append(stres)
        return (result, singleTagResults)


        