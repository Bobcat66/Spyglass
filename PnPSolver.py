import robotpy_apriltag as apriltag
import numpy as np
import cv2
from wpimath.geometry import *
from typing import List, Union
from vtypes import Fiducial, ApriltagResult

class PnPSolver():
    def __init__(self, field: apriltag.AprilTagFieldLayout, fid_size: float):
        self.__field: apriltag.AprilTagFieldLayout = field
        self.__fid_size: float = fid_size
    
    def solve(self,fiducials: List[Fiducial]):
        """
        Solves the Perspective-n-Point problem using the fiducials detected by the camera.
        :param fiducials: List of Fiducial detections
        """
        object_points = []
        image_points = []
        for fiducial in fiducials:
            tag_pose: Pose3d = None
            if fiducial.id in [tag.ID for tag in self.__field.getTags()]:
                tag_pose = self.__field.getTagPose(fiducial.id)
            if tag_pose != None:
                corner_0 = tag_pose + Transform3d(Translation3d(0, self.__fid_size / 2.0, -self.__fid_size / 2.0), Rotation3d())
                corner_1 = tag_pose + Transform3d(Translation3d(0, -self.__fid_size / 2.0, -self.__fid_size / 2.0), Rotation3d())
                corner_2 = tag_pose + Transform3d(Translation3d(0, -self.__fid_size / 2.0, self.__fid_size / 2.0), Rotation3d())
                corner_3 = tag_pose + Transform3d(Translation3d(0, self.__fid_size / 2.0, self.__fid_size / 2.0), Rotation3d())

        

    

    

    








