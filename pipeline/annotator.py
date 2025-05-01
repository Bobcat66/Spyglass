# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

import cv2
from utils.vtypes import Fiducial, SingleTagPoseResult
from typing import List
from configuration.config_types import *


def drawFiducials(image: cv2.Mat, fiducials: List[Fiducial]) -> None:
    '''
    Annotates fiducial detections on a BGR image
    '''
    for f in fiducials:
        bottom_left = tuple(f.corners[0].astype(int))
        bottom_right = tuple(f.corners[1].astype(int))
        top_right = tuple(f.corners[2].astype(int))
        top_left = tuple(f.corners[3].astype(int))
        cv2.line(image, bottom_left, bottom_right, (0, 255, 0), 2)
        cv2.line(image, bottom_right, top_right, (0, 255, 0), 2)
        cv2.line(image, top_right, top_left, (0, 255, 0), 2)
        cv2.line(image, top_left, bottom_left, (0, 255, 0), 2)
        cv2.putText(image, str(f.id), (top_left[0],top_left[1]-15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

def drawSingleTagPose(
    image: cv2.Mat, 
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

