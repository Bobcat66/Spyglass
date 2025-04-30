#This file is to test the Apriltag detector on a USB camera
#Everything is hardcoded for now, this is just a test

import cscore
import cv2
import numpy as np
import pipeline.tagdetector as tagdetector
from pipeline.pnpsolvers import CameraPnPSolver
from pipeline.annotations import drawFiducials

if __name__ == "__main__":
    testimage = cv2.imread("apriltag_test.png")
    print(testimage.shape)
    detections = tagdetector.detectCV(testimage)
    drawFiducials(testimage, detections)
    cv2.imshow("test", testimage)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
