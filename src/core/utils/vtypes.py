# MIT License
#
# Copyright (c) 2025 FRC 1076 PiHi Samurai
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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

# Single tag pose results are supposed to be field-agnostic, which is why they have taf
@dataclass(frozen=True)
class SingleTagPoseResult:
    id: int
    corners: numpy.typing.NDArray[numpy.float64]
    decisionMargin: float
    hammingDist: float
    distance: float
    rvecs_0: numpy.typing.NDArray[numpy.float64]
    tvecs_0: numpy.typing.NDArray[numpy.float64]
    tag_pose_0: Pose3d # Pose of the tag from the camera's coordinate frame
    error_0: float
    rvecs_1: numpy.typing.NDArray[numpy.float64]
    tvecs_1: numpy.typing.NDArray[numpy.float64]
    tag_pose_1: Pose3d
    error_1: float

@dataclass(frozen=True)
class NTagPoseResult:
    field_pose_0: Pose3d
    error_0: float
    field_pose_1: Union[Pose3d, None] #The SolvePnP algorithm sometimes can return two poses, but only one is valid. This Union is meant to approximate an optional
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



