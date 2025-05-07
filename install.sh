#!/usr/bin/env bash

echo -e "SamuraiSight Installer\n"

ROOT_DIR = "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCH_SCRIPT = "smsght"
LAUNCH_PATH = "$ROOT_DIR/bin/$LAUNCH_SCRIPT"

#Check if samuraisight is already installed
if command -v $LAUNCH_SCRIPT &>/dev/null; then
    echo -e "$LAUNCH_SCRIPT is already in PATH"
    echo "SamuraiSight is already installed"
    echo "Aborting installation"
    exit 1 # 1 denotes that samuraisight is already installed

#Make smsght.sh (the launch script) an executable and add it to the PATH

chmod +x $LAUNCH_PATH


echo "Do you want SamuraiSight to launch on boot? [Y/N]: "
read launchOnBoot
if [ "$launchOnBoot" == "Y" ]; then











