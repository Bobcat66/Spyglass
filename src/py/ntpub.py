import ntcore
from typing import List, Union
from vtypes import *
#The ntpub module provides an abstracted interface to the NetworkTables server.
#It functions as a module-level singleton object, so you can use it directly without instantiating it.

class NTPipePub():
    def __init__(self,pipename: str):
        #self.__pipename: str = pipename
        self.__table: ntcore.NetworkTable = __getPipeTable(pipename)
        self.__apriltag_results_pub: ntcore.DoubleArrayPublisher = self.__table.getDoubleArrayTopic("apriltag_results").publish(
            ntcore.PubSubOptions(periodic=0.01, sendAll=True, keepDuplicates=True)
        )
        self.__objdetect_results_pub: ntcore.DoubleArrayPublisher = self.__table.getDoubleArrayTopic("objdetect_results").publish(
            ntcore.PubSubOptions(periodic=0.01, sendAll=True, keepDuplicates=True)
        )
        self.__apriltag_fps_pub: ntcore.IntegerPublisher = self.__table.IntegerTopic("apriltag_fps").publish()
        self.__objdetect_fps_pub: ntcore.IntegerPublisher = self.__table.IntegerTopic("objdetect_fps").publish()
        _publishers.append(self)
    
    def publishApriltagResult(
            self,
            timestamp: int, #microseconds since FPGA epoch
            result: Union[ApriltagResult,None],
            fiducialResults: List[FiducialDistResult]
        ) -> None:
        result_data: List[float] = [0] #1st element indicates the number of results
        if result != None:
            result_data[0] = 1
            result_data.append(result.pose_0.translation().X())
            result_data.append(result.pose_0.translation().Y())
            result_data.append(result.pose_0.translation().Z())
            result_data.append(result.pose_0.rotation().getQuaternion().W())
            result_data.append(result.pose_0.rotation().getQuaternion().X())
            result_data.append(result.pose_0.rotation().getQuaternion().Y())
            result_data.append(result.pose_0.rotation().getQuaternion().Z())
            if (result.pose_1 != None):
                result_data[0] = 2
                result_data.append(result.pose_1.translation().X())
                result_data.append(result.pose_1.translation().Y())
                result_data.append(result.pose_1.translation().Z())
                result_data.append(result.pose_1.rotation().getQuaternion().W())
                result_data.append(result.pose_1.rotation().getQuaternion().X())
                result_data.append(result.pose_1.rotation().getQuaternion().Y())
                result_data.append(result.pose_1.rotation().getQuaternion().Z())
        for fiducial in fiducialResults:
            result_data.append(fiducial.id)
            for corner in fiducial.corners.ravel(): # corners are stored as a 2d array, numpy's ravel method flattens them into a 1d array for networktables
                result_data.append(corner)
            result_data.append(fiducial.distance)
        self.__apriltag_results_pub.set(result_data,timestamp)
    
    def publishObjDetectResult(
            self,
            timestamp: int, #microseconds since FPGA epoch
            results: List[ObjDetectResult]
        ) -> None:
        result_data: List[float] = [0] #1st element indicates the number of results
        for res in results:
            result_data[0] = result_data[0] + 1
            result_data.append(res.obj_class)
            result_data.append(res.confidence)
            for corner in res.corners.ravel():
                result_data.append(corner)
        self.__objdetect_results_pub.set(result_data,timestamp)

    def publishApriltagFPS(self, fps: int, timestamp: int) -> None:
        self.__apriltag_fps_pub.set(fps,timestamp)

    def publishObjDetectFPS(self, fps: int, timestamp: int) -> None:    
        self.__objdetect_fps_pub.set(fps,timestamp)

#Initialize NT4 client
inst: ntcore.NetworkTableInstance = ntcore.NetworkTableInstance.getDefault()
inst.startClient4("visionclient")
inst.setServerTeam(1076)
_publishers: list[NTPipePub] = []
_gtname: str = "samuraisight"

def getGlobalTable() -> ntcore.NetworkTable:
    """
    Returns the global NT table.
    """
    return inst.getTable(_gtname)

def __getPipeTable(pipename : str) -> ntcore.NetworkTable:
    return inst.getTable(_gtname + '/' + pipename)
    