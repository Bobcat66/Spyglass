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
from typing import List,Union
from configuration.config_types import CameraConfig, CameraIntrinsics
from video.CameraHandler import CameraHandler
import logging

logger = logging.getLogger(__name__)

_cameras: dict[str,CameraHandler] = {}
_validCameras: list[int] = [caminfo.dev for caminfo in cscore.UsbCamera.enumerateUsbCameras()]

def loadCameras(cameraList: List[CameraConfig]) -> None:
    for camConfig in cameraList:
        if camConfig.device_number not in _validCameras:
            logger.warning("Camera %d does not exist",camConfig.device_number)
            continue
        camera = CameraHandler(camConfig)
        logger.debug("Acquired camera %s",camera._camera.getPath())
        _cameras[camConfig.name] = camera

def getCamera(name: str) -> Union[CameraHandler,None]:
    cam = _cameras.get(name)
    if cam is None:
        logger.warning("Camera '%s' not found",name)
    return cam