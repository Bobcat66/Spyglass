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

import robotpy_apriltag as apriltag
import numpy as np
import cv2
from wpimath.geometry import *
from typing import List, Union
from utils.vtypes import Fiducial, NTagPoseResult, SingleTagPoseResult
from pipeline.coords import wpilibTranslationToOpenCv, openCvPoseToWpilib
from configuration.config_types import *
from configuration import Field

#TODO: Figure out the apriltag axes
class GeneralPnPSolver():
    '''
    A PnP solver for cases with an arbitrary number of tags. When solving for multiple tags, the SQPnP algorith is used.
    In cases where only one tag is detected, the IPPE Square algorithm is used.
    '''
    def __init__(
        self, 
        intrinsics: CameraIntrinsics,
        ignorelist: List[int]
    ):
        self._intrinsics = intrinsics
        self._ignorelist = ignorelist #list of tag ids to ignore
    
    def solve(self,fiducials: List[Fiducial]) -> Union[NTagPoseResult,None]:
        """
        Solves the Perspective-n-Point problem using the fiducials detected by the camera.
        :param fiducials: List of Fiducial detections
        """
        object_points: List[float] = []
        tag_ids: List[int] = []
        tag_poses: List[Pose3d] = []
        image_points: List[float] = []
        
        for fiducial in fiducials:
            fid_pose: Pose3d = None
            if fiducial.id in [tag.ID for tag in Field.getLayout().getTags()]:
                fid_pose = Field.getLayout().getTagPose(fiducial.id)
            if fid_pose != None:
                corner_0 = fid_pose + Transform3d(Translation3d(0, Field.getTagSize() / 2.0, -Field.getTagSize() / 2.0), Rotation3d())
                corner_1 = fid_pose + Transform3d(Translation3d(0, -Field.getTagSize() / 2.0, -Field.getTagSize() / 2.0), Rotation3d())
                corner_2 = fid_pose + Transform3d(Translation3d(0, -Field.getTagSize() / 2.0, Field.getTagSize() / 2.0), Rotation3d())
                corner_3 = fid_pose + Transform3d(Translation3d(0, Field.getTagSize() / 2.0, Field.getTagSize() / 2.0), Rotation3d())
                object_points += [
                    wpilibTranslationToOpenCv(corner_0.translation()),
                    wpilibTranslationToOpenCv(corner_1.translation()),
                    wpilibTranslationToOpenCv(corner_2.translation()),
                    wpilibTranslationToOpenCv(corner_3.translation()),
                ]
                image_points += [
                    [fiducial.corners[0][0], fiducial.corners[0][1]],
                    [fiducial.corners[1][0], fiducial.corners[1][1]],
                    [fiducial.corners[2][0], fiducial.corners[2][1]],
                    [fiducial.corners[3][0], fiducial.corners[3][1]],
                ]
                tag_ids.append(fiducial.id)
                tag_poses.append(fid_pose)
        if len(tag_ids) == 0:
            return None
        elif len(tag_ids) == 1:
            object_points = np.array(
                [
                    [-Field.getTagSize() / 2.0, Field.getTagSize() / 2.0, 0],
                    [Field.getTagSize() / 2.0, Field.getTagSize() / 2.0, 0],
                    [Field.getTagSize() / 2.0, -Field.getTagSize() / 2.0, 0],
                    [-Field.getTagSize() / 2.0, -Field.getTagSize() / 2.0, 0],
                ]
            )
            try:
                _, rvecs, tvecs, errors = cv2.solvePnPGeneric(
                    object_points,
                    np.array(image_points),
                    self._intrinsics.matrix,
                    self._intrinsics.dist_coeffs,
                    flags=cv2.SOLVEPNP_IPPE_SQUARE
                )
            except:
                return None
           
            # Calculate WPILib camera poses
            field_to_tag_pose = tag_poses[0]
            camera_to_tag_pose_0 = openCvPoseToWpilib(tvecs[0], rvecs[0])
            camera_to_tag_pose_1 = openCvPoseToWpilib(tvecs[1], rvecs[1])
            camera_to_tag_0 = Transform3d(camera_to_tag_pose_0.translation(), camera_to_tag_pose_0.rotation())
            camera_to_tag_1 = Transform3d(camera_to_tag_pose_1.translation(), camera_to_tag_pose_1.rotation())
            field_to_camera_0 = field_to_tag_pose.transformBy(camera_to_tag_0.inverse())
            field_to_camera_1 = field_to_tag_pose.transformBy(camera_to_tag_1.inverse())
            field_to_camera_pose_0 = Pose3d(field_to_camera_0.translation(), field_to_camera_0.rotation())
            field_to_camera_pose_1 = Pose3d(field_to_camera_1.translation(), field_to_camera_1.rotation())
            # Return result
            return NTagPoseResult(field_to_camera_pose_0, errors[0][0], field_to_camera_pose_1, errors[1][0])
        else:
            # Solve for multiple tags
            try:
                _, rvecs, tvecs, errors = cv2.solvePnPGeneric(
                    np.array(object_points),
                    np.array(image_points),
                    self._intrinsics.matrix,
                    self._intrinsics.dist_coeffs,
                    flags=cv2.SOLVEPNP_SQPNP
                )
            except:
                return None
            
            # Calculate WPILib camera poses
            camera_to_field_pose = openCvPoseToWpilib(tvecs[0], rvecs[0])
            camera_to_field = Transform3d(camera_to_field_pose.translation(), camera_to_field_pose.rotation())
            field_to_camera = camera_to_field.inverse()
            field_to_camera_pose = Pose3d(field_to_camera.translation(), field_to_camera.rotation())
            
            return NTagPoseResult(field_to_camera_pose, errors[0][0], None, None)

class FiducialPnPSolver():
    '''
    Solves the PnP problem for a single tag using the IPPE Square algorithm. This is heavily optimized for cases in which we are estimating pose based off a single fiducial
    '''
    def __init__(
        self,
        intrinsics: CameraIntrinsics
    ):
        self._intrinsics = intrinsics
    
    def solve(self,fiducial: Fiducial) -> Union[SingleTagPoseResult,None]:
        object_points = np.array(
            [
                [-Field.getTagSize() / 2.0, Field.getTagSize() / 2.0, 0],
                [Field.getTagSize() / 2.0, Field.getTagSize() / 2.0, 0],
                [Field.getTagSize() / 2.0, -Field.getTagSize() / 2.0, 0],
                [-Field.getTagSize() / 2.0, -Field.getTagSize() / 2.0, 0],
            ]
        )
        try:
            _, rvecs, tvecs, errors = cv2.solvePnPGeneric(
                object_points,
                fiducial.corners,
                self._intrinsics.matrix,
                self._intrinsics.dist_coeffs,
                flags=cv2.SOLVEPNP_IPPE_SQUARE
            )
        except:
            return None
          
        # Convert to WPILib coordinate system (Does NOT transform to the field frame)
        camera_to_tag_pose_0 = openCvPoseToWpilib(tvecs[0], rvecs[0])
        camera_to_tag_pose_1 = openCvPoseToWpilib(tvecs[1], rvecs[1])
        # Return result
        return SingleTagPoseResult(
            fiducial.id,
            fiducial.corners,
            fiducial.decisionMargin,
            fiducial.hammingDist,
            np.linalg.norm(tvecs[0] if errors[0][0] <= errors[1][0] else tvecs[1]),
            rvecs[0],
            tvecs[0],
            camera_to_tag_pose_0,
            errors[0][0],
            rvecs[1],
            tvecs[1],
            camera_to_tag_pose_1,
            errors[1][0]
        )

