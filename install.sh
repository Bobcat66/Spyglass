# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="/opt/Spyglass"
SERVICE_NAME=spyglass
SERVICE_FILE="/etc/systemd/system/spyglass.service"
ROOTSRV_FILE="/etc/systemd/system/spg-rootsrv.service"
echo -e "------------- Spyglass Installer -------------\n"

echo "Installing Spyglass in $ROOT_DIR"

# Checks to ensure the script is being run with root permissions
if [[ $EUID -ne 0 ]]; then
  echo "The Spyglass installer must be run with root privileges."
  echo "Aborting installation."
  exit 2 # exit code 2 denotes that the script was running with improper permissions
fi

if [ ! -f "/etc/debian_version" ]; then
   echo "The Spyglass installer is only designed to run on debian-based distros. /etc/debian_version was not detected on this system."
   echo "Aborting installation."
   exit 3 # 3 denotes the installer was run on an improperly configured system
fi

if ! dpkg -l | grep -q "systemd"; then
    echo "Spyglass runs as a systemd service. Systemd was not detected on this system"
    echo "Aborting installation."
    exit 3
fi

# Check if spyglass is already installed
if [ -d $ROOT_DIR ]; then
    echo "Spyglass is already installed"
    echo "Aborting installation."
    exit 4 # 4 denotes that spyglass is already installed
fi

# Prompt the user to allow the installer to make changes to the network configuration
echo "Spyglass will make changes to the configuration of network interface eth0."
read -p "Do you want to continue? [y/N]: " userAllowedNetwork
case $userAllowedNetwork in
    y|Y )
        ;;
    n|N )
        echo "Aborting installation."
        exit 1 # 1 indicates that the user aborted installation
        ;;
    * )
        echo "WARNING: Unrecognized response \"$userAllowedNetwork\""
        echo "Aborting installation."
        exit 1
        ;;
esac

function promptNetMgmt {
    local userAllowedNetMgmt
    read -p "Allow Spyglass to perform network management itself? [y/N]: " userAllowedNetMgmt
    case $userAllowedNetMgmt in
    y|Y )
        return 0
        ;;
    n|N )
        echo "Aborting installation."
        exit 1 # 1 indicates that the installation was aborted due to user input
        ;;
    * )
        echo "WARNING: Unrecognized response \"$userAllowedNetMgmt\""
        echo "Aborting installation."
        exit 1
        ;;
    esac
}
# Detect primary network manager
if systemctl --quiet is-active systemd-networkd; then
    # systemd-networkd is the preferred network manager for Spyglass
    NETMNGR=NETWORK_D
    NETWORK_FILE="/etc/systemd/network/10-spyglass-eth0.network"
    cat > $NETWORK_FILE <<EOF
;Spyglass Network Configuration File. DO NOT MODIFY THIS MANUALLY
[Match]
Name=eth0

[Network]
DHCP=yes
;Address=
Gateway=_dhcp4
EOF
elif systemctl --quiet is-active NetworkManager; then
    #NETMNGR=NETWORK_MANAGER # Uncomment this when NetworkManager is supported
    echo "WARNING: NetworkManager is currently unsupported by Spyglass. We strongly recommend switching to systemd-networkd"
    promptNetMgmt
    NETMNGR=UNKNOWN
elif systemctl --quiet is-active dhcpcd; then
    #NETMNGR=DHCPCD # Uncomment this when dhcpcd is supported
    echo "WARNING: dhcpcd is currently unsupported by Spyglass. We strongly recommend switching to systemd-networkd"
    promptNetMgmt
    NETMNGR=UNKNOWN
elif systemctl --quiet is-active networking; then
    #NETMNGR=IFUPDOWN # Uncomment this when Ifupdown support is added
    echo "WARNING: Ifupdown is currently unsupported by Spyglass. We strongly recommend switching to systemd-networkd"
    promptNetMgmt
    NETMNGR=UNKNOWN
else
    # Prompt user to allow Spyglass to directly configure the network
    echo "WARNING: Unknown network manager. We strongly recommend switching to systemd-networkd"
    promptNetMgmt
    NETMNGR=UNKNOWN
fi


# Prompt the user to allow the installer to install Spyglass dependencies.

echo "This script will install the following dependencies: python3.13, python3.13-venv, software-properties-common, mrcal."
echo "Additionally, this script will add the deadsnakes PPA to your system."
read -p "Do you want to continue? [y/N]: " userAllowedDeps
case "$userAllowedDeps" in
    y|Y )
        apt-get -y update
        apt-get -y install software-properties-common mrcal
        add-apt-repository -y ppa:deadsnakes/ppa
        apt-get -y update
        apt-get -y install python3.13 python3.13-venv
        ;;
    n|N )
        echo "Aborting installation."
        exit 1
        ;;
    * )
        echo "WARNING: Unrecognized response \"$userAllowedDeps\""
        echo "Aborting installation."
        exit 1
        ;;
esac

read -p "Enter team number: " TEAM_NUMBER
case ${#TEAM_NUMBER} in
    0 )
        echo "No team number entered."
        echo "Aborting installation."
        exit 1
        ;;
    1|2 )
        TE_AM="0.$TEAM_NUMBER"
        ;;
    3 )
        TE_AM="${TEAM_NUMBER:0:1}.${TEAM_NUMBER:1:2}"
        ;;
    4 )
        TE_AM="${TEAM_NUMBER:0:2}.${TEAM_NUMBER:2:2}"
        ;;
    5 )
        TE_AM="${TEAM_NUMBER:0:3}.${TEAM_NUMBER:3:2}"
        ;;
    * )
        echo "Team numbers must be between 1 and 5 digits long"
        echo "Aborting installation"
        exit 1
        ;;
esac

read -p "Enter device name: " DEV_NAME

# --- After this point, the installation will not abort automatically unless there is an exception ---

# Setting up the deployment directory
mkdir $ROOT_DIR

# Copying essential code from the repo to the deployment directory
cp -r $REPO_DIR/src/core $ROOT_DIR
cp -r $REPO_DIR/src/rootsrv $ROOT_DIR
cp -r $REPO_DIR/resources $ROOT_DIR
cp -r $REPO_DIR/bin $ROOT_DIR
cp $REPO_DIR/uninstall.sh $ROOT_DIR/uninstall.sh
cp $REPO_DIR/requirements.txt $ROOT_DIR/requirements.txt
cp $REPO_DIR/config.toml $ROOT_DIR/config.toml

# Loading service file
cp $REPO_DIR/services/spyglass.service $SERVICE_FILE
cp $REPO_DIR/services/spg-rootsrv.service $ROOTSRV_FILE
systemctl daemon-reload
systemctl enable spg-rootsrv.service

# Changing working directory to deployment directory in order to complete installation
cd $ROOT_DIR

groupadd spyglass
useradd --system --no-create-home --shell /usr/sbin/nologin spyglass-srv
usermod -aG video spyglass-srv
usermod -aG spyglass spyglass-srv

# Create .env file
ENV_FILE=".env"
cat > $ENV_FILE <<EOF
# Environment Configuration (Only edit this file if you know what you are doing)
APP_ENV=production
DEBUG=false
TEAM=$TEAM_NUMBER
DEV_NAME=$DEV_NAME
USE_STATIC_IP=false
GATEWAY=10.$TE_AM.1
ROBORIO=10.$TE_AM.2
NETMNGR=$NETMNGR
MRCAL=true
EOF

echo ".env file created at $(realpath "$ENV_FILE")"

# Make all files in the /bin directory executable
find /opt/Spyglass/bin -type f -exec chmod +x {} \;

read -p "Do you want Spyglass to launch on startup? [y/N]: " launchOnStartup
case "$launchOnStartup" in
    y|Y )
        systemctl enable spyglass
        echo "Spyglass will launch automatically on startup. This can be disabled with sudo systemctl disable spyglass"
        ;;
    n|N )
        echo "Spyglass will not launch on startup. To enable launch on startup, run sudo systemctl enable spyglass"
        ;;
    * )
        echo "WARNING: Unrecognized response \"$launchOnStartup\""
        echo "Defaulting to launch on startup. This can be disabled by running sudo systemctl disable spyglass"
        systemctl enable spyglass
        ;;
esac

read -p "Do you want to set a static IP Address? [y/N]: " SetStatic
case "$SetStatic" in 
    y|Y )
        read -p "Enter IP address: " StaticIP
        ./bin/rootsrv/netconfig -s $StaticIP
        echo "Using static IP."
        ;;
    n|N )
        ./bin/rootsrv/netconfig -d
        echo "Using DHCP. WARNING: It is HIGHLY recommended to set a static IP for competitions"
        echo "To enable Static IP, set USE_STATIC_IP to true in the .env file, and add an entry called STATIC_IP assigned to the ip address"
        ;;
    * )
        ./bin/rootsrv/netconfig -d
        echo "WARNING: Unrecognized response \"$SetStatic\""
        echo "Defaulting to DHCP. WARNING: It is HIGHLY recommended to set a static IP for competitions"
        echo "To enable Static IP, set USE_STATIC_IP to true in the .env file, and set the STATIC_IP entry to the address you want to use"
        ;;
esac


VENV=".venv"
python3.13 -m venv $VENV
source ".venv/bin/activate"
pip install -r requirements.txt
echo "Successfully created python virtual environment"
# Creates logs/ directory, and models/ directory
mkdir logs
mkdir models
echo "ROOTSRV_SOCK=ipc:///tmp/spg-rootsrv.sock" >> $ENV_FILE
mkdir output # Output is a directory which can be written to by the spyglass service
cd output
mkdir logs
mkdir calib
mkdir cap
cd ..
chown -R :spyglass /opt/Spyglass/output
chmod -R g+w /opt/Spyglass/output
chmod g+s /opt/Spyglass/output
exit 0