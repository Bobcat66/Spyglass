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

import ntcore
from typing import List, Union
from utils.vtypes import *
import logging
logger = logging.getLogger(__name__)
inst: ntcore.NetworkTableInstance
_gtname: str

def initialize(name: str, ntinstance: ntcore.NetworkTableInstance) -> None:
    logger.info("ntmanager initialized")
    global _gtname, inst
    _gtname = name
    inst = ntinstance

class NTManager():
    def __init__(self,pipename: str):
        #self.__pipename: str = pipename
        self._table: ntcore.NetworkTable = _getPipeTable(pipename)
        self._apriltag_results_pub: ntcore.DoubleArrayPublisher = self._table.getDoubleArrayTopic("apriltag_results").publish(
            ntcore.PubSubOptions(periodic=0.01, sendAll=True, keepDuplicates=True)
        )
        self._objdetect_results_pub: ntcore.DoubleArrayPublisher = self._table.getDoubleArrayTopic("objdetect_results").publish(
            ntcore.PubSubOptions(periodic=0.01, sendAll=True, keepDuplicates=True)
        )
        self._fps_pub: ntcore.IntegerPublisher = self._table.getIntegerTopic("fps").publish()
    
    def publishApriltagResult(
            self,
            timestamp: int, #microseconds since FPGA epoch
            result: ApriltagResult
        ) -> None:
        result_data: List[float] = [0,0] #1st element indicates the number of results, 2nd element indicates number of apriltag detections
        if result.poseResult != None:
            result_data[0] = 1
            result_data.append(result.poseResult.field_pose_0.translation().X())
            result_data.append(result.poseResult.field_pose_0.translation().Y())
            result_data.append(result.poseResult.field_pose_0.translation().Z())
            result_data.append(result.poseResult.field_pose_0.rotation().getQuaternion().W())
            result_data.append(result.poseResult.field_pose_0.rotation().getQuaternion().X())
            result_data.append(result.poseResult.field_pose_0.rotation().getQuaternion().Y())
            result_data.append(result.poseResult.field_pose_0.rotation().getQuaternion().Z())
            if (result.poseResult.field_pose_1 != None):
                result_data[0] = 2
                result_data.append(result.poseResult.field_pose_1.translation().X())
                result_data.append(result.poseResult.field_pose_1.translation().Y())
                result_data.append(result.poseResult.field_pose_1.translation().Z())
                result_data.append(result.poseResult.field_pose_1.rotation().getQuaternion().W())
                result_data.append(result.poseResult.field_pose_1.rotation().getQuaternion().X())
                result_data.append(result.poseResult.field_pose_1.rotation().getQuaternion().Y())
                result_data.append(result.poseResult.field_pose_1.rotation().getQuaternion().Z())
        for fiducial in result.fiducials:
            result_data[1] = result_data[1] + 1
            result_data.append(fiducial.id)
            for corner in fiducial.corners.ravel(): # corners are stored as a 2d array, numpy's ravel method flattens them into a 1d array for networktables
                result_data.append(corner)
            result_data.append(fiducial.decisionMargin)
            result_data.append(fiducial.hammingDist)
            result_data.append(fiducial.distance)
            result_data.append(fiducial.tag_pose_0.translation().X())
            result_data.append(fiducial.tag_pose_0.translation().Y())
            result_data.append(fiducial.tag_pose_0.translation().Z())
            result_data.append(fiducial.tag_pose_0.rotation().getQuaternion().W())
            result_data.append(fiducial.tag_pose_0.rotation().getQuaternion().X())
            result_data.append(fiducial.tag_pose_0.rotation().getQuaternion().Y())
            result_data.append(fiducial.tag_pose_0.rotation().getQuaternion().Z())
            result_data.append(fiducial.tag_pose_1.translation().X())
            result_data.append(fiducial.tag_pose_1.translation().Y())
            result_data.append(fiducial.tag_pose_1.translation().Z())
            result_data.append(fiducial.tag_pose_1.rotation().getQuaternion().W())
            result_data.append(fiducial.tag_pose_1.rotation().getQuaternion().X())
            result_data.append(fiducial.tag_pose_1.rotation().getQuaternion().Y())
            result_data.append(fiducial.tag_pose_1.rotation().getQuaternion().Z())
        self._apriltag_results_pub.set(result_data,timestamp)
    
    def publishObjDetectResults(
            self,
            timestamp: int, #microseconds since FPGA epoch
            results: List[ObjDetectResult]
        ) -> None:
        result_data: List[float] = [0] #1st element indicates the number of results
        for res in results:
            result_data[0] = result_data[0] + 1
            result_data.append(res.obj_class)
            result_data.append(res.confidence)
            result_data.append(res.percent_area)
            for corner_angle in res.corner_angles.ravel():
                result_data.append(corner_angle)
            for corner_pixel in res.corner_pixels.ravel():
                result_data.append(corner_pixel)
        self._objdetect_results_pub.set(result_data,timestamp)
    
    def publishResult(
        self,
        timestamp: int,
        result: PipelineResult
    ):
        if result.apriltagResult is not None:
            self.publishApriltagResult(timestamp,result.apriltagResult)
        if result.objDetectResults is not None:
            self.publishObjDetectResults(timestamp,result.objDetectResults)
    
    def publishFPS(self, fps: int, timestamp: int) -> None:
        self._fps_pub.set(fps,timestamp)

def getGlobalTable() -> ntcore.NetworkTable:
    """
    Returns the global NT table.
    """
    return inst.getTable(_gtname)

def now() -> int:
    return ntcore._now()

def _getPipeTable(pipename : str) -> ntcore.NetworkTable:
    return inst.getTable(_gtname + '/' + pipename)

    