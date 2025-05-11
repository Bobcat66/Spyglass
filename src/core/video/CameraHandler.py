# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

import cscore
import numpy as np
from configuration.config_types import CameraConfig, CameraIntrinsics
from typing import Union, Tuple
import logging

logger = logging.getLogger(__name__)

class CameraHandler:
    def __init__(self,config: CameraConfig):
        self.name = config.name
        self._camera = cscore.UsbCamera(config.name,config.device_number)
        self._videoMode = cscore.VideoMode(config.pixel_format,config.xres,config.yres,config.fps)
        setVideoMode = self._camera.setVideoMode(self._videoMode)
        if not setVideoMode:
            logger.warning(f"Unable to configure camera {self.name}")
        self._intrinsics = config.intrinsics 
        self._sinkCounter: int = 0

    def getSink(self) -> cscore.CvSink:
        sink = cscore.CvSink(f"opencv_{self.name}_{self._sinkCounter}")
        self._sinkCounter += 1
        sink.setSource(self._camera)
        return sink
    
    def getVideoMode(self) -> cscore.VideoMode:
        return self._videoMode
    
    def getIntrinsics(self) -> Union[CameraIntrinsics,None]:
        if self._intrinsics is None:
            logger.warning("Camera %s is not calibrated",self.name)
        return self._intrinsics
    
    def getResolution(self) -> Tuple[int,int]:
        return self._videoMode.width,self._videoMode.height
    
    def getFPS(self) -> int:
        return self._videoMode.fps
    
    def getRawSource(self) -> cscore.UsbCamera:
        return self._camera
        

