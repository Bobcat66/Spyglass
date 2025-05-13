from video import CameraHandler
from typing import Callable

class CalibrationSession():
    def __init__(self,camera: CameraHandler,capTrigger: Callable[[],bool],useMrcal:bool)