from configuration import configsources

if __name__ == "__main__":
    configurator = configsources.ConfigParser("deploy/config.toml")
    print(configurator.dump())