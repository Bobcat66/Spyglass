# MIT License
#
# Copyright (c) 2025 FRC 1076 PiHi Samurai
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
        

