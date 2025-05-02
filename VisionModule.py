import cscore
from pipeline.Pipeline import Pipeline
from network.ntmanager import NTManager
from configuration.config_types import *
import cv2

#This class handles everything related to the camera, from capturing video to processing to output
#TODO: Refactor this to use configurators, add option to disable streaming
#TODO Later: Add option to turn on and off stream while the program is running
class VisionWorker:
    def __init__(self, camConf: CameraConfig, pipConf: PipelineConfig, grayscale: bool, camera: cscore.VideoCamera, pipeline: Pipeline, ntman: NTManager, rawport: int, processedport: int):
        self._camera = camera
        self._camConf = camConf
        self._pipConf = pipConf
        pixelFormat = cscore.VideoMode.PixelFormat.kGray if grayscale else cscore.VideoMode.PixelFormat.kBGR
        formatted = self._camera.setPixelFormat(pixelFormat)
        if not formatted:
            raise ValueError("{pipeline.name}: Could not format camera")
        self._input = cscore.CvSink(pipeline.name + "_input",pixelFormat)
        self._output = cscore.CvSource(pipeline.name + "_output",pixelFormat=cscore.VideoMode.PixelFormat.kBGR)
        self._pipeline = pipeline
        self._ntman = ntman
        self._rawserver = cscore.MjpegServer(f"{self._pipeline.name}_raw", rawport)
        self._processedserver = cscore.MjpegServer(f"{self._pipeline.name}_processed", processedport)
        self._rawserver.setSource(self._camera)
        self._processedserver.setSource(self._output)
    
    def run(self) -> None:
        """
        Run the pipeline.
        """
        frame: cv2.Mat = np.zeros(shape=(self._camConf.yres,self._camConf.xres,1 if self._pipConf.grayscale else 3),dtype=np.uint8)
        while True:
            time, frame = self._input.grabFrame(frame)
            res = self._pipeline.process(frame)
            self._ntman.publishNTagPoseResult(time,res)
            self._output.putFrame(res.frame)
    #TODO: Add thread management
