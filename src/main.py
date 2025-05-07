from configuration import configsources
from network import ntmanager
import ntcore
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Use DEBUG for more verbose logs #TODO: Configure this with system.toml
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":

    logger.info("Launching SamuraiSight")

    config = configsources.ConfigParser("../config.toml")
    #devconfig = config.get_dev_config()

    # Initialize NetworkTables (FOR TESTING)
    inst: ntcore.NetworkTableInstance = ntcore.NetworkTableInstance.getDefault()
    inst.startServer("10.10.76.2")
    inst.startClient4("SamuraiSight")
    ntmanager.initialize("SamuraiSight",inst)
    while True:
        pass





    
