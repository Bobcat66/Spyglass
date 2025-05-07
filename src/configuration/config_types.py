
from dataclasses import dataclass
import numpy as np
import cscore
import robotpy_apriltag as apriltag
from typing import Union, Dict, List

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
    family: str

@dataclass
class DeviceConfig:
    """Device configuration class."""
    name: str #The device ID
    server_ip: str #The IP address of the networktables server
    
@dataclass
class ApriltagConfig:
    """Apriltag-specific pipeline configuration"""
    excludeTags: List[int] #Tags to reject completely
    excludeTagsPNP: List[int] #Tags to reject in multitag PNP solving, they will still be used for single-tag distance estimation
    detConfigs: Union[apriltag.AprilTagDetector.Config,None]
    detQtps: Union[apriltag.AprilTagDetector.QuadThresholdParameters,None]

@dataclass
class ObjDetectConfig:
    """Object detection-specific pipeline configuration"""
    model: str
    confidenceThreshold: float

@dataclass
class PipelineConfig:
    """Vision pipeline configuration class."""
    name: str
    type: str
    camera: str
    grayscale: bool
    stream: bool
    stream_xres: int
    stream_yres: int
    rawport: Union[int,None]
    processedport: Union[int,None]
    objdetectConfig: Union[ObjDetectConfig,None]
    apriltagConfig: Union[ApriltagConfig,None]
 
