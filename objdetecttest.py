# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

import cv2
from pipeline import annotator
from pipeline.ObjectDetector import ObjectDetector
from utils.vtypes import *
from configuration.config_types import CameraConfig, FieldConfig
import numpy as np

if __name__ == "__main__":
    cam = cv2.VideoCapture(0)
    result, image = cam.read()
    fakeCameraConf = CameraConfig(
        "Fake camera that doesn't exist",
        69,
        True,
        np.array([
            [
                979.1087360312252,
                0,
                608.5591334099096
            ],
            [
                0,
                979.8457780935689,
                352.9815581130428
            ],
            [
                0,
                0,
                1
            ]
        ], dtype=np.float64),
        np.array([
            0.09581952042360092,
            -0.2603932345361037,
            0.0035795949814343524,
            -0.005134231272255606,
            0.19101200082384226
        ], dtype=np.float64),
        None,
        1280,
        720,
        30
    ) # These coefficients are based on my laptop's webcam
    detector = ObjectDetector(fakeCameraConf,"models/yolo11n.pt")
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        detections = detector.detect(frame)
        annotator.drawObjDetectResults(frame,detections,detector.getClassNames())
        cv2.imshow('Webcam Feed', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()