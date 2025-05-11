import cscore
from typing import List,Union
from configuration.config_types import CameraConfig, CameraIntrinsics
from CameraHandler import CameraHandler
import logging
import numpy as np

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


            
