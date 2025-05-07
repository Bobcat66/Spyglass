ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME=samuraisight
LAUNCH_PATH="$ROOT_DIR/bin/$SERVICE_NAME"
USER=$(whoami)
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
echo -e "------------- SamuraiSight Installer -------------\n"

# Check if samuraisight is already installed
if [ -f $SERVICE_FILE ]; then
    echo "SamuraiSight is already installed"
    echo "Aborting installation"
    exit 1 # 1 denotes that samuraisight is already installed
fi

read -p "Enter team number: " TEAM_NUMBER

# Create .env file
ENV_FILE=".env"
cat > $ENV_FILE <<EOF
# Environment Configuration (Only edit this file if you know what you are doing)
APP_ENV=production
DEBUG=false
ROOT_DIR=$ROOT_DIR
USER=$USER
TEAM=$TEAM_NUMBER
EOF
echo ".env file created at $(realpath "$ENV_FILE")"

# I wrote this at 3am in the morning, ill figure out a better way soon
if (( ${#TEAM_NUMBER} <= 2 )); then
    TE_AM="0.$TEAM_NUMBER"
elif (( ${#TEAM_NUMBER} == 3 )); then
    TE_AM="${TEAM_NUMBER:0:1}.${TEAM_NUMBER:1:2}"
elif (( ${#TEAM_NUMBER} == 4 )); then
    TE_AM="${TEAM_NUMBER:0:2}.${TEAM_NUMBER:2:2}"
elif (( ${#TEAM_NUMBER} == 5 )); then
    TE_AM="${TEAM_NUMBER:0:3}.${TEAM_NUMBER:3:2}"
fi

GATEWAY="10.$TE_AM.1"
echo "GATEWAY=$GATEWAY" >> $ENV_FILE
ROBORIO_IP="10.$TE_AM.2"
echo "ROBORIO_IP=$ROBORIO_IP" >> $ENV_FILE

# Make samuraisight (the launch script) an executable and add it to the PATH variable
chmod +x $LAUNCH_PATH

echo "LAUNCH_ON_STARTUP=true" >> $ENV_FILE
cat <<EOF > /tmp/temp_service
[Unit]
Description=Robot Vision System
After=network.target

[Service]
ExecStart=$LAUNCH_PATH
Restart=on-failure
WorkingDirectory=$ROOT_DIR

[Install]
WantedBy=multi-user.target
EOF
sudo mv /tmp/temp_service $SERVICE_FILE
sudo systemctl daemon-reload
echo "SERVICE_FILE=$SERVICE_FILE" >> $ENV_FILE
echo "Configured Systemd service"


read -p "Do you want SamuraiSight to launch on startup? [Y/N]: " launchOnStartup
if [ "$launchOnStartup" == "Y" ]; then
    echo "LAUNCH_ON_STARTUP=true" >> $ENV_FILE
    sudo systemctl enable "$SERVICE_NAME.service"
    echo "Systemd service successfully enabled."
    echo "SamuraiSight will now start automatically on boot"
elif [ "$launchOnStartup" == "N" ]; then
    echo "LAUNCH_ON_STARTUP=false" >> $ENV_FILE
else
    echo "ERROR: Unrecognized response \"$launchOnStartup\""
    exit 2 #2 denotes that user input was malformed
fi

read -p "Do you want to set a static IP Address? [Y/N]: " SetStatic
if [ "$SetStatic" == "Y" ]; then
    echo "USE_STATIC_IP=true" >> $ENV_FILE
    read -p "Enter IP address: " StaticIP
    echo "STATIC_IP=$StaticIP" >> $ENV_FILE
elif [ "$SetStatic" == "N" ]; then
    echo "USE_STATIC_IP=false" >> $ENV_FILE
else
    echo "ERROR: Unrecognized response \"$SetStatic\""
    exit 2 #2 denotes that user input was malformed
fi

# This ensures the working directory is the root directory
cd $ROOT_DIR
VENV=".venv"
python3 -m venv $VENV
source ".venv/bin/activate"
pip install -r requirements.txt
echo "Successfully created python virtual environment"
exit 0 #0 means successful installation