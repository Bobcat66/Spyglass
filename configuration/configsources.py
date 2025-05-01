import tomllib
from configuration.config_types import *
import robotpy_apriltag as apriltag

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
        return self.config.get("cameras")
    
    def get_camera_config(self, camera_name: str) -> CameraConfig:
        configDict: dict = self._get_camera_configs().get(camera_name, None)
        if configDict is None:
            raise ValueError(f"Camera {camera_name} not found in configuration.")
        return CameraConfig(
            camera_name,
            configDict.get("dev_id"),
            configDict.get("calibration"),
            np.ndarray(configDict.get("matrix"), dtype=np.float64),
            np.ndarray(configDict.get("distortion"), dtype=np.float64),
            self.pixelFormatDict.get(configDict.get("pixel_format"), cscore.VideoMode.PixelFormat.kUnknown),
            configDict.get("xres"),
            configDict.get("yres"),
            configDict.get("fps")
        )
    
    def get_field_config(self) -> FieldConfig:
        fieldDict: dict = self.config.get("field")
        if fieldDict is None:
            raise ValueError("Field configuration not found in configuration.")
        tag_size = fieldDict.get("tag_size")
        family = fieldDict.get("family")
        layout = apriltag.AprilTagFieldLayout("resources/fields/" + fieldDict.get("layout"))
        return FieldConfig(
            tag_size,
            layout,
            family
        )
    
    def dump(self):
        return self.config