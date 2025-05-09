
import cv2
from utils.vtypes import Fiducial, SingleTagPoseResult, ObjDetectResult
from typing import List, Union
from configuration.config_types import *

class Annotator:
    def __init__(self,camConf: CameraConfig, fieldConf: FieldConfig, pipeConf: PipelineConfig):
        self._cameraConfig = camConf
        self._fieldConfig = fieldConf
        self._pipeConfig = pipeConf

    def drawSingleTagPose(self,image: cv2.Mat,result: SingleTagPoseResult):
        if result.error_0 > result.error_1:
            cv2.drawFrameAxes(
                image,
                self._cameraConfig.camera_matrix,
                self._cameraConfig.dist_coeffs,
                result.rvecs_0,
                result.tvecs_0,
                self._fieldConfig.tag_size/2
            )
        else:
            cv2.drawFrameAxes(
                image,
                self._cameraConfig.camera_matrix,
                self._cameraConfig.dist_coeffs,
                result.rvecs_1,
                result.tvecs_1,
                self._fieldConfig.tag_size/2
            )
    
    def drawFiducials(self, image: cv2.Mat,fiducials: List[Fiducial]):
        for f in fiducials:
            color = (0,0,255) if f.id in self._pipeConfig.apriltagConfig.excludeTagsPNP else (0,255,0) #Draws Multitag rejected tags in red, not green
            bottom_left = tuple(f.corners[0].astype(int))
            bottom_right = tuple(f.corners[1].astype(int))
            top_right = tuple(f.corners[2].astype(int))
            top_left = tuple(f.corners[3].astype(int))
            cv2.line(image, bottom_left, bottom_right, color, 2)
            cv2.line(image, bottom_right, top_right, color, 2)
            cv2.line(image, top_right, top_left, color, 2)
            cv2.line(image, top_left, bottom_left, color, 2)
            cv2.putText(image, str(f.id), (top_left[0],top_left[1]-15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    def drawObjDetectResults(
        image: cv2.Mat,
        results: List[ObjDetectResult],
        class_names: Union[Dict[int,str],None] = None
    ) -> None:
        for result in results:
            bottom_left = tuple(result.corner_pixels[0].astype(int))
            bottom_right = tuple(result.corner_pixels[1].astype(int))
            top_right = tuple(result.corner_pixels[2].astype(int))
            top_left = tuple(result.corner_pixels[3].astype(int))
            cv2.line(image, bottom_left, bottom_right, (0, 0, 255), 2)
            cv2.line(image, bottom_right, top_right, (0, 0, 255), 2)
            cv2.line(image, top_right, top_left, (0, 0, 255), 2)
            cv2.line(image, top_left, bottom_left, (0, 0, 255), 2)
            labelText = f"{class_names.get(result.obj_class,f"Object Class {result.obj_class}") if class_names is not None else "Object Class " + str(result.obj_class)} ({result.confidence:.3f})"
            cv2.putText(
                image, 
                labelText, 
                (top_left[0],top_left[1]-7), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, 
                (255, 0, 0), 
                2
            )

