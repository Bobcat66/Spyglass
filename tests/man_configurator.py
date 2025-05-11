import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../src/core')))

from configuration import configsources

if __name__ == "__main__":
    configurator = configsources.ConfigParser("config.toml")
    print(configurator.dump())