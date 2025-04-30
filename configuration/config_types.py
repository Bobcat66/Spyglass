
from dataclasses import dataclass
import numpy as np
import cscore
import robotpy_apriltag as apriltag
from typing import Union

@dataclass
class CameraConfig:
    """Camera configuration class."""
    name: str
    device_number: int #The device number of the camera. e.g. 0 for a camera connected to /dev/video0
    calibration: bool #True if the camera is calibrated, false otherwise
    camera_matrix: Union[np.typing.NDArray[np.float64],None] #The camera matrix of the camera
    dist_coeffs: Union[np.typing.NDArray[np.float64],None] #The distortion coefficients of the camera
    pixel_format: cscore.VideoMode.PixelFormat #The pixel format of the camera
    xres: int #The width of the camera in pixels
    yres: int #The height of the camera in pixels
    fps: int #The frames per second of the camera

@dataclass
class FieldConfig:
    """Field configuration class."""
    tag_size: float #The size of the tags in meters
    layout: apriltag.AprilTagFieldLayout #The field layout of the field

@dataclass
class DeviceConfig:
    """Device configuration class."""
    name: str #The device ID of the camera
    dev_ip: str #The IP address of the camera
    server_ip: str #The IP address of the networktables server

