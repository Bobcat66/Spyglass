#This file is to test the Apriltag detector on a USB camera
#Everything is hardcoded for now, this is just a test

import cv2
import numpy as np
import pipeline.tagdetector as tagdetector
from pipeline.pnpsolvers import GeneralPnPSolver
from pipeline.annotator import drawFiducials
from time import perf_counter_ns
if __name__ == "__main__":
    #testimage = cv2.imread("apriltag_test.png", cv2.IMREAD_GRAYSCALE)
    testimage = cv2.imread("apriltag_test.png")
    begin = perf_counter_ns()
    detections = tagdetector.detectCV_BGR(testimage)
    end = perf_counter_ns()
    #colorImage = cv2.cvtColor(testimage, cv2.COLOR_GRAY2BGR)
    drawFiducials(testimage, detections)
    print("Detections: ", len(detections))
    print("Time taken: ", (end - begin) / 1e6 , "ms")
    cv2.imshow("test", testimage)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
