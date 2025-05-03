import cscore
import threading
from pipeline import Pipeline
from network.ntmanager import NTManager
from configuration.config_types import *
from cscore import CameraServer
import cv2
from time import perf_counter
import logging

logger = logging.getLogger(__name__)
#This class handles everything related to the camera, from capturing video to processing to output
#TODO: Refactor this to use configurators, add option to disable streaming
#TODO Later: Add option to turn on and off stream while the program is running
class VisionWorker:
    def __init__(self, fieldConf: FieldConfig, camConf: CameraConfig, pipConf: PipelineConfig):
        self._camera = CameraServer.startAutomaticCapture(camConf.device_number)
        logger.info(f"Acquired camera {camConf.device_number} ({camConf.name})")
        self._fldConf = fieldConf
        self._camConf = camConf
        self._pipConf = pipConf
        self._grayscale = pipConf.grayscale
        self._stream = pipConf.stream
        #pixelFormat = cscore.VideoMode.PixelFormat.kGray if self._grayscale else cscore.VideoMode.PixelFormat.kBGR
        videoMode = cscore.VideoMode(pixelFormat_=camConf.pixel_format,width_=camConf.xres,height_=camConf.yres,fps_=camConf.fps)
        setVideoMode = self._camera.setVideoMode(videoMode)
        if not setVideoMode:
            logger.warning(f"Unable to configure camera {camConf.name}")
        outputVideoMode = cscore.VideoMode(pixelFormat_=cscore.VideoMode.PixelFormat.kBGR,width_=camConf.xres,height_=camConf.yres,fps_=camConf.fps)
        self._pipeline = Pipeline.buildPipeline(pipConf,camConf,fieldConf)
        self._input = CameraServer.getVideo(self._camera)
        self._output = cscore.CvSource(self._pipeline.name + "_output",outputVideoMode)
        self._ntman = NTManager(pipConf.name)
        if self._stream:
            self._rawserver = cscore.MjpegServer(f"{self._pipeline.name}_raw", pipConf.rawport)
            self._processedserver = cscore.MjpegServer(f"{self._pipeline.name}_processed", pipConf.processedport)
            self._rawserver.setSource(self._camera)
            self._processedserver.setSource(self._output)
        self._running: bool = False # Simple variable assignments are atomic by default in python
        self._thread = threading.Thread(target=self.run,name=f"{pipConf.name}_worker",daemon=True)
    
    #TODO: Figure out how to speed up frame grabbing. This is a serious source of latency right now
    #Maybe the raw stream is screwing things up? Test
    def run(self) -> None:
        """
        Run the pipeline.
        """
        frame: cv2.Mat = np.zeros(shape=(240,320,1),dtype=np.uint8)
        lastFPSTimestamp = perf_counter()
        frameCounter = 0
        while self._running:
            #There is performance characterization code, remove it when finished
            #starttime = perf_counter()
            #t0 = perf_counter()
            time, frame = self._input.grabFrame(frame)
            #t1 = perf_counter()
            #print("grab frame time: " + str((t1-t0)*1000) + " ms")
            
            if time == 0: 
                print(self._input.getError())
            else:
                if self._grayscale: frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            #t0 = perf_counter()
            res = self._pipeline.process(frame)
            #t1 = perf_counter()
            #print("pipeline time: " + str((t1-t0)*1000) + " ms")
            self._ntman.publishApriltagPoseResult(time,res.nTagPoseResult,res.tagDistResults)
            if res.frame is not None: self._output.putFrame(res.frame)
            frameCounter += 1
            #endtime = perf_counter()
            #print("total time: " + str((endtime - starttime)*1000) + " ms")
            #Measure FPS
            if perf_counter() - lastFPSTimestamp >= 1.0:
                logger.info(f"{self._pipConf.name} running at {frameCounter} fps")
                self._ntman.publishApriltagFPS(frameCounter,time)
                frameCounter = 0
                lastFPSTimestamp = perf_counter()
                


    
    def start(self) -> None:
        logger.info(f"Started {self._pipConf.name} worker")
        self._running = True
        self._thread.start()

    def stop(self) -> None:
        logger.info(f"Stopped {self._pipConf.name} worker")
        self._running = False
        self._thread.join()
    
    def startOnMainThread(self) -> None:
        #Starts the worker on the main thread, for testing. DO NOT USE, WILL BLOCK MAIN THREAD INDEFINITELY
        self._running = True
        self.run()
