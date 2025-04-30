from configuration import configsources

if __name__ == "__main__":
    configurator = configsources.FileConfigurator("config.toml")
    print(configurator.dump())