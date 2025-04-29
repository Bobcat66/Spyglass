import robotpy_apriltag as apriltag
import numpy as np
import cv2
from wpimath.geometry import *
from typing import List, Union
from vtypes import Fiducial, ApriltagResult
from coords import wpilibTranslationToOpenCv, openCvPoseToWpilib

class ApriltagPnPSolver():
    def __init__(
        self, 
        field: apriltag.AprilTagFieldLayout, 
        tag_size: float,
        camera_matrix: np.typing.NDArray[np.float64], 
        dist_coeffs:  np.typing.NDArray[np.float64]
    ):
        self.__field: apriltag.AprilTagFieldLayout = field
        self.__tag_size: float = tag_size
        self.__camera_matrix: np.typing.NDArray[np.float64] = camera_matrix
        self.__dist_coeffs: np.typing.NDArray[np.float64] = dist_coeffs
    
    def solve(self,fiducials: List[Fiducial]) -> Union[ApriltagResult, None]:
        """
        Solves the Perspective-n-Point problem using the fiducials detected by the camera.
        :param fiducials: List of Fiducial detections
        """
        object_points: List[float] = []
        tag_ids: List[int] = []
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
                _, rvecs, tvecs, errors = cv2.solvePnP(
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
            return ApriltagResult(tag_ids, field_to_camera_pose_0, errors[0][0], field_to_camera_pose_1, errors[1][0])
        else:
            # Solve for multiple tags
            try:
                _, rvecs, tvecs, errors = cv2.solvePnP(
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
            
            return ApriltagResult(tag_ids, field_to_camera_pose, errors[0][0], None, None)




        



        

    

    

    








