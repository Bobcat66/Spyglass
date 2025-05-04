
import ultralytics
from typing import List
import cv2
import ultralytics.engine.results
from configuration.config_types import CameraConfig
from utils.vtypes import ObjDetectResult
import numpy as np
import math

class ObjectDetector:

    def __init__(self, camConf: CameraConfig, model_path: str):
        """
        Initialize the ObjectDetector with a YOLO model.

        :param model_path: Path to the YOLO model file.
        """
        #This class is designed to help compute a 3DOF pose estimate of an arbitrary object
        #Using camera intrinsics, we normalize the corners of the points, which we can then use to calculate a ray from the camera to the corners of the bounding box
        #Using this ray (as well as the camera's extrinsic properties), we can work out the 3DOF pose of the object (Assuming the object is on the ground)
        self._model = ultralytics.YOLO(model_path,'detect')
        self._camConf = camConf

    def detect(self, frame: cv2.Mat) -> List[ObjDetectResult]:
        model_results: ultralytics.engine.results.Results = self._model(frame,stream=True)
        bbxarr: np.ndarray = model_results[0].boxes.data #Numpy array containing bounding boxes
        results: List[ObjDetectResult] = []
        for bbx in bbxarr:
            left,top = bbx[0],bbx[1]
            right,bottom = bbx[2],bbx[3]
            confidence = bbx[4]
            obj_class = bbx[5]
            corner_pixels = np.array(
                [left,bottom],
                [right,bottom],
                [right,top],
                [left,top]
            )
            corner_angles = np.zeros(shape=(4,2))
            norm_corners = cv2.undistortPoints(corner_pixels,self._camConf.camera_matrix,self._camConf.dist_coeffs)
            for index,corner in enumerate(norm_corners):
                corner_angles[index][0] = math.atan(corner[0][0])
                corner_angles[index][1] = math.atan(corner[0][1])
            results.append(ObjDetectResult(obj_class,confidence,corner_angles,corner_pixels))
        return results
            
                
