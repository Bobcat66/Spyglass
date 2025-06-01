# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

echo "Uninstalling Spyglass..."

SERVICE_NAME="spyglass.service"
SERVICE_FILE="/etc/systemd/system/spyglass.service"
ROOTSRV_FILE="/etc/systemd/system/spg-rootsrv.service"
ROOT_DIR="/opt/Spyglass"

if ! [ -d $ROOT_DIR ]; then
    echo "Spyglass is not installed"
    exit 0
fi

USER="spyglass-srv"
GROUP="spyglass"
systemctl stop spyglass
systemctl disable spyglass
echo "Disabled Spyglass service"
systemctl stop spg-rootsrv
systemctl disable spg-rootsrv
echo "Disabled Spyglass Root Service"
userdel $USER
groupdel $GROUP
rm $SERVICE_FILE
rm $ROOTSRV_FILE
rm -r $ROOT_DIR
echo "Deleted program files"
NETWORK_FILE="/etc/systemd/network/10-spyglass-eth0.network"
if [ -f $NETWORK_FILE ]; then
    rm $NETWORK_FILE
    echo "Deleted network files"
fi






