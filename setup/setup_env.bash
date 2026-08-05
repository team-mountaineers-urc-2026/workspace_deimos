#!/bin/bash

# setup necessary permissions
sudo usermod -aG tty $USER
sudo usermod -aG dialout $USER

# setup URC udev rules
./udev_rules/install_udev_rules.py
sudo udevadm control --reload-rules && sudo udevadm trigger

# setup for the seabreeze
seabreeze_os_setup

# install mavros geograph lib datasets
ros2 run mavros install_geographiclib_datasets.sh
