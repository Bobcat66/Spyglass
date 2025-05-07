#!/usr/bin/env bash

echo "Uninstalling SamuraiSight"

SERVICE_NAME="samuraisight.service"
SERVICE_FILE="/etc/systemd/system/samuraisight.service"

if [ ! -f $SERVICE_FILE ]; then
    echo "SamuraiSight is not installed"
    exit 0
fi

ROOT_DIR=$(grep -E '^WorkingDirectory=' $SERVICE_FILE | cut -d= -f2)
sudo systemctl stop $SERVICE_NAME
sudo systemctl disable $SERVICE_NAME
sudo rm $SERVICE_FILE
sudo rm -r $ROOT_DIR





