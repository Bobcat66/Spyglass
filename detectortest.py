#This file is to test the Apriltag detector on a USB camera
#Everything is hardcoded for now, this is just a test

import cscore
import cv2
import numpy as np
import pipeline.tagdetector as tagdetector
from pipeline.pnpsolvers import CameraPnPSolver
from pipeline.annotations import drawFiducials
from time import perf_counter_ns
if __name__ == "__main__":
    testimage = cv2.imread("apriltag_test.png")
    begin = perf_counter_ns()
    detections = tagdetector.detectCV(testimage)
    drawFiducials(testimage, detections)
    end = perf_counter_ns()
    print("Time taken: ", (end - begin) / 1e6 , "ms")
    cv2.imshow("test", testimage)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
