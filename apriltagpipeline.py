import robotpy_apriltag as apriltag
import numpy as np
import cv2
import tagdetector
import cscore
from pnpsolvers import CameraPnPSolver
from wpimath.geometry import *
from typing import List, Union
from vtypes import Fiducial, ApriltagResul
from pipeline.coords import wpilibTranslationToOpenCv, openCvPoseToWpilib
from ntpub import NTPipePub

class AprilTagPipeline():

    def __init__(
        self, 
        name: str,
        field: apriltag.AprilTagFieldLayout, 
        tag_size: float,
        camera_matrix: np.typing.NDArray[np.float64], 
        dist_coeffs:  np.typing.NDArray[np.float64],
        source: cscore.CvSource,
        pixelMode: cscore.VideoMode.PixelFormat,
        width: int,
        height: int,
        fps: int
    ):
        self.__name: str = name
        self.__field: apriltag.AprilTagFieldLayout = field
        self.__tag_size: float = tag_size
        self.__camera_matrix: np.typing.NDArray[np.float64] = camera_matrix
        self.__dist_coeffs: np.typing.NDArray[np.float64] = dist_coeffs
        self.__solver: CameraPnPSolver = CameraPnPSolver(field, tag_size, camera_matrix, dist_coeffs)
        self.__fidsolver: IPPESquarePnPSolver = IPPESquarePnPSolver(tag_size,camera_matrix,dist_coeffs)
        self.__sink: cscore.CvSink = cscore.CvSink(name + "_input",pixelMode,width,height,fps)
        self.__sink.setSource(source)
        self.__source: cscore.CvSource = cscore.CvSource(name + "_output",pixelMode,width,height,fps)
        self.__tmpMat: cscore.Mat
        self.__pub: NTPipePub = NTPipePub(name)
    
    def process(self) -> None:
        """
        Process the input image and detect AprilTags.
        """
        self.__tmpMat = self.__sink.grabFrame()
        detections = tagdetector.detect(self.__tmpMat)
        result = self.__solver.solve(detections)
        fiducialDists: List[FiducialDistResult] = []
        for (detection in detections):
            fiducialDist = self.__generateTagDistance(detection)
            if fiducialDist != None:
                fiducialDists.append(fiducialDist)
        
    
    def __generateTagDistance(self,fiducial: Fiducial) -> Union[FiducialDistResult,None]:
        """
        Generate the distance of the fiducial from the camera.
        :param fiducial: The fiducial to generate the distance for.
        :return: The distance of the fiducial from the camera.
        """
        fidpose: Union[FiducialPoseResult,None] = self.__fidsolver.solve(fiducial)
        if fidpose == None:
            return None
        return FiducialDistResult(
            fidpose.id,
            fidpose.corners,
            fidpose.pose_0.translation().norm()
        )


        


        
