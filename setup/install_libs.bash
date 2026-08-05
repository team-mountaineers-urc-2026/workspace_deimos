#!/bin/bash

# apt dependencies
sudo apt install python3-pip # used to install python packages
sudo apt install python3-vcstool # tool for pulling many git repos with a single command
sudo apt install cmake # needed for building ROS workspaces
sudo apt install ros-humble-rqt-tf-tree # useful features for examining transform trees in ROS 
sudo apt install ros-humble-tf2-tools # useful tools for working with transforms in ROS 
sudo apt install can-utils # tools for managing/debugging CAN bus
sudo apt install ros-humble-mavros # mavros, used for navigation stuff
sudo apt install ros-humble-tf-transformations
sudo apt install python3-pyqt5.qtwebengine # GUI dependencies
sudo apt install sshpass # Comms Monitoring Dependency
sudo apt install joystick # Controller Testing
sudo apt install ffmpeg # Camera Manager Streams
sudo apt install grep # Search utility
sudo apt install nmap
sudo apt install tmux

# python dependencies
pip3 install dynamixel_sdk # used for controlling dynamixels
pip3 install seabreeze[pyseabreeze] # used for controlling the spectrometer
pip3 install python-can # used for sending CAN bus command using Python
pip3 install pyusb # USB tools for Python
pip3 install pyqt5 qtpy pyqtlet2==0.8.0 pyqtgraph pymap3d pyproj # GUI libs
pip3 install transforms3d # dependency for ArUco detection
pip install PyQtWebEngine
pip install pyqtlet2
pip install aioax25
