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
systemctl stop smsight
systemctl disable smsight
systemctl stop sms-rootsrv
systemctl disable sms-rootsrv
userdel $USER
rm $SERVICE_FILE
rm $ROOTSRV_FILE
rm -r $ROOT_DIR
NETWORK_FILE="/etc/systemd/network/10-smsight-eth0.network"
if [ -f $NETWORK_FILE ]; then
    rm $NETWORK_FILE
fi






