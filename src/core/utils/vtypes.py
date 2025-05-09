# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

from dataclasses import dataclass
from typing import List, Union
from wpimath.geometry import Pose3d
import numpy
import cv2

@dataclass(frozen=True)
class Fiducial:
    id: int
    corners: numpy.typing.NDArray[numpy.float64]
    decisionMargin: float
    hammingDist: float

@dataclass(frozen=True)
class TagDistResult:
    id: int
    corners: numpy.typing.NDArray[numpy.float64]
    decisionMargin: float
    hammingDist: float
    distance: float

@dataclass(frozen=True)
class SingleTagPoseResult:
    id: int
    corners: numpy.typing.NDArray[numpy.float64]
    decisionMargin: float
    hammingDist: float
    distance: float
    rvecs_0: numpy.typing.NDArray[numpy.float64]
    tvecs_0: numpy.typing.NDArray[numpy.float64]
    pose_0: Pose3d
    error_0: float
    rvecs_1: numpy.typing.NDArray[numpy.float64]
    tvecs_1: numpy.typing.NDArray[numpy.float64]
    pose_1: Pose3d
    error_1: float

@dataclass(frozen=True)
class NTagPoseResult:
    pose_0: Pose3d
    error_0: float
    pose_1: Union[Pose3d, None] #The SolvePnP algorithm sometimes can return two poses, but only one is valid. This Union is meant to approximate an optional
    error_1: Union[float, None]

@dataclass(frozen=True)
class ObjDetectResult:
    obj_class: int
    confidence: float
    percent_area: float
    corner_angles: numpy.typing.NDArray[numpy.float64] #The euler angles of the bounding box corners relative to the principal axis of the camera, in radians
    corner_pixels: numpy.typing.NDArray[numpy.float64] #the actual pixel locations of the bounding box corners

@dataclass(frozen=True)
class ApriltagResult:
    fiducials: List[SingleTagPoseResult]
    poseResult: Union[NTagPoseResult,None]

@dataclass(frozen=True)
class PipelineResult:
    apriltagResult: Union[ApriltagResult,None]
    objDetectResults: Union[List[ObjDetectResult],None]
    frame: Union[cv2.Mat,None]



