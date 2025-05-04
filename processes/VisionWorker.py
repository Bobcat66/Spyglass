# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

import cscore
import threading
from pipeline import Pipeline
from network.ntmanager import NTManager
from configuration.config_types import *
from cscore import CameraServer
import cv2
from time import perf_counter_ns
import logging

logger = logging.getLogger(__name__)
#This class handles everything related to the camera, from capturing video to processing to output
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
    
    def run(self) -> None:
        """
        Run the pipeline.
        """
        frame: cv2.Mat = np.zeros(shape=(self._camConf.xres,self._camConf.yres,1),dtype=np.uint8)
        nanosSinceLastFPS = perf_counter_ns()
        frameCounter = 0
        while self._running:

            time, frame = self._input.grabFrame(frame)

            if time == 0: 
                logger.warning(self._input.getError())
            else:
                if self._grayscale: frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            
            res = self._pipeline.process(frame)
            self._ntman.publishResult(time,res)
            if res.frame is not None: self._output.putFrame(res.frame)
            frameCounter += 1
            #Measure FPS
            if perf_counter_ns() - nanosSinceLastFPS >= 1e9:
                logger.info(f"{self._pipConf.name} running at {frameCounter} fps")
                self._ntman.publishFPS(frameCounter,time)
                frameCounter = 0
                nanosSinceLastFPS = perf_counter_ns()
    
    def start(self) -> None:
        self._running = True
        self._thread.start()
        logger.info(f"Started {self._pipConf.name} worker")

    def stop(self) -> None:
        self._running = False
        self._thread.join()
        logger.info(f"Stopped {self._pipConf.name} worker")
    
    def startOnMainThread(self) -> None:
        #Starts the worker on the main thread, for testing. DO NOT USE, WILL BLOCK MAIN THREAD INDEFINITELY
        self._running = True
        self.run()
