REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="/opt/SamuraiSight"
SERVICE_NAME=smsight
SERVICE_FILE="/etc/systemd/system/smsight.service"
echo -e "------------- SamuraiSight Installer -------------\n"

echo "Installing SamuraiSight in $ROOT_DIR"

# Check if samuraisight is already installed
if [ -d $ROOT_DIR ]; then
    echo "SamuraiSight is already installed"
    echo "Aborting installation"
    exit 1 # 1 denotes that samuraisight is already installed
fi

# Setting up the deployment directory
mkdir $ROOT_DIR
mkdir $ROOT_DIR/src
mkdir $ROOT_DIR/resources
mkdir $ROOT_DIR/bin
# Copying essential code from the repo to the deployment directory
cp -r $REPO_DIR/src $ROOT_DIR/src
cp -r $REPO_DIR/resources $ROOT_DIR/resources
cp -r $REPO_DIR/bin $ROOT_DIR/bin
cp $REPO_DIR/uninstall.sh $ROOT_DIR/uninstall.sh
cp $REPO_DIR/requirements.txt $ROOT_DIR/requirements.txt
cp $REPO_DIR/config.toml $ROOT_DIR/config.toml

# Loading service file
cp $REPO_DIR/smsight.service $SERVICE_FILE
systemctl daemon-reload

# Changing working directory to deployment directory in order to complete installation
cd $ROOT_DIR

useradd --system --no-create-home --shell /usr/sbin/nologin smsight-srv
usermod -aG video smsight-srv

read -p "Enter team number: " TEAM_NUMBER
read -p "Enter device name: " DEV_NAME

# Create .env file
ENV_FILE=".env"
cat > $ENV_FILE <<EOF
# Environment Configuration (Only edit this file if you know what you are doing)
APP_ENV=production
DEBUG=false
TEAM=$TEAM_NUMBER
SERVICE_FILE=$SERVICE_FILE
DEV_NAME=$DEV_NAME
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

# Make samuraisight (the launch script) an executable
chmod +x ./bin/smsight

read -p "Do you want SamuraiSight to launch on startup? [Y/N]: " launchOnStartup
if [ "$launchOnStartup" == "Y" ]; then
    systemctl enable "smsight.service"
    echo "SamuraiSight will launch automatically on startup. This can be disabled with sudo systemctl disable smsight.service"
elif [ "$launchOnStartup" == "N" ]; then
    echo "SamuraiSight will not launch on startup. To enable launch on startup, run sudo systemctl enable smsight.service"
else
    echo "ERROR: Unrecognized response \"$launchOnStartup\""
    echo "Defaulting to launch on startup. This can be disabled by running sudo systemctl disable smsight.service"
    systemctl enable "smsight.service"
fi

read -p "Do you want to set a static IP Address? [Y/N]: " SetStatic
if [ "$SetStatic" == "Y" ]; then
    echo "USE_STATIC_IP=true" >> $ENV_FILE
    read -p "Enter IP address: " StaticIP
    echo "STATIC_IP=$StaticIP" >> $ENV_FILE
elif [ "$SetStatic" == "N" ]; then
    echo "USE_STATIC_IP=false" >> $ENV_FILE
    echo "Using DHCP. WARNING: It is HIGHLY recommended to set a static IP for competitions"
    echo "To enable Static IP, set USE_STATIC_IP to true in the .env file, and add an entry called STATIC_IP assigned to the ip address"
else
    echo "ERROR: Unrecognized response \"$SetStatic\""
    echo "Defaulting to DHCP"
    echo "To enable Static IP, set USE_STATIC_IP to true in the .env file, and add an entry called STATIC_IP assigned to the ip address"
    echo "USE_STATIC_IP=false" >> $ENV_FILE
fi

VENV=".venv"
python3 -m venv $VENV
source ".venv/bin/activate"
pip install -r requirements.txt
echo "Successfully created python virtual environment"
# Creates logs/ directory, models/ directory, and recordings/ directory
mkdir logs
mkdir models
exit 0 #0 means successful installation