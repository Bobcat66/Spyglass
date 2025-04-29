import robotpy_apriltag as apriltag
import numpy as np
import tagdetector
import cscore
import timesync
from pnpsolvers import CameraPnPSolver, IPPESquarePnPSolver
from wpimath.geometry import *
from typing import List, Union
from vtypes import Fiducial, ApriltagResult, FiducialDistResult, FiducialPoseResult
from coords import wpilibTranslationToOpenCv, openCvPoseToWpilib
from src.py.ntpubsub import NTPipePub

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
        self.__solver: CameraPnPSolver = CameraPnPSolver(field, tag_size, camera_matrix, dist_coeffs)
        self.__fidsolver: IPPESquarePnPSolver = IPPESquarePnPSolver(tag_size,camera_matrix,dist_coeffs)
        self.__sink: cscore.CvSink = cscore.CvSink(name + "_input",pixelMode,width,height,fps)
        self.__sink.setSource(source)
        self.__source: cscore.CvSource = cscore.CvSource(name + "_output",pixelMode,width,height,fps)
        self.__tmpMat: np.typing.NDArray[np.uint8]
        self.__pub: NTPipePub = NTPipePub(name)
    
    def process(self) -> None:
        """
        Process the input image and detect AprilTags.
        """
        self.__tmpMat = self.__sink.grabFrame()
        detections = tagdetector.detectCV(self.__tmpMat)
        result = self.__solver.solve(detections)
        fiducialDists: List[FiducialDistResult] = []
        for detection in detections:
            fiducialDist = self.__generateTagDistance(detection)
            if fiducialDist != None:
                fiducialDists.append(fiducialDist)
        self.__pub.publishApriltagResult(
            timesync.getFPGA(),
            result,
            fiducialDists
        )
        self.__source.putFrame(self.__tmpMat)
        
    
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
    
    def getSource(self) -> cscore.CvSource:
        """
        Get the source of the pipeline.
        :return: The source of the pipeline.
        """
        return self.__source


        


        
