# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

import robotpy_apriltag as apriltag
import numpy as np
import cv2
from typing import List
from utils.vtypes import Fiducial

def _toFiducial(detection: apriltag._apriltag.AprilTagDetection) -> Fiducial:
    """
    Convert an AprilTag detection to a Fiducial object.
    :param detection: The AprilTag detection to convert.
    :return: The converted Fiducial object.
    """
    #TODO: Maybe shift corner position in array for OpenCV? IDK
    corners: List[float] = []
    for i in range(4):
        cornerPoint: apriltag._apriltag.AprilTagDetection.Point = detection.getCorner(i)
        corners += [cornerPoint.x, cornerPoint.y]

    return Fiducial(
        detection.getId(),
        np.array(corners, dtype=np.float64).reshape((4, 2)),
        detection.getDecisionMargin(),
        detection.getHamming()
    )

class ApriltagDetector:
    """
    A class that encapsulates an apriltag detector.
    """
    def __init__(self):
        self._detector: apriltag.AprilTagDetector = apriltag.AprilTagDetector()
        self._ignorelist: List[int] = []
    
    def detect(self, image: cv2.Mat) -> List[Fiducial]:
        """
        Detect AprilTags in a grayscale image.
        :param image: A grayscale image to detect AprilTags in.
        :return: A list of detected AprilTags.
        """
        rawdetections: List[apriltag.AprilTagDetection] = self._detector.detect(image)
        return [_toFiducial(detection) for detection in rawdetections if self._filter(detection)]
    
    def _filter(self, detection: apriltag.AprilTagDetection) -> bool:
        """
        Filter function for detecting AprilTags.
        :param detection: The AprilTag detection to filter.
        :return: True if the detection passes the filter, False otherwise.
        """
        #TODO: Implement filtering logic
        return not (detection.getId() in self._ignorelist)
    
    def addFamily(self, family: str) -> None:
        """
        Add a family of AprilTags to the detector.
        :param family: The family of AprilTags to add.
        """
        self._detector.addFamily(family)
    
    def removeFamily(self, family: str) -> None:
        """
        Remove a family of AprilTags from the detector.
        :param family: The family of AprilTags to remove.
        """
        self._detector.removeFamily(family)
    
    def clearFamilies(self) -> None:
        """
        Clear all families from the detector.
        """
        self._detector.clearFamilies()
    
    def setConfig(self, config: apriltag.AprilTagDetector.Config) -> None:
        """
        Set the configuration for the AprilTag detector.
        :param config: The configuration to set.
        """
        self._detector.setConfig(config)
    
    def getConfig(self) -> apriltag._apriltag.AprilTagDetector.Config:
        """
        Get the current configuration of the AprilTag detector.
        :return: The current configuration.
        """
        return self._detector.getConfig()
    
    def setQuadThresholdParameters(self, params: apriltag.AprilTagDetector.QuadThresholdParameters) -> None:
        """
        Set the quad threshold parameters for the AprilTag detector.
        :param params: The quad threshold parameters to set.
        """
        self._detector.setQuadThresholdParameters(params)
    
    def getQuadThresholdParameters(self) -> apriltag.AprilTagDetector.QuadThresholdParameters:
        """
        Get the current quad threshold parameters of the AprilTag detector.
        :return: The current quad threshold parameters.
        """
        return self._detector.getQuadThresholdParameters()
    
    def setRejectlist(self,tags: List[int]) -> None:
        self._ignorelist = tags
    
    def getRejectlist(self) -> List[int]:
        return self._ignorelist.copy()