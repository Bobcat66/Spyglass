echo "Uninstalling SamuraiSight"

SERVICE_NAME="smsight.service"
SERVICE_FILE="/etc/systemd/system/smsight.service"
ROOT_DIR="/opt/SamuraiSight"

if [ ! -d $ROOT_DIR ]; then
    echo "SamuraiSight is not installed"
    exit 0
fi

USER="smsight-srv"
systemctl stop $SERVICE_NAME
systemctl disable $SERVICE_NAME
userdel $USER
rm $SERVICE_FILE
rm -r $ROOT_DIR





