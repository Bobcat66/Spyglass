# Copyright (c) Jesse Kane
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

from video.CameraHandler import CameraHandler
from typing import Callable, Tuple, List, Union
from calibration.common import CalibrationModule, Seed, BoardObservation, CalibrationInput
from calibration import loader
import numpy as np
import cv2.aruco as aruco
import cv2
import logging
import traceback
import json
import os

logger = logging.getLogger(__name__)

class CalibrationSession():
    def __init__(self,
        camera: CameraHandler,
        capTrigger: Callable[[],bool],
        endTrigger: Callable[[],bool],
        resolution: Tuple[int,int],
        useMrcal: bool,
        board_size: Tuple[int,int],
        square_len: float,
        marker_len: float,
        dictionary: aruco.Dictionary,
        seed: Seed = None,
        use_seed: bool = False
    ):
        self._resolution = resolution
        self._board = aruco.CharucoBoard(board_size,square_len,marker_len,dictionary)
        self._input = camera.getSink()
        self._capture = capTrigger
        self._end = endTrigger
        self._calibrator : CalibrationModule = None
        self._use_seed = use_seed
        if useMrcal:
            self._calibrator = loader.getMrcal()
        else:
            self._calibrator = loader.getOpenCV()

        self._seed = Seed(0,0,0,0,0,0,0,0,0)
        if use_seed:
            self._seed = seed
        
        self._detector = aruco.CharucoDetector(self._board)
        self._observations: List[BoardObservation] = []
        self._ids: List[np.typing.NDArray[np.int16]]
        self._path = f"output/calib/{camera.name}/{self._resolution[0]}x{self._resolution[1]}.json"
    
    def process(self,frame: cv2.Mat, capture: bool) -> Union[cv2.Mat,None]:
        framecopy = frame.copy()

        try:
            charuco_corners, charuco_ids, marker_corners, marker_ids = self._detector.detectBoard(frame)
            aruco.drawDetectedMarkers(framecopy,marker_corners,marker_ids)
            aruco.drawDetectedCornersCharuco(framecopy,charuco_corners,charuco_ids)
            for index,obs in enumerate(self._observations):
                aruco.drawDetectedCornersCharuco(framecopy,obs.img_points,self._ids[index])
            if capture:
                objpts,imgpts= self._board.matchImagePoints(charuco_corners,charuco_ids)
                self._observations.append(BoardObservation(objpts,imgpts,None)) #TODO: ADD WEIGHTS!!!!!
            return framecopy

        except Exception as e:
            logger.warning(f"Unable to process frame due to an unhandled exception.")
            traceback.print_exc()
            return
    
    def end(self) -> None:
        if len(self._observations) == 0:
            logger.error("No calibration data")
            return
        if not os.path.isdir(os.path.dirname(self._path)):
            os.makedirs(os.path.dirname(self._path))
        calInput = CalibrationInput(
            self._observations,
            self._resolution,
            self._seed,
            self._use_seed
        )
        results = self._calibrator.calibrate(calInput)
        with open(self._path,"w") as cfile:
            cfile.write(results.dumpJson())
        logger.info("Calibration complete. Results stored at %s",os.path.join(os.getcwd(),self._path))
    
    def run(self):
        frame: cv2.Mat = np.zeros(shape=(1,1,1),dtype=np.uint8)
        prevCap: bool = False
        while not self._end():
            cap = self._capture()
            time, frame = self._input.grabFrame(frame)
            self.process(frame, cap and not prevCap)
        
