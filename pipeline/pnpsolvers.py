# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

import robotpy_apriltag as apriltag
import numpy as np
import cv2
from wpimath.geometry import *
from typing import List, Union
from utils.vtypes import Fiducial, NTagPoseResult, SingleTagPoseResult
from pipeline.coords import wpilibTranslationToOpenCv, openCvPoseToWpilib
from configuration.config_types import *

class GeneralPnPSolver():
    '''
    A PnP solver for cases with an arbitrary number of tags. When solving for multiple tags, the SQPnP algorith is used.
    In cases where only one tag is detected, the IPPE Square algorithm is used.
    '''
    def __init__(
        self, 
        camConf: CameraConfig,
        fieldConf: FieldConfig,
    ):
        self.__field: apriltag.AprilTagFieldLayout = fieldConf.layout
        self.__tag_size: float = fieldConf.tag_size
        self.__camera_matrix: np.typing.NDArray[np.float64] = camConf.camera_matrix
        self.__dist_coeffs: np.typing.NDArray[np.float64] = camConf.dist_coeffs
    
    def solve(self,fiducials: List[Fiducial]) -> Union[NTagPoseResult, None]:
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
            if fiducial.id in [tag.ID for tag in self.__field.getTags()]:
                fid_pose = self.__field.getTagPose(fiducial.id)
            if fid_pose != None:
                corner_0 = fid_pose + Transform3d(Translation3d(0, self.__tag_size / 2.0, -self.__tag_size / 2.0), Rotation3d())
                corner_1 = fid_pose + Transform3d(Translation3d(0, -self.__tag_size / 2.0, -self.__tag_size / 2.0), Rotation3d())
                corner_2 = fid_pose + Transform3d(Translation3d(0, -self.__tag_size / 2.0, self.__tag_size / 2.0), Rotation3d())
                corner_3 = fid_pose + Transform3d(Translation3d(0, self.__tag_size / 2.0, self.__tag_size / 2.0), Rotation3d())
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
                    [-self.__tag_size / 2.0, self.__tag_size / 2.0, 0],
                    [self.__tag_size / 2.0, self.__tag_size / 2.0, 0],
                    [self.__tag_size / 2.0, -self.__tag_size / 2.0, 0],
                    [-self.__tag_size / 2.0, -self.__tag_size / 2.0, 0],
                ]
            )
            try:
                _, rvecs, tvecs, errors = cv2.solvePnPGeneric(
                    object_points,
                    np.array(image_points),
                    self.__camera_matrix,
                    self.__dist_coeffs,
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
            return NTagPoseResult(tag_ids, field_to_camera_pose_0, errors[0][0], field_to_camera_pose_1, errors[1][0])
        else:
            # Solve for multiple tags
            try:
                _, rvecs, tvecs, errors = cv2.solvePnPGeneric(
                    np.array(object_points),
                    np.array(image_points),
                    self.__camera_matrix,
                    self.__dist_coeffs,
                    flags=cv2.SOLVEPNP_SQPNP
                )
            except:
                return None
            
            # Calculate WPILib camera poses
            camera_to_field_pose = openCvPoseToWpilib(tvecs[0], rvecs[0])
            camera_to_field = Transform3d(camera_to_field_pose.translation(), camera_to_field_pose.rotation())
            field_to_camera = camera_to_field.inverse()
            field_to_camera_pose = Pose3d(field_to_camera.translation(), field_to_camera.rotation())
            
            return NTagPoseResult(tag_ids, field_to_camera_pose, errors[0][0], None, None)

class FiducialPnPSolver():
    '''
    Solves the PnP problem for a single tag using the IPPE Square algorithm. This is heavily optimized for cases in which we are estimating pose based off a single fiducial
    '''
    def __init__(
        self,
        fieldConf: FieldConfig,
        camConf: CameraConfig,
    ):
        self.__tag_size: float = fieldConf.tag_size
        self.__camera_matrix: np.typing.NDArray[np.float64] = camConf.camera_matrix
        self.__dist_coeffs: np.typing.NDArray[np.float64] = camConf.dist_coeffs
    
    def solve(self,fiducial: Fiducial) -> Union[SingleTagPoseResult,None]:
        object_points = np.array(
            [
                [-self.__tag_size / 2.0, self.__tag_size / 2.0, 0],
                [self.__tag_size / 2.0, self.__tag_size / 2.0, 0],
                [self.__tag_size / 2.0, -self.__tag_size / 2.0, 0],
                [-self.__tag_size / 2.0, -self.__tag_size / 2.0, 0],
            ]
        )
        try:
            _, rvecs, tvecs, errors = cv2.solvePnP(
                object_points,
                np.array(fiducial.corners),
                self.__camera_matrix,
                self.__dist_coeffs,
                flags=cv2.SOLVEPNP_IPPE_SQUARE
            )
        except:
            return None
        
        camera_to_tag_pose_0 = openCvPoseToWpilib(tvecs[0], rvecs[0])
        camera_to_tag_pose_1 = openCvPoseToWpilib(tvecs[1], rvecs[1])
        return SingleTagPoseResult(
            fiducial.id,
            fiducial.corners,
            camera_to_tag_pose_0,
            errors[0][0],
            camera_to_tag_pose_1,
            errors[1][0]
        )





        



        

    

    

    








