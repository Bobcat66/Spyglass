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

from configuration import configsources
from network import ntmanager
import ntcore
import logging
from video import CameraManager
from pipeline import PipelineManager
from utils.misc import releaseGIL

from processes import rootsrv_client as rootsrv
import os
from dotenv import load_dotenv


load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") == "true" else logging.INFO, 
    format='[%(levelname)s] %(threadName)s(%(name)s): %(message)s' # stdout is being logged by journald, which already keeps timestamps
)

logger = logging.getLogger(__name__)


if __name__ == "__main__":

    logger.info("Launching Spyglass")

    
    inst: ntcore.NetworkTableInstance = ntcore.NetworkTableInstance.getDefault()
    inst.startServer(os.getenv("ROBORIO"))
    inst.startClient4(os.getenv("DEV_NAME"))
    ntmanager.initialize(os.getenv("DEV_NAME"),inst)
    rootsrv.initialize(os.getenv("ROOTSRV_SOCK"))

    configurator = configsources.ConfigParser("config.toml")

    configurator.loadFieldConfig()

    CameraManager.loadCameras(configurator.getCameraConfigs())
    PipelineManager.loadPipelines(configurator.getPipelineConfigs())
    PipelineManager.startAll()

    while True:
        #TODO: Manage webclient/NT client here
        releaseGIL()

    
    
    


    

    
    
    






    
