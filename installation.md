# WIP, More detailed instructions will be written eventually
How to Install on a coprocessor (or any Debian-based machine):

Step 1: Image your coprocessor with a debian-based OS 
(This was tested and developed on Ubuntu)

Step 2: Install Python 3.13

Step 3: Install mrcal

Step 4: Clone this git repo onto your coprocessor

Step 5: Create python virtual environment (optional)

Step 6: Install requirements.txt

>As of now there is not a way to automatically start SamuraiVision when the coprocessor boots, you need to manually ssh into the coprocessor and launch SamuraiVision. Eventually I'll write a shell script or something to automatically launch SamuraiVision on startup.

>As a reminder, SamuraiVision is still under active development and is not ready for deployment. These installation instructions are for testing only

Install on a windows machine

Step 1: Install WSL2

Step 2: Install a debian-based distro in WSL

Step 3: Install usbipd in powershell, and bind the camera you wish to use to WSL2

From here, follow the linux installation instruction to install SamuraiVision in WSL2


