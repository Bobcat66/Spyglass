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
            logger.warning(f"camera {camera_name} not configured")
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
        tag_size = fieldDict.get("tag_size")
        family = fieldDict.get("family")
        layout = apriltag.AprilTagFieldLayout("resources/fields/" + fieldDict.get("layout") + ".json")
        return FieldConfig(
            tag_size,
            layout,
            family
        )
    
    def dump(self):
        return self.config