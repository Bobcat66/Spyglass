import tomllib
from configuration.config_types import *
import robotpy_apriltag as apriltag
import logging

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
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_file, 'rb') as f:
            return tomllib.load(f)
        

    def get_config(self, key: str):
        return self.config.get(key, None)
    
    def get_dev_config(self):
        devDict: dict = self.config.get("device")
        return DeviceConfig(
            devDict.get("name"),
            devDict.get("dev_ip"),
            devDict.get("server_ip")
        )
    
    def _get_camera_configs(self) -> dict:
        cdict = self.config.get("cameras")
        if cdict is None:
            logger.warning("no cameras configured")
    
    def _get_pipeline_configs(self) -> dict:
        pdict = self.config.get("pipelines")
        if pdict is None:
            logger.warning("no pipelines configured")
    
    def get_camera_config(self, camera_name: str) -> Union[CameraConfig,None]:
        configDict: dict = self._get_camera_configs().get(camera_name, None)
        if configDict is None:
            logger.warning("camera %s not configured",camera_name)
            return None
        return CameraConfig(
            camera_name,
            configDict.get("dev_id"),
            configDict.get("calibration"),
            np.ndarray(configDict.get("matrix"), dtype=np.float64) if configDict.get("calibration") else None,
            np.ndarray(configDict.get("distortion"), dtype=np.float64) if configDict.get("calibration") else None,
            self.pixelFormatDict.get(configDict.get("pixel_format"), cscore.VideoMode.PixelFormat.kUnknown),
            configDict.get("xres"),
            configDict.get("yres"),
            configDict.get("fps")
        )
    
    def get_field_config(self) -> Union[FieldConfig,None]:
        fieldDict: dict = self.config.get("field")
        if fieldDict is None:
            logger.warning("Field is not configured")
            return None
        tag_size = fieldDict.get("tag_size")
        family = fieldDict.get("family")
        layout = apriltag.AprilTagFieldLayout("../resources/fields/" + fieldDict.get("layout") + ".json")
        return FieldConfig(
            tag_size,
            layout,
            family
        )
    
    #TODO: Add separate stream resolution
    def get_pipeline_config(self, pipeline_name: str) -> Union[PipelineConfig,None]:
        pipedict: dict = self._get_pipeline_configs().get(pipeline_name)
        if pipedict is None:
            logger.warning("No pipeline named '%s' detected",pipeline_name)
        type = pipedict.get("type",None)
        camera: str = pipedict.get("camera",None)
        if camera is None:
            logger.error("No camera configuration detected for pipeline %s",pipeline_name)
        stream: bool = pipedict.get("stream",False)
        stream_xres: int = pipedict.get("stream_xres",320)
        stream_yres: int = pipedict.get("stream_yres",240)
        rawport: int = pipedict.get("rawport",None)
        processedport: int
        if stream and (rawport is None):
            logger.warning("Streaming enabled on pipeline %s, but no raw video port detected. Raw stream will be disabled",pipeline_name)
        if stream and (processedport is None):
            logger.warning("Streaming enabled on pipeline %s, but no processed video port detected. Processed stream will be disabled",pipeline_name)
        

        match type:
            case "apriltag":
                #Apriltag
                config = PipelineConfig(
                )
                pass
            case "objdetect":
                #Object detection
                pass
            case None:
                logger.error("No pipeline type detected for pipeline %s",pipeline_name)
                return None
            case _:
                logger.error("'%s' is not recognized as a valid pipeline type for %s",type,pipeline_name)
                return None


    
    def dump(self):
        return self.config