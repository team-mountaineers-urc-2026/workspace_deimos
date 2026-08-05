#!/bin/bash

# This script installs ROS Humble and some WVU URC stuff that is not handled by rosdep.
# It assumes you are running Ubuntu 22.04.
# The script is based on the ROS Humble isntall guide for Ubuntu:
# https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html

# ROS2 Humble Install

# 1.0 Set locale
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# 1.1 Configure Ubuntu repositories
sudo apt install software-properties-common
sudo add-apt-repository -y universe

# 1.2 Set up your keys
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

# 1.3 Set up your sources.list
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# 1.4 Installation
sudo apt update && sudo apt upgrade -y
sudo apt install ros-humble-desktop -y

# 1.5 Environment Setup
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc

# 1.6 Setup for colcon
sudo apt install python3-colcon-common-extensions -y
echo "source /usr/share/colcon_cd/function/colcon_cd.sh" >> ~/.bashrc
echo "export _colcon_cd_root=/opt/ros/humble/" >> ~/.bashrc
echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" >> ~/.bashrc

# 1.7 Setup for rosdep
sudo apt-get install python3-rosdep -y
sudo rosdep init
rosdep update

# 2 WVU URC specific stuff

# 2.1 apt packages and library installs 
sudo apt install python3-pip python3-vcstool cmake
sudo apt-get install ros-humble-camera-info-manager
sudo apt install ros-humble-rqt-tf-tree
sudo apt install ros-humble-tf2-tools 
pip install python-can
sudo apt install can-utils
sudo apt-get install ros-humble-mavros
ros2 run mavros install_geographiclib_datasets.sh
pip install seabreeze[pyseabreeze]=2.7.0
seabreeze_os_setup
pip3 install pyusb
pip3 install opencv-contrib-python transforms3d
sudo apt-get install ros-humble-tf-transformations

# 2.2 IP Address Specific Stuff
#echo "What IP address will this computer be using?"
#echo "Please enter in form XXX.XXX.XXX.XXX"
#read ip
#echo "export URC_IP_ADDRESS=$ip" >> ~/.bashrc

# 2.3 user groups
sudo usermod -a -G tty $USER
sudo usermod -a -G dialout $USER

echo "#######################################
ROS HUMBLE INSTALL COMPLETE
VIEW README.md FOR ADDITIONAL SETUP STEPS
#######################################"
