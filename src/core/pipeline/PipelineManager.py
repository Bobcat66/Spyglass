from processes.PipelineWorker import PipelineWorker, buildPipelineWorker
import logging
from typing import List
from configuration.config_types import PipelineConfig

logger = logging.getLogger(__name__)

_pipelines: dict[str,PipelineWorker] = {}
_activePipelines: set[str] = set()

def loadPipelines(pipelineConfigs: List[PipelineConfig]) -> None:
    for config in pipelineConfigs:
        if config.name in _pipelines.keys():
            logger.warning("Two pipelines named %s detected",config.name)
            continue
        logger.debug("Loading pipeline %s",config.name)
        worker = buildPipelineWorker(config)
        _pipelines[config.name] = worker

def startPipeline(pipename: str) -> None:
    worker = _pipelines.get(pipename)
    if worker is None:
        logger.warning("No pipeline named %s detected",pipename)
        return
    if pipename in _activePipelines:
        logger.debug("Pipeline %s already started",pipename)
        return
    worker.start()
    _activePipelines.add(pipename)

def stopPipeline(pipename: str) -> None:
    if pipename not in _activePipelines:
        logger.debug("Pipeline %s already stopped",pipename)
        return
    worker = _pipelines.get(pipename)
    if worker is None:
        logger.warning("No pipeline named %s detected",pipename)
        return
    worker.stop()
    _activePipelines.remove(pipename)

def startAll() -> None:
    for name in _pipelines.keys():
        startPipeline(name)

def stopAll() -> None:
    for name in _activePipelines:
        stopPipeline(name)
    


    
