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
from typing import List,Tuple
import traceback
import sys

logger = logging.getLogger(__name__)
#This class handles everything related to the camera, from capturing video to processing to output
#TODO Later: Add option to turn on and off stream while the program is running
#TODO: Refactor pixel format handling, cut out redundant opencv calls
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

        #Thread
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

            res = None
            try:
                res = self._pipeline.process(frame)
            except Exception as e:
                logger.warning(f"{self._pipConf.name} unable to process frame due to an unhandled exception.")
                traceback.print_exc()
                continue

            self._ntman.publishResult(time,res)
            if res.frame is not None: self._output.putFrame(res.frame)

            #Measure FPS
            frameCounter += 1
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

    def benchmark(self,benchtime: float) -> None:
        logger.info(f"Benchmarking {self._pipConf.name} for {benchtime} seconds")
        frame: cv2.Mat = np.zeros(shape=(self._camConf.xres,self._camConf.yres,1),dtype=np.uint8)
        benchdata: List[Tuple[int,int,int,int,List[int]]] = [] #total cycle time,capture time,process time,publish time,deep benchmark data
        
        t0 = perf_counter_ns()
        while perf_counter_ns() - t0 < (benchtime * 1e9):

            cyc_t0 = perf_counter_ns()
            cap_t0 = perf_counter_ns()
            time, frame = self._input.grabFrame(frame)
            if time == 0: 
                logger.warning(self._input.getError())
            else:
                if self._grayscale: frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            cap_t1 = perf_counter_ns()


            dbench,res = None,None
            prc_t0 = perf_counter_ns()
            try:
                dbench,res = self._pipeline.deepBenchmark(frame)
            except:
                logger.warning(f"{self._pipConf.name} unable to process frame due to an unhandled exception.")
                traceback.print_exc()
                continue
            prc_t1 = perf_counter_ns()

            pub_t0 = perf_counter_ns()
            self._ntman.publishResult(time,res)
            if res.frame is not None: self._output.putFrame(res.frame)
            pub_t1 = perf_counter_ns()
            cyc_t1 = perf_counter_ns()
            benchdata.append((cyc_t1-cyc_t0,cap_t1-cap_t0,prc_t1-prc_t0,pub_t1-pub_t0,dbench))
        
        dbench_len = len(benchdata[0][4])
        cycles_measured = len(benchdata)
        dbench_period_averages: List[float] = [0.0] * (dbench_len-1) #data is in milliseconds
        dbench_period_maxima: List[float] = [0.0] * (dbench_len-1) #data is in milliseconds
        dbench_period_minima: List[float] = [sys.float_info.max] * (dbench_len-1) #data is in milliseconds

        cycle_avg = 0.0
        cycle_max = 0.0
        cycle_min = sys.float_info.max

        capture_avg = 0.0
        capture_max = 0.0
        capture_min = sys.float_info.max

        process_avg = 0.0
        process_max = 0.0
        process_min = sys.float_info.max

        publish_avg = 0.0
        publish_max = 0.0
        publish_min = sys.float_info.max

        for bdat in benchdata:
            dbdat = bdat[4]

            cycle = bdat[0]/1e6
            capture = bdat[1]/1e6
            process = bdat[2]/1e6
            publish = bdat[3]/1e6

            cycle_avg += cycle/cycles_measured
            if cycle > cycle_max:
                cycle_max = cycle
            if cycle < cycle_min:
                cycle_min = cycle

            capture_avg += capture/cycles_measured
            if capture > capture_max:
                capture_max = capture
            if capture < capture_min:
                capture_min = capture

            process_avg += process/cycles_measured
            if process > process_max:
                process_max = process
            if process < process_min:
                process_min = process
            
            publish_avg += publish/cycles_measured
            if publish > publish_max:
                publish_max = publish
            if publish < publish_min:
                publish_min = publish

            for i in range(1,dbench_len):
                period_ms = (dbdat[i]-dbdat[i-1])/1e6 
                dbench_period_averages[i-1] += period_ms/cycles_measured
                if period_ms > dbench_period_maxima[i-1]:
                    dbench_period_maxima[i-1] = period_ms
                if period_ms < dbench_period_minima[i-1]:
                    dbench_period_minima[i-1] = period_ms
            
        benchreport = f"""
{self._pipConf.name} BENCHMARK REPORT
-----------------------------------------
Time: {benchtime} s
Cycles Measured: {cycles_measured}
Avg cycle time: {cycle_avg:.3f} ms
Max cycle time: {cycle_max:.3f} ms
Min cycle time: {cycle_min:.3f} ms
-----------------CAPTURE-----------------
Avg capture time: {capture_avg:.3f} ms
Max capture time: {capture_max:.3f} ms
Min capture time: {capture_min:.3f} ms
-----------------PROCESS-----------------
Avg process time: {process_avg:.3f} ms
Max process time: {process_max:.3f} ms
Min process time: {process_min:.3f} ms
-----------------PUBLISH-----------------
Avg publish time: {publish_avg:.3f} ms
Max publish time: {publish_max:.3f} ms
Min publish time: {publish_min:.3f} ms
-----------------DPBENCH-----------------
PRD |    AVG    |    MAX    |    MIN    |"""
        for i in range(dbench_len-1):
            benchreport += f"\n{i: 3} | {dbench_period_averages[i]: 9.3f} | {dbench_period_maxima[i]: 9.3f} | {dbench_period_minima[i]: 9.3f} |"
        logger.info(benchreport)







