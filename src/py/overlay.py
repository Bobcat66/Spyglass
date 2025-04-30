# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

import cv2
import numpy as np
from vtypes import Fiducial, SingleTagPoseResult
from typing import List
from configuration import *

def drawFiducials(image: np.typing.NDArray[np.uint8], fiducials: List[Fiducial]) -> None:
    cv2.aruco.drawDetectedMarkers(image, np.array([f.corners for f in fiducials]), np.array([f.id for f in fiducials]))

def drawSingleTagPose(
    image: np.typing.NDArray[np.uint8], 
    result: SingleTagPoseResult, 
    fieldConf: FieldConfig, 
    camConf: CameraConfig
) -> None:
    """
    Draw the axes of a Single Tag Pose estimate
    :param image: The image to draw on.
    :param fiducialPose: The list of fiducial poses to draw.
    :param fieldConf: The field configuration.
    :param camConf: The camera configuration.
    """
    cv2.drawFrameAxes(
        image,
        camConf.camera_matrix,
        camConf.dist_coeffs,
        result.pose_0.rotation().toVector(),
        result.pose_0.translation().toVector(),
        fieldConf.tag_size/2
    )
    cv2.drawFrameAxes(
        image,
        camConf.camera_matrix,
        camConf.dist_coeffs,
        result.pose_1.rotation().toVector(),
        result.pose_1.translation().toVector(),
        fieldConf.tag_size/2
    )

#TODO: Add object detection overlay

