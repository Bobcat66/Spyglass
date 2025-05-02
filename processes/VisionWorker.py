import cscore
import threading
from pipeline import Pipeline
from network.ntmanager import NTManager
from configuration.config_types import *
import cv2
from time import perf_counter_ns

#This class handles everything related to the camera, from capturing video to processing to output
#TODO: Refactor this to use configurators, add option to disable streaming
#TODO Later: Add option to turn on and off stream while the program is running
class VisionWorker:
    def __init__(self, fieldConf: FieldConfig, camConf: CameraConfig, pipConf: PipelineConfig):
        self._camera = cscore.UsbCamera(camConf.name,camConf.device_number)
        self._fldConf = fieldConf
        self._camConf = camConf
        self._pipConf = pipConf
        self._grayscale = pipConf.grayscale
        self._stream = pipConf.stream
        pixelFormat = cscore.VideoMode.PixelFormat.kGray if self._grayscale else cscore.VideoMode.PixelFormat.kBGR
        successfulCamConfig = self._camera.setVideoMode(cscore.VideoMode(pixelFormat_=pixelFormat,width_=camConf.xres,height_=camConf.yres,fps_=camConf.fps))
        if not successfulCamConfig:
            print(f"SamuraiSight: Unable to configure camera {camConf.name}")
            successfulPixelFormat = self._camera.setPixelFormat(pixelFormat)
            if not successfulPixelFormat:
                print(f"SamuraiSight: Unable to configure camera {camConf.name} pixel format")
        self._pipeline = Pipeline.buildPipeline(pipConf,camConf,fieldConf)
        self._input = cscore.CvSink(self._pipeline.name + "_input",pixelFormat)
        self._input.setSource(self._camera)
        self._output = cscore.CvSource(self._pipeline.name + "_output",cscore.VideoMode.PixelFormat.kBGR,camConf.xres,camConf.yres,camConf.fps)
        self._ntman = NTManager(pipConf.name)
        if self._stream:
            self._rawserver = cscore.MjpegServer(f"{self._pipeline.name}_raw", pipConf.rawport)
            self._processedserver = cscore.MjpegServer(f"{self._pipeline.name}_processed", pipConf.processedport)
            self._rawserver.setSource(self._camera)
            self._processedserver.setSource(self._output)
        self._running: bool = False # Simple variable assignments are atomic by default in python
        self._thread = threading.Thread(target=self.run,name=f"{pipConf.name}_worker",daemon=True)
    
    def run(self) -> None:
        """
        Run the pipeline.
        """
        frame: cv2.Mat = np.zeros(shape=(self._camConf.yres,self._camConf.xres,1 if self._pipConf.grayscale else 3),dtype=np.uint8)
        while self._running:
            #TODO: see if time needs to be latency compensated
            time, frame = self._input.grabFrame(frame)
            if time == 0: print(self._input.getError())
            res = self._pipeline.process(frame)
            self._ntman.publishApriltagPoseResult(time,res.nTagPoseResult,res.tagDistResults)
            if res.frame is not None: self._output.putFrame(res.frame)
    
    def start(self) -> None:
        self._running = True
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        self._thread.join()
    
    def startOnMainThread(self) -> None:
        #Starts the worker on the main thread, for testing. DO NOT USE, WILL BLOCK MAIN THREAD INDEFINITELY
        self._running = True
        self.run()
