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

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../src/python/core')))
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