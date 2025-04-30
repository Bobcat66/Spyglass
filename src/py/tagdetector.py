# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

import robotpy_apriltag as apriltag
import numpy as np
from collections.abc import Buffer
from typing import List
from vtypes import Fiducial

#Module level singleton that encapsulates the apriltag detector

_detector: apriltag.AprilTagDetector = apriltag.AprilTagDetector()
_detector.addFamily("tag36h11")

def toFiducial(detection: apriltag._apriltag.AprilTagDetection) -> Fiducial:
    """
    Convert an AprilTag detection to a Fiducial object.
    :param detection: The AprilTag detection to convert.
    :return: The converted Fiducial object.
    """
    return Fiducial(
        detection.id,
        np.array(detection.corners, dtype=np.float64).reshape((4, 2))
    )

def detect(image: Buffer) -> List[Fiducial]:
    return [toFiducial(detection) for detection in _detector.detect(image)]

def detectCV(image: np.typing.NDArray[np.uint8]) -> List[Fiducial]:
    return detect(image.tobytes())

def setConfig(config: apriltag._apriltag.AprilTagDetector.Config) -> None:
    """
    Set the configuration of the detector.
    """
    _detector.setConfig(config)

def getConfig() -> apriltag._apriltag.AprilTagDetector.Config:
    """
    Get the configuration of the detector.
    :return: The configuration of the detector.
    """
    return _detector.getConfig()

def addFamily(fam: str) -> bool:
    """
    Add a family to the detector.
    :param fam: The family to add.
    :return: True if the family was added, False otherwise.
    """
    return _detector.addFamily(fam)

def removeFamily(fam: str) -> None:
    """
    Remove a family from the detector.
    :param fam: The family to remove.
    """
    _detector.removeFamily(fam)

def getQuadThresholdParameters() -> apriltag._apriltag.AprilTagDetector.QuadThresholdParameters:
    """
    Get the quad threshold parameter of the detector.
    :return: The quad threshold parameter of the detector.
    """
    return _detector.getQuadThresholdParameters()


def setQuadThresholdParameters(params: apriltag._apriltag.AprilTagDetector.QuadThresholdParameters) -> None:
    """
    Set the quad threshold parameter of the detector.
    :param params: The quad threshold parameter to set.
    """
    _detector.setQuadThresholdParameters(params)

def clearFamilies() -> None:
    """
    Clear all families from the detector.
    """
    _detector.clearFamilies()
