# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../src/core')))

import cv2
from pipeline import annotations, pnpsolvers
from pipeline.ApriltagDetector import ApriltagDetector
from utils.vtypes import *
from configuration.config_types import CameraConfig, FieldConfig
import numpy as np
from time import perf_counter_ns
import robotpy_apriltag as apriltag

import sys
import os
sys.path.append(os.path.abspath('..'))

if __name__ == "__main__":
    cam = cv2.VideoCapture(0)
    result, image = cam.read()
    detector = ApriltagDetector()
    detector.addFamily("tag36h11")
    fakeCameraConf = CameraConfig(
        name="Camera is directly captured by openCV for testing, only the intrinsics matter",
        device_number=69,
        calibration=True,
        camera_matrix=np.array([
            [
                979.1087360312252 / 1.5,
                0,
                608.5591334099096
            ],
            [
                0,
                979.8457780935689 / 1.5,
                352.9815581130428
            ],
            [
                0,
                0,
                1
            ]
        ], dtype=np.float64),
        dist_coeffs=np.array([
            0.09581952042360092,
            -0.2603932345361037,
            0.0035795949814343524,
            -0.005134231272255606,
            0.19101200082384226
        ], dtype=np.float64),
        pixel_format=None,
        xres=1280,
        yres=720,
        fps=60
    ) # These coefficients are based on my laptop's webcam
    fakeFieldConf = FieldConfig(
        tag_size=0.1651,
        layout=apriltag.AprilTagFieldLayout.loadField(apriltag.AprilTagField.k2025ReefscapeWelded),
        family="tag36h11"
    )
    fsolver = pnpsolvers.FiducialPnPSolver(fakeCameraConf,fakeFieldConf)
    solver = pnpsolvers.GeneralPnPSolver(fakeCameraConf,fakeFieldConf)
    lastFPS = perf_counter_ns()
    frameCounter = 0
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        gsframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detections = detector.detect(gsframe)
        annotations.drawFiducials(frame, detections)
        for detection in detections:
            result = fsolver.solve(detection)
            if result != None:
                #print(result)
                annotations.drawSingleTagPose(frame, result, fakeFieldConf, fakeCameraConf)
                print(cv2.norm(result.tvecs_0))
        ntagres = solver.solve(detections)
        #if ntagres is not None: print(ntagres.pose_0.translation())
        cv2.imshow('Webcam Feed', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frameCounter += 1
        if perf_counter_ns() - lastFPS >= 1e9:
            print(f"{frameCounter} fps")
            frameCounter = 0
            lastFPS = perf_counter_ns()
    cam.release()
    cv2.destroyAllWindows()