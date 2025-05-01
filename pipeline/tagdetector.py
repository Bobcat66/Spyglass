# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

import robotpy_apriltag as apriltag
import numpy as np
import cv2
from collections.abc import Buffer
from typing import List
from utils.vtypes import Fiducial

#Module level singleton that encapsulates the apriltag detector

#TODO: Add configurator
_detector: apriltag.AprilTagDetector = apriltag.AprilTagDetector()
_detector.addFamily("tag36h11")

def toFiducial(detection: apriltag._apriltag.AprilTagDetection) -> Fiducial:
    """
    Convert an AprilTag detection to a Fiducial object.
    :param detection: The AprilTag detection to convert.
    :return: The converted Fiducial object.
    """
    corners: List[float] = []
    for i in range(4):
        cornerPoint: apriltag._apriltag.AprilTagDetection.Point = detection.getCorner(i)
        corners += [cornerPoint.x, cornerPoint.y]

    return Fiducial(
        detection.getId(),
        np.array(corners, dtype=np.float64).reshape((4, 2))
    )

def _detect(image: Buffer) -> List[Fiducial]:
    rawdetections: List[apriltag.AprilTagDetection] = _detector.detect(image)
    return [toFiducial(detection) for detection in rawdetections]

def detectCV_GS(image: np.typing.NDArray[np.uint8]) -> List[Fiducial]:
    """
    Detect AprilTags in a grayscale image.
    :param image: The grayscale image to detect AprilTags in.
    :return: A list of detected AprilTags.
    DEPRECATED
    """
    return _detect(image)

def detectCV_BGR(image: np.typing.NDArray[np.uint8]) -> List[Fiducial]:
    """
    Detect AprilTags in a color image (BGR).
    :param image: The color image to detect AprilTags in.
    :return: A list of detected AprilTags.
    DEPRECATED
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return _detect(gray_image)

def detectCV_RGB(image: np.typing.NDArray[np.uint8]) -> List[Fiducial]:
    """
    Detect AprilTags in a color image (RGB).
    :param image: The color image to detect AprilTags in.
    :return: A list of detected AprilTags.
    DEPRECATED
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return _detect(gray_image)

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

def clearFamilies() -> None:
    """
    Clear all families from the detector.
    """
    _detector.clearFamilies()
