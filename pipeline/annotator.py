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
    Draw a Single Tag Pose estimate
    :param image: The image to draw on.
    :param fiducialPose: The list of fiducial poses to draw.
    :param fieldConf: The field configuration.
    :param camConf: The camera configuration.
    """
    if result.error_0 > result.error_1: #I am aware the greater than sign should be flipped, this is a temporary measure until I figure out why the mirrored pose returned by IPPE square has less error than the true pose.
        cv2.drawFrameAxes(
            image,
            camConf.camera_matrix,
            camConf.dist_coeffs,
            result.rvecs_0,
            result.tvecs_0,
            fieldConf.tag_size/2
        )
    else:
        cv2.drawFrameAxes(
            image,
            camConf.camera_matrix,
            camConf.dist_coeffs,
            result.rvecs_1,
            result.tvecs_1,
            fieldConf.tag_size/2
        )

#TODO: Add object detection overlay

