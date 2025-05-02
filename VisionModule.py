import cscore
import threading
from pipeline import Pipeline
from network.ntmanager import NTManager
from configuration.config_types import *
import cv2

#This class handles everything related to the camera, from capturing video to processing to output
#TODO: Refactor this to use configurators, add option to disable streaming
#TODO Later: Add option to turn on and off stream while the program is running
class VisionWorker:
    def __init__(self, fieldConf: FieldConfig, camConf: CameraConfig, pipConf: PipelineConfig, camera: cscore.VideoCamera, rawport: Union[int,None], processedport: Union[int,None]):
        self._camera = camera
        self._fldConf = fieldConf
        self._camConf = camConf
        self._pipConf = pipConf
        self._grayscale = pipConf.grayscale
        self._stream = pipConf.stream
        pixelFormat = cscore.VideoMode.PixelFormat.kGray if self._grayscale else cscore.VideoMode.PixelFormat.kBGR
        formatted = self._camera.setPixelFormat(pixelFormat)
        if not formatted:
            raise ValueError(f"{pipConf.name}: Could not format camera {camConf.name}")
        self._pipeline = Pipeline.buildPipeline(pipConf,camConf,fieldConf)
        self._input = cscore.CvSink(self._pipeline.name + "_input",pixelFormat)
        self._output = cscore.CvSource(self._pipeline.name + "_output",pixelFormat=cscore.VideoMode.PixelFormat.kBGR)
        self._ntman = NTManager(pipConf.name)
        if self._stream:
            self._rawserver = cscore.MjpegServer(f"{self._pipeline.name}_raw", rawport)
            self._processedserver = cscore.MjpegServer(f"{self._pipeline.name}_processed", processedport)
            self._rawserver.setSource(self._camera)
            self._processedserver.setSource(self._output)
        self._thread = threading.Thread(target=self.run(),name=f"{pipConf.name}_worker",daemon=True)
        self._running: bool = False # Simple variable assignments are atomic by default in python
    
    def run(self) -> None:
        """
        Run the pipeline.
        """
        frame: cv2.Mat = np.zeros(shape=(self._camConf.yres,self._camConf.xres,1 if self._pipConf.grayscale else 3),dtype=np.uint8)
        while self._running:
            #TODO: see if time needs to be latency compensated
            time, frame = self._input.grabFrame(frame)
            res = self._pipeline.process(frame)
            self._ntman.publishApriltagPoseResult(time,res)
            if res.frame is not None: self._output.putFrame(res.frame)
    #TODO: Add thread management

    def start(self):
        self._running = True
        self._thread.start()

    def stop(self):
        self._running = False
        self._thread.join()
