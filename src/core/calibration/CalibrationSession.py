from video.CameraHandler import CameraHandler
from typing import Callable, Tuple, List, Union
from calibration.common import CalibrationModule, Seed, BoardObservation
from calibration import loader
import numpy as np
import cv2.aruco as aruco
import cv2
import logging
import traceback

logger = logging.getLogger(__name__)

class CalibrationSession():
    def __init__(self,
        camera: CameraHandler,
        capTrigger: Callable[[],bool],
        endTrigger: Callable[[],bool],
        useMrcal: bool,
        board_size: Tuple[int,int],
        square_len: float,
        marker_len: float,
        dictionary: aruco.Dictionary,
        seed: Seed = None,
        use_seed: bool = False
    ):
        self._board = aruco.CharucoBoard(board_size,square_len,marker_len,dictionary)
        self._input = camera.getSink()
        self._capture = capTrigger
        self._end = endTrigger
        self._calibrator : CalibrationModule = None
        if useMrcal:
            self._calibrator = loader.getMrcal()
        else:
            self._calibrator = loader.getOpenCV()

        _seed = Seed(0,0,0,0,0,0,0,0,0)
        if use_seed:
            _seed = seed
        
        self._detector = aruco.CharucoDetector(self._board)
        self._frame: cv2.Mat = np.zeros(shape=(1,1,1),dtype=np.uint8)
        self._observations: List[BoardObservation] = []
        self._ids: List[np.typing.NDArray[np.int16]]
    
    def process(self,frame: cv2.Mat, capture: bool) -> Union[cv2.Mat,None]:
        framecopy = frame.copy()

        try:
            charuco_corners, charuco_ids, marker_corners, marker_ids = self._detector.detectBoard(frame)
            aruco.drawDetectedMarkers(framecopy,marker_corners,marker_ids)
            aruco.drawDetectedCornersCharuco(framecopy,charuco_corners,charuco_ids)
            for index,obs in enumerate(self._observations):
                aruco.drawDetectedCornersCharuco(framecopy,obs.img_points,self._ids[index])
            if capture:
                allcorners = self._board.getChessboardCorners()
                self._observations.append(BoardObservation())

        except Exception as e:
            logger.warning(f"Unable to process frame due to an unhandled exception.")
            traceback.print_exc()
            return
        
        