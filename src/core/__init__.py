from configuration import configsources
from network import ntmanager
import ntcore
import logging

from processes import rootsrv_client as rootsrv
import os
from dotenv import load_dotenv

#
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") == "true" else logging.INFO, 
    format='[%(levelname)s] %(threadName)s(%(name)s): %(message)s' # stdout is being logged by journald, which already keeps timestamps
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    rootsrv.initialize(os.getenv("ROOTSRV_SOCK"))

    logger.info("Launching SamuraiSight")

    config = configsources.ConfigParser("config.toml")
    #devconfig = config.get_dev_config()

    inst: ntcore.NetworkTableInstance = ntcore.NetworkTableInstance.getDefault()
    inst.startServer(os.getenv("ROBORIO"))
    inst.startClient4(os.getenv("DEV_NAME"))
    ntmanager.initialize(os.getenv("DEV_NAME"),inst)

    
    
    






    
