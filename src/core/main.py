from configuration import configsources
from network import ntmanager
import ntcore
import logging
from utils import rootsrv_client as rootsrv
import os
from dotenv import load_dotenv

#
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Use DEBUG for more verbose logs #TODO: Configure this with environment variables
    format='[%(levelname)s] %(name)s: %(message)s' # stdout is being logged by journald, which already keeps timestamps
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":

    print(os.getcwd())

    rootsrv.initialize(os.getenv("ROOTSRV_SOCK"))

    logger.info("Launching SamuraiSight")

    config = configsources.ConfigParser("config.toml")
    #devconfig = config.get_dev_config()

    # Initialize NetworkTables (FOR TESTING)
    inst: ntcore.NetworkTableInstance = ntcore.NetworkTableInstance.getDefault()
    inst.startServer("10.10.76.2")
    inst.startClient4("SamuraiSight")
    ntmanager.initialize("SamuraiSight",inst)
    rootsrv.dynamicIP()
    






    
