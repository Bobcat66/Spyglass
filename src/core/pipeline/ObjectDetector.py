# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

import ultralytics
from typing import List
import cv2
import ultralytics.engine.results
from utils.vtypes import ObjDetectResult
from configuration.config_types import CameraIntrinsics
from typing import Dict, Tuple
import numpy as np
import math

class ObjectDetector:

    def __init__(self, model_path: str, intrinsics: CameraIntrinsics):
        """
        Initialize the ObjectDetector with a YOLO model.

        :param model_path: Path to the YOLO model file.
        """
        # This class is designed to help compute a 3 DoF pose estimate of an arbitrary object
        # Using camera intrinsics, we normalize the corners of the points, which we can then use to calculate rays from the camera to the corners of the bounding box
        # Using these rays (as well as the camera's extrinsic properties), we can work out a rough estimate 3 DoF pose of the object with 
        # the pythagorean theorem (Assuming the object is on the ground)
        self._model = ultralytics.YOLO(model_path,'detect')
        self._intrinsics = intrinsics

    def detect(self, frame: cv2.Mat) -> List[ObjDetectResult]:
        model_result: ultralytics.engine.results.Results = self._model.predict(frame,verbose=False)[0]
        bbxarr: np.ndarray = model_result.boxes.data #Numpy array containing bounding boxes
        area: Tuple[int,int] = model_result.orig_shape
        results: List[ObjDetectResult] = []
        for bbx in bbxarr:
            left,top = bbx[0],bbx[1]
            right,bottom = bbx[2],bbx[3]
            confidence = bbx[4]
            obj_class = bbx[5]
            corner_pixels = np.array(
                [
                    [left,bottom],
                    [right,bottom],
                    [right,top],
                    [left,top]
                ]
            )
            percent_area: float = (abs(left-right)*abs(top-bottom))/(area[0]*area[1])
            corner_angles: np.typing.NDArray[np.float64] = np.zeros(shape=(4,2))
            norm_corners = cv2.undistortPoints(corner_pixels,self._intrinsics.matrix,self._intrinsics.dist_coeffs)
            for index,corner in enumerate(norm_corners):
                corner_angles[index][0] = math.atan(corner[0][0])
                corner_angles[index][1] = math.atan(corner[0][1])
            results.append(ObjDetectResult(int(obj_class),confidence,percent_area,corner_angles,corner_pixels))
        return results
    
    def getClassNames(self) -> Dict[int,str]:
        return self._model.names
            
                
