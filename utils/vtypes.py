# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

from dataclasses import dataclass
from typing import List, Union
from wpimath.geometry import Pose3d
import numpy

@dataclass(frozen=True)
class Fiducial:
    id: int
    corners: numpy.typing.NDArray[numpy.float64]

@dataclass(frozen=True)
class FiducialDistResult:
    id: int
    corners: numpy.typing.NDArray[numpy.float64]
    distance: float

@dataclass(frozen=True)
class SingleTagPoseResult:
    id: int
    corners: numpy.typing.NDArray[numpy.float64]
    pose_0: Pose3d
    error_0: float
    pose_1: Pose3d
    error_1: float

@dataclass(frozen=True)
class NTagPoseResult:
    fid_ids: List[int]
    pose_0: Pose3d
    error_0: float
    pose_1: Union[Pose3d, None] #The SolvePnP algorithm sometimes can return two poses, but only one is valid. This Union is meant to approximate an optional
    error_1: Union[float, None]

@dataclass(frozen=True)
class ObjDetectResult:
    obj_class: int
    confidence: float
    corners: numpy.typing.NDArray[numpy.float64] #corners of the bounding rectangle

