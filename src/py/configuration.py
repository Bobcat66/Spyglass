
from dataclasses import dataclass
import numpy as np
import cscore
import robotpy_apriltag as apriltag

@dataclass
class CameraConfig:
    """Camera configuration class."""
    name: str
    device_number: int #The device number of the camera. e.g. 0 for a camera connected to /dev/video0
    calibration: bool #True if the camera is calibrated, false otherwise
    camera_matrix: np.typing.NDArray[np.float64] #The camera matrix of the camera
    dist_coeffs: np.typing.NDArray[np.float64] #The distortion coefficients of the camera
    pixel_format: cscore.VideoMode.PixelFormat #The pixel format of the camera
    xres: int #The width of the camera in pixels
    yres: int #The height of the camera in pixels
    fps: int #The frames per second of the camera

@dataclass
class FieldConfig:
    """Field configuration class."""
    tag_size: float #The size of the tags in meters
    layout: apriltag.AprilTagFieldLayout #The field layout of the field