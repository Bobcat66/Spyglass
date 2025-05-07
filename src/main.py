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
    devconfig = config.get_dev_config()

    # Initialize NetworkTables
    inst: ntcore.NetworkTableInstance = ntcore.NetworkTableInstance.getDefault()
    inst.startServer(devconfig.server_ip)
    inst.startClient4(devconfig.name)
    ntmanager.initialize(devconfig.name,inst)





    
