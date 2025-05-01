import cv2
from pipeline import pnpsolvers,annotator
from pipeline.ApriltagDetector import ApriltagDetector
from utils.vtypes import *
from configuration.config_types import CameraConfig, FieldConfig
import numpy as np

if __name__ == "__main__":
    cam = cv2.VideoCapture(0)
    result, image = cam.read()
    detector = ApriltagDetector()
    detector.addFamily("tag36h11")
    fakeCameraConf = CameraConfig(
        "Fake camera that doesn't exist",
        69,
        True,
        np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float64),
        np.array([0, 0, 0, 0, 0], dtype=np.float64),
        None,
        640,
        480,
        60
    )
    fakeFieldConf = FieldConfig(
        tag_size=0.1651,
        layout=None,
        family="tag36h11"
    )
    solver = pnpsolvers.FiducialPnPSolver(fakeCameraConf,fakeFieldConf)
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        gsframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detections = detector.detect(gsframe)
        annotator.drawFiducials(frame, detections)
        for detection in detections:
            result = solver.solve(detection)
            if result != None:
                #print(result)
                annotator.drawSingleTagPose(frame, result, fakeFieldConf, fakeCameraConf)
        cv2.imshow('Webcam Feed', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()