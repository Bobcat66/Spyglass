from abc import ABC, abstractmethod
import cv2
import cv2.aruco as aruco
from dataclasses import dataclass
import numpy as np
from typing import Tuple, List

# This module contains the portions of the calibration toolkit that are platform-agnostic. 

# SamuraiSight only supports ChArUco boards

@dataclass
class BoardObservation:
    object_points: np.typing.NDArray[np.float64]
    img_points: np.typing.NDArray[np.float64]
    weights: np.typing.NDArray[np.float64]

@dataclass
class CalibrationInput:
    observations: List[BoardObservation]
    size: Tuple[int,int]
    fx_seed: float
    fy_seed: float

@dataclass
class CalibrationData:
    size: Tuple[int,int]
    matrix: List[List[float]] #These have to be basic lists in order to keep them JSON-serializable
    dist_coeffs: List[float]
    avg_reproject_err: float

    def getNumpyMat(self) -> np.typing.NDArray[np.float64]:
        return np.array(self.matrix,dtype=np.float64)
    
    def getNumpyDistCoeffs(self) -> np.typing.NDArray[np.float64]:
        return np.array(self.dist_coeffs,dtype=np.float64)

class CharucoDetector():
    def __init__(self,)




    
    


    