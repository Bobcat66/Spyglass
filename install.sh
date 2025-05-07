#!/usr/bin/env bash
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME=samuraisight
LAUNCH_PATH="$ROOT_DIR/bin/$SERVICE_NAME"
USER=$(whoami)

echo -e "SamuraiSight Installer\n"

# Check if samuraisight is already installed
if command -v "$SERVICE_NAME" &>/dev/null; then
    echo -e "$SERVICE_NAME is already in PATH"
    echo "SamuraiSight is already installed"
    echo "Aborting installation"
    exit 1 # 1 denotes that samuraisight is already installed
fi

read -p "Enter team number: " TEAM_NUMBER

# Create .env file
ENV_FILE = ".env"
cat > "$ENV_FILE" <<EOF
# Environment Configuration (Only edit this file if you know what you are doing)
APP_ENV=production
DEBUG=false
ROOT_DIR=$ROOT_DIR
USER=$USER
TEAM=$TEAM_NUMBER
EOF
echo ".env file created at $(realpath "$ENV_FILE")"

echo "TEAM=$TEAM_NUMBER" >> $ENV_FILE

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



# Make smsght (the launch script) an executable and add it to the PATH variable
chmod +x $LAUNCH_PATH
echo "export PATH=\"\$PATH:$ROOT_DIR/bin\"" >> ~/.bashrc

read -p "Do you want SamuraiSight to launch on startup? [Y/N]: " launchOnStartup
if [ "$launchOnBoot" == "Y" ]; then
    SERVICE_FILE = "/etc/systemd/system/$SERVICE_NAME.service"
    echo "LAUNCH_ON_STARTUP=true" >> $ENV_FILE
    sudo bash -c "cat > $SERVICE_FILE"  <<EOF
[Unit]
Description=Robot Vision System
After=network.target

[Service]
ExecStart=$LAUNCH_PATH
Restart=on-failure
User=$USER
WorkingDirectory=$ROOT_DIR

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME.service"
    echo "SERVICE_FILE=$SERVICE_FILE" >> $ENV_FILE
    echo "Systemd service successfully configured and enabled."
    echo "SamuraiSight will now start automatically on boot"
elif [ "$launchOnBoot" == "N" ]; then
    echo "LAUNCH_ON_STARTUP=false" >> $ENV_FILE
else
    echo "ERROR: Unrecognized response \""$launchOnBoot"\""
    exit 2 #2 denotes that user input was malformed

# This ensures the working directory is the root directory
cd $ROOT_DIR
VENV=".venv"
python3 -m venv $VENV
source ".venv/scripts/activate"
pip install -r requirements.txt
echo "Successfully created python virtual environment"
exit 0 #0 means successful installation















