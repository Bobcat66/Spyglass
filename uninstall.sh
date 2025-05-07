#!/usr/bin/env bash

echo "Uninstalling SamuraiSight"

if [ ! -f "/etc/systemd/system/samuraisight.service" ]; then
    echo "SamuraiSight is not installed"
    exit 0
fi


