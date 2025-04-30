import tomllib
from configuration.config_types import *

class FileConfigurator:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_file, 'rb') as f:
            return tomllib.load(f)

    def get_config(self, key: str):
        return self.config.get(key, None)
    
    def get_dev_config(self):
        devDict: dict = self.config.get("device")
        return DeviceConfig(
            devDict.get("name"),
            devDict.get("dev_ip"),
            devDict.get("server_ip")
        )
    
    def dump(self):
        return self.config