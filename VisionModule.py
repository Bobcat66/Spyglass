import cscore
from pipeline.Pipeline import Pipeline
from network.ntmanager import NTManager

#This class handles everything related to the camera, from capturing video to processing to output
class VisionWorker:
    def __init__(self, source: cscore.VideoSource, pipeline: Pipeline, ntman: NTManager, rawport: int, processedport: int):
        self._source = source
        self._pipeline = pipeline
        self._ntman = ntman
        self._rawserver = cscore.MjpegServer(f"{self._pipeline.name}_raw", rawport)
        self._processedserver = cscore.MjpegServer(f"{self._pipeline.name}_processed", processedport)
        self._rawserver.setSource(self._source)
        pipeline.addSink(self._processedserver)
    
    def run(self) -> None:
        """
        Run the pipeline.
        """
        self._pipeline.run()
    #TODO: Add thread management
