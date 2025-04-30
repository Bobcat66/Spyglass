from configuration import configurator
from network import ntmanager
import argparse
import ntcore

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SamuraiSight")
    parser.add_argument("--config", type=str, help="Path to the configuration file",default="config.toml")
    args = parser.parse_args()

    config = configurator.Configurator(args.config)
    devconfig = config.get_dev_config()

    # Initialize NetworkTables
    inst: ntcore.NetworkTableInstance = ntcore.NetworkTablesInstance.getDefault()
    inst.startServer(devconfig.server_ip)
    inst.startClient4(devconfig.name)
    ntmanager.initialize(devconfig.name,inst)





    
