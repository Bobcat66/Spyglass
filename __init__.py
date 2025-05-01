from configuration import configsources
from network import ntmanager
import pipeline
import network
import utils
import argparse
import ntcore

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SamuraiSight")
    parser.add_argument("--config", type=str, help="Path to the configuration file",default="config.toml")
    args = parser.parse_args()

    config = configsources.ConfigParser(args.config)
    devconfig = config.get_dev_config()

    # Initialize NetworkTables
    inst: ntcore.NetworkTableInstance = ntcore.NetworkTableInstance.getDefault()
    inst.startServer(devconfig.server_ip)
    inst.startClient4(devconfig.name)
    ntmanager.initialize(devconfig.name,inst)





    
