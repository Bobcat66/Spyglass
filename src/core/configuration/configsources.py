# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

import tomllib
from configuration.config_types import *
import robotpy_apriltag as apriltag
import logging
from configuration import Field

logger = logging.getLogger(__name__)
class ConfigParser:
    pixelFormatDict = {
        "kUnknown": cscore.VideoMode.PixelFormat.kUnknown,
        "kGray": cscore.VideoMode.PixelFormat.kGray,
        "kBGR": cscore.VideoMode.PixelFormat.kBGR,
        "kYUYV": cscore.VideoMode.PixelFormat.kYUYV,
        "kMJPEG": cscore.VideoMode.PixelFormat.kMJPEG,
        "kRGB": cscore.VideoMode.PixelFormat.kRGB565,
        "kBGRA": cscore.VideoMode.PixelFormat.kBGRA,
    }
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = self.loadConfig()

    def loadConfig(self):
        with open(self.config_file, 'rb') as f:
            return tomllib.load(f)

    def getConfig(self, key: str):
        return self.config.get(key, None)
    
    def _getCameraDicts(self) -> dict:
        cdict = self.config.get("cameras")
        if cdict is None:
            logger.warning("no cameras configured")
        return cdict
    
    def _getPipelineDicts(self) -> dict:
        pdict = self.config.get("pipelines")
        if pdict is None:
            logger.warning("no pipelines configured")
        return pdict
    
    def getCameraConfigs(self) -> List[CameraConfig]:
        cam_configs = []
        for camera_name,configDict in self._getCameraDicts().items():
            cam_configs.append(CameraConfig(
                camera_name,
                configDict.get("dev_id"),
                configDict.get("calibration"),
                CameraIntrinsics(
                    np.array(configDict.get("matrix"), dtype=np.float64),
                    np.array(configDict.get("distortion"), dtype=np.float64)
                ) if configDict.get("calibration") else None,
                self.pixelFormatDict.get(configDict.get("pixel_format"), cscore.VideoMode.PixelFormat.kUnknown),
                configDict.get("xres"),
                configDict.get("yres"),
                configDict.get("fps")
            ))
        return cam_configs
        
    
    def loadFieldConfig(self) -> None:
        fieldDict: dict = self.config.get("field")
        if fieldDict is None:
            logger.warning("Field is not configured")
            return
        tag_size = fieldDict.get("tag_size")
        family = fieldDict.get("family")
        layoutName = fieldDict.get("layout")
        Field.setTagSize(tag_size)
        Field.setFamily(family)
        Field.loadLayout(layoutName)
    
    #TODO: Add separate stream resolution
    def getPipelineConfigs(self) -> List[PipelineConfig]:
        config_list = []
        for pipeline_name,pipedict in self._getPipelineDicts().items():
            type = pipedict.get("type",None)
            camera: str = pipedict.get("camera",None)
            if camera is None:
                logger.error("No camera configuration detected for pipeline %s",pipeline_name)
                continue
            stream: bool = pipedict.get("stream",False)
            stream_xres: int = pipedict.get("stream_xres",320)
            stream_yres: int = pipedict.get("stream_yres",240)
            stream_fps: int = pipedict.get("stream_fps",30)
            rawport: int = pipedict.get("rawport",None)
            processedport: int = pipedict.get("processedport",None)
            if stream and (rawport is None):
                logger.warning("Streaming enabled on pipeline %s, but no raw video port detected. Raw stream will be disabled",pipeline_name)
            if stream and (processedport is None):
                logger.warning("Streaming enabled on pipeline %s, but no processed video port detected. Processed stream will be disabled",pipeline_name)    
            match type:
                case "apriltag":
                    #Apriltag pipelines are always grayscale
                    atconf = apriltag.AprilTagDetector.Config()
                    atconf.debug = pipedict.get("debug",False)
                    atconf.decodeSharpening = pipedict.get("decodeSharpening",0.25)
                    atconf.numThreads = pipedict.get("numThreads",1)
                    atconf.quadDecimate = pipedict.get("quadDecimate",2.0)
                    atconf.quadSigma = pipedict.get("quadSigma",0.0)
                    atconf.refineEdges = pipedict.get("refineEdges",True)
                    qtps = apriltag.AprilTagDetector.QuadThresholdParameters()
                    qtps.criticalAngle = pipedict.get("criticalAngle",45.0)
                    qtps.deglitch = pipedict.get("deglitch",False)
                    qtps.maxLineFitMSE = pipedict.get("maxLineFitMSE",10.0)
                    qtps.maxNumMaxima = pipedict.get("maxNumMaxima",10)
                    qtps.minClusterPixels = pipedict.get("minClusterPixels",300)
                    qtps.minWhiteBlackDiff = pipedict.get("minWhiteBlackDiff",5)
                    config = PipelineConfig(
                        pipeline_name,
                        "apriltag",
                        camera,
                        True,
                        stream,
                        stream_xres,
                        stream_yres,
                        stream_fps,
                        rawport,
                        processedport,
                        None,
                        ApriltagConfig(
                            pipedict.get("excludeTags",[]),
                            pipedict.get("excludeTagsPNP",[]),
                            atconf,
                            qtps
                        )
                    )
                    config_list.append(config)
                case "objdetect":
                    config = PipelineConfig(
                        pipeline_name,
                        "apriltag",
                        camera,
                        True,
                        stream,
                        stream_xres,
                        stream_yres,
                        stream_fps,
                        rawport,
                        processedport,
                        ObjDetectConfig(
                            pipedict.get("model"),
                            pipedict.get("confidenceThreshold") #Doesn't do anything at the moment
                        ),
                        None
                    )
                    continue
                case None:
                    logger.error("No pipeline type detected for pipeline %s",pipeline_name)
                    continue
                case _:
                    logger.error("'%s' is not recognized as a valid pipeline type for %s",type,pipeline_name)
                    continue
        return config_list


    
    def dump(self):
        return self.config