echo "Uninstalling SamuraiSight"

SERVICE_NAME="samuraisight.service"
SERVICE_FILE="/etc/systemd/system/samuraisight.service"

if [ ! -f $SERVICE_FILE ]; then
    echo "SamuraiSight is not installed"
    exit 0
fi

ROOT_DIR=$(grep -E '^WorkingDirectory=' $SERVICE_FILE | cut -d= -f2)
USER=$(grep -E '^User=' $SERVICE_FILE | cut -d= -f2)
systemctl stop $SERVICE_NAME
systemctl disable $SERVICE_NAME
userdel $USER
rm $SERVICE_FILE
rm -r $ROOT_DIR





