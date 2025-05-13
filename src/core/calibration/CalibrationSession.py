from video.CameraHandler import CameraHandler
from typing import Callable, Tuple, Dict
from calibration.common import CalibrationModule, Seed
from calibration import loader
import numpy as np
import math
import cv2.aruco as aruco

class CalibrationSession():
    def __init__(self,
        camera: CameraHandler,
        capTrigger: Callable[[],bool],
        useMrcal: bool,
        board_size: Tuple[int,int],
        square_len: float,
        marker_len: float,
        dictionary: aruco.Dictionary,
        seed: Seed = None,
        use_seed: bool = False
    ):
        self._input = camera.getSink()
        self._capture = capTrigger
        self._calibrator : CalibrationModule = None
        if useMrcal:
            self._calibrator = loader.getMrcal()
        else:
            self._calibrator = loader.getOpenCV()

        _seed = Seed(0,0,0,0,0,0,0,0,0)
        if use_seed:
            _seed = seed
        
        self._detector = aruco.CharucoDetector(
            aruco.CharucoBoard(board_size,square_len,marker_len,dictionary)
        )
        
        