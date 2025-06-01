# MIT License
#
# Copyright (c) 2025 FRC 1076 PiHi Samurai
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
    


    
