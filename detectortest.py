#This file is to test the Apriltag detector on a USB camera
#Everything is hardcoded for now, this is just a test

import cscore
import numpy as np
import pipeline.tagdetector as tagdetector
from pipeline.pnpsolvers import CameraPnPSolver

if __name__ == "__main__":
    camera_name: str = "TEST_CAMERA"
    device_number: int = 0
    cameraSource: cscore.UsbCamera = cscore.UsbCamera(camera_name, device_number)
    cameraSource.setVideoMode(cscore.VideoMode.PixelFormat.kMJPEG, 640, 480, 30)
    sink: cscore.CvSink = cscore.CvSink(camera_name + "_input")
    sink.setSource(cameraSource)
    tmpmat: np.typing.NDArray[np.uint8] = np.ndarray([])

    while False:
        sink.grabFrame(tmpmat)
        results = tagdetector.detectCV(tmpmat)
        for result in results:
            print(result.id, result.corners)

