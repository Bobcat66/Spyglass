# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../src/core')))
import robotpy_apriltag as apriltag
import numpy as np
import ntcore
import cscore
from network import ntmanager
from processes.PipelineWorker import PipelineWorker
from video.CameraHandler import CameraHandler
from utils.misc import releaseGIL

from configuration.config_types import CameraConfig, PipelineConfig, CameraIntrinsics
from configuration import Field
import logging
# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(threadName)s(%(name)s): %(message)s'
)

ntmanager.initialize("Test",ntcore.NetworkTableInstance.getDefault())

Field.setFamily("tag36h11")
Field.setLayout(apriltag.AprilTagFieldLayout.loadField(apriltag.AprilTagField.k2025ReefscapeWelded))
Field.setTagSize(1.651)
camConfig = CameraConfig(
    "webcam",
    0,
    True,
    CameraIntrinsics(
        np.array([
            [979.1087360312252,0.000000000000000,608.5591334099096],
            [0.000000000000000,979.8457780935689,352.9815581130428],
            [0.000000000000000,0.000000000000000,1.000000000000000]
        ], dtype=np.float64),
        np.array([
            0.09581952042360092,
            -0.2603932345361037,
            0.0035795949814343524,
            -0.005134231272255606,
            0.19101200082384226
        ], dtype=np.float64)
    ),
    cscore.VideoMode.PixelFormat.kYUYV,
    1280,
    720,
    30
)

pipeConfig = PipelineConfig(
    "test_pipe",
    "apriltag",
    "webcam",
    True,
    True,
    1280,
    720,
    30,
    8000,
    8001,
    None,
    None
)

camera = CameraHandler(camConfig)
visworker = PipelineWorker(pipeConfig,camera)
visworker.start()
while True:
    releaseGIL()