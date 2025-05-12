# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

echo "Uninstalling SamuraiSight"

SERVICE_NAME="smsight.service"
SERVICE_FILE="/etc/systemd/system/smsight.service"
ROOTSRV_FILE="/etc/systemd/system/sms-rootsrv.service"
ROOT_DIR="/opt/SamuraiSight"

if ! [ -d $ROOT_DIR ]; then
    echo "SamuraiSight is not installed"
    exit 0
fi

USER="smsight-srv"
GROUP="smsight"
systemctl stop smsight
systemctl disable smsight
systemctl stop sms-rootsrv
systemctl disable sms-rootsrv
userdel $USER
groupdel $GROUP
rm $SERVICE_FILE
rm $ROOTSRV_FILE
rm -r $ROOT_DIR
NETWORK_FILE="/etc/systemd/network/10-smsight-eth0.network"
if [ -f $NETWORK_FILE ]; then
    rm $NETWORK_FILE
fi






