#!/bin/bash

h ()
{
  echo "sheetz"
  echo "    The sheetz suite of commands, run \`sheetz help\` for an in depth listing"
  echo ""
  echo "signal_strength"
  echo "    Prints out the radio signal strength every 3 seconds"
  echo ""
  echo "launch <category>"
  echo "    Launches a setup component. Run with no arguments to list options"
  echo ""
  echo "pid <name>"
  echo "    Equivalent to 'ps aux | grep <name>'"
  echo ""
  echo "reset <motor_name>"
  echo "    Reset a given myactuatormotor"
  echo ""
  echo "--- DEPRECIATED ---"
  echo "start <camera_name> <lowest|low|mid|high|insane|incomprehensible>"
  echo "    Starts a Camera with the given preset"
  echo ""
  echo "decypher <camera_name>"
  echo "    Uncompresses a Camera using Theora"
  echo ""
  echo "recall <camera_name>"
  echo "    Resends the Theora Header for a camera"
  echo ""
  echo "replug <port>"
  echo "    Unbinds and Binds a USB port simulating un and replugging it"
  echo ""
  echo "flie <camera_name>"
  echo "    Republishes a camera with the image rotated 180 degrees"
  echo ""
  echo "contrast <camera_name> <value>"
  echo "    Changes the output contrast of a given camera"
  echo ""
  echo "brightness <camera_name> <value>"
  echo "    Changes the output brightness of a given camera"
  echo ""
  echo "pico <value>"
  echo "    Launches the Docker for a pico on port ttyACM<value>"
  echo ""
}

pid ()
{
  ps aux | grep "$1"
}

reset ()
{
  cd ~/workspace-daedalus && source install/setup.bash
  if [[ "$1" == "front_right" || "$1" == "front_left" || "$1" == "back_right" || "$2" == "back_left" ]]; then
    ros2 topic pub /drivetrain/"$1"/send/reset controls_msgs/msg/SystemResetMsgSentParams "{}" --once
  elif [[ "$1" == "drill" ]]; then
    ros2 topic pub /science/"$1"/send/reset controls_msgs/msg/SystemResetMsgSentParams "{}" --once
  else
    ros2 topic pub /manipulator/"$1"/send/reset controls_msgs/msg/SystemResetMsgSentParams "{}" --once
  fi
}


start ()
{
  if [[ "$2" == "lowest" || "$2" == "low" || "$2" == "mid" || "$2" == "high" || "$2" == "pano" || "$2" == "insane" || "$2" == "incomprehensible" ]]; then
    cd ~/workspace-heimdall && source install/setup.bash && ros2 launch launches/components/dynamic_cam.launch.py camera_name:="$1" param_file:="$2.yaml"
  else
    echo "$2 is not valid"
    echo "Please use lowest | low | mid | high | insane | pano | incomprehensible"
  fi
}

recall ()
{
  ros2 service call "$1_mux/recall_header" std_srvs/srv/Trigger
}

decypher ()
{
  cd ~/image-transport-ws && source install/setup.bash && ros2 run image_transport republish --ros-args -p in_transport:='theora' -p out_transport:='raw' -r "in/theora":="/$1/image_raw/theora_mux" -r "out":="/$1/image_uncompressed" -r __node:="$1_decypherer"
}

replug ()
{
  echo "$1" | sudo tee /sys/bus/usb/drivers/usb/unbind
  sleep 3
  echo "$1" | sudo tee /sys/bus/usb/drivers/usb/bind
}

path ()
{
  sudo udevadm info /dev/urc/cam/"$1" | grep P:
}

flip ()
{
  cd ~/workspace-heimdall && source install/setup.bash && ros2 run image_mod_pkg image_flip --ros-args -r "/input":="/$1/image_uncompressed" -r "/output:=/$1/image_flipped"
}

contrast ()
{
  ros2 param set "$1" contrast "$2"
}

brightness ()
{
  ros2 param set "$1" brightness "$2"
}

pico ()
{
  sudo docker run -it --rm -v /dev:/dev --privileged --net=host microros/micro-ros-agent:humble serial --dev /dev/ttyACM"$1" -b 115200
}

signal_strength()
{
  cd ~/workspace-deimos && ./scripts/comms/print_signal_strength.py
}


 
MOUNT_DIR="$HOME/coords_usb_drive"
DEVICE_FILE="/tmp/coords_usb_device"

mount_usb_drive() {
    before=$(ls /dev/sd* 2>/dev/null | grep -E '/dev/sd[a-z][0-9]+$')

    echo "Insert USB drive..."

    while :; do
        sleep 2

        after=$(ls /dev/sd* 2>/dev/null | grep -E '/dev/sd[a-z][0-9]+$')

        new_dev=$(comm -13 \
            <(echo "$before" | sort) \
            <(echo "$after" | sort) | head -n1)

        if [[ -n "$new_dev" ]]; then
            device="$new_dev"

            echo "Detected: $device"

            mkdir -p "$MOUNT_DIR"

            sudo mount "$device" "$MOUNT_DIR"

            if [[ $? -ne 0 ]]; then
                echo "Mount failed"
                return 1
            fi

            # Save device path for later unmount
            echo "$device" > "$DEVICE_FILE"

            echo "Mounted $device at $MOUNT_DIR"
            break
        fi
    done

    mkdir -p "$HOME/recieved_coords_from_drive"

    if cp -r "$MOUNT_DIR"/* "$HOME/recieved_coords_from_drive/" 2>/dev/null; then
        if [ "$(ls -A "$HOME/recieved_coords_from_drive" 2>/dev/null)" ]; then
            echo "Files copied successfully to ~/recieved_coords_from_drive/"
        else
            echo "cp succeeded but destination appears empty"
            return 1
        fi
    else
        echo "Copy failed"
        return 1
    fi

    if [[ ! -f "$DEVICE_FILE" ]]; then
          echo "No saved device found."
          return 1
      fi

      device=$(cat "$DEVICE_FILE")

      echo "Unmounting $device..."

      sudo umount "$device"

      if [[ $? -eq 0 ]]; then
          echo "Unmount successful"

          rm -f "$DEVICE_FILE"
      else
          echo "Unmount failed"
          return 1
      fi

}

unmount_usb_drive() {
    if [[ ! -f "$DEVICE_FILE" ]]; then
        echo "No saved device found."
        return 1
    fi

    device=$(cat "$DEVICE_FILE")

    echo "Unmounting $device..."

    sudo umount "$device"

    if [[ $? -eq 0 ]]; then
        echo "Unmount successful"

        rm -f "$DEVICE_FILE"
    else
        echo "Unmount failed"
        return 1
    fi
}


launch ()
{
  if [[ "$1" == "es" || "$1" == "er" || "$1" == "dm" || "$1" == "d" ]]; then
    # export ROS_DISCOVERY_SERVER="192.168.1.94:11811";
    cd ~/workspace-deimos && source install/setup.bash && sudo ls && ros2 launch launches/deimos/deimos_es.launch.py 'doJoy':='false'

  elif [[ "$1" == "science" ]]; then
    cd ~/workspace-deimos && source install/setup.bash && sudo ls && ros2 launch launches/deimos/deimos_science.launch.py  'doJoy':='false'

  elif [[ "$1" == "gui" ]]; then
    # export ROS_DISCOVERY_SERVER="192.168.1.94:11811";
    cd ~/workspace-deimos && source install/setup.bash && cd ~/ros2-rover-gui && ./start_gui.bash

  elif [[ "$1" == "es_tethered" || "$1" == "er_tethered" || "$1" == "dm_tethered" || "$1" == "d_tethered" ]]; then
    cd ~/workspace-deimos && source install/setup.bash && sudo ls && ros2 launch launches/deimos/deimos_es.launch.py

  elif [[ "$1" == "drive" ]]; then
    cd ~/workspace-deimos && source install/setup.bash && sudo ls && ros2 launch launches/deimos/deimos_drive.launch.py

  elif [[ "$1" == "arm" ]]; then
    cd ~/workspace-deimos && source install/setup.bash && sudo ls && ros2 launch launches/deimos/deimos_arm.launch.py

  elif [[ "$1" == "es_base" || "$1" == "er_base" || "$1" == "dm_base" || "$1" == "d_base" ]]; then
    # export ROS_DISCOVERY_SERVER="192.168.1.94:11811";
    cd ~/workspace-deimos && source install/setup.bash  && ros2 launch launches/base_station/base_station_es.launch.py

  elif [[ "$1" == "autonomy" ]]; then
    cd ~/workspace-deimos && source install/setup.bash && sudo ls && ros2 launch launches/deimos/deimos_auto.launch.py

  elif [[ "$1" == "science_base" ]]; then
    cd ~/workspace-deimos && source install/setup.bash && ros2 launch launches/base_station/base_station_science.launch.py

  elif [[ "$1" == "autonomy_base" ]]; then
    cd ~/workspace-deimos && source install/setup.bash && ros2 launch launches/base_station/base_station_autonomy.launch.py


  else
    echo "The Following Arguments are Valid:"
    echo "es"
    echo "dm | d | er"
    echo ""
    echo "es_tethered"
    echo "dm_tethered | d_tethered | er_tethered"
    echo ""
    echo "es_base"
    echo "dm_base | d_base | er_base"
    echo ""
    echo "science"
    echo "science_base"
    echo ""
    echo "autonomy"
    echo "autonomy_base"
    echo ""
    echo "gui"
    echo "drive"
    echo "arm"
  fi
}

can ()
{
  if [ "$#" -ne 2 ]; then
    echo "!! Incorrect Number of Arguments !!"
  fi

  if [[ $1 =~ ^[0-3]+$  && "$2" == "end" ]]; then
    echo "Shutting down can$1...."
    sudo ip link set can$1 down

  elif [[ $1 =~ ^[0-3]+$ && "$2" == "start" ]]; then
    echo "Spinning up can$1...."
    sudo /sbin/ip link set can$1 up type can bitrate 1000000

  else
    echo "The Following Arguments are Valid:"
    echo "can # start"
    echo "can # end"
  fi

}

sheetz ()
{
  # HELP COMMAND
  if [[ "$1" == "help" ]]; then
    echo ""
    echo "      help        - Prints this help message"
    echo ""
    echo "      bag         - Records preset ros2 topics into a rosbags folder located in your home directory"
    echo "      build       - Builds a colcon workspace with self-dependencies"
    echo "      construct   - Builds a colcon workspace bypassing errors"
    echo "      nuke        - Removes a colcon workspace present in the current directory"

    return 1
  fi

  # BUILD COMMAND
  if [[ "$1" == "build" ]]; then

    # Check to see if a src folder exists
    if [ -d ./src ]; then
      colcon build --continue-on-error;
      source install/setup.bash;
      colcon build --packages-select-build-failed

    # If no src folder exists ask the user
    else
      echo "No \`src\` folder found."
      while true; do
        echo "Do you wish to continue? [y/n]"
        read -p "" yn
        case $yn in
          [Yy]* ) colcon build --continue-on-error; source install/setup.bash; colcon build --packages-select-build-failed; source install/setup.bash; break;;
          [Nn]* ) break;;
          * ) echo "Please answer y or n.";;
        esac
      done
    fi

    return 1
  fi

  # CONSTRUCT COMMAND
  if [[ "$1" == "construct" ]]; then

    # Check to see if a src folder exists
    if [ -d ./src ]; then
      colcon build --continue-on-error;
      source install/setup.bash

    # If no src folder exists ask the user
    else
      echo "No \`src\` folder found."
      while true; do
        echo "Do you wish to continue? [y/n]"
        read -p "" yn
        case $yn in
          [Yy]* ) colcon build --continue-on-error; source install/setup.bash; break;;
          [Nn]* ) break;;
          * ) echo "Please answer y or n.";;
        esac
      done
    fi

    return 1
  fi

  # NUKE COMMAND
  if [[ "$1" == "nuke" ]]; then

    echo "This action is irreversable"
    while true; do
      echo "Do you wish to continue? [y/n]"
      read -p "" yn
      case $yn in
        [Yy]* ) rm -rf build/ install/ log/; echo "Workspace removed."; break;;
        [Nn]* ) break;;
        * ) echo "Please answer y or n.";;
      esac
    done

    return 1
  fi

  # BAG COMMAND
  if [[ "$1" == "bag" ]]; then

    NAME="$(date +"rosbag2_%Y_%m_%d-%H_%M_%S")"

    # Chassis Bag
    if [[ "$2" == "chassis" ]]; then
      echo "CHASSIS NOT YET IMPLEMENTED"

    elif [[ "$2" == "manipulator" ]]; then
      echo "MANIPULATOR NOT YET IMPLEMENTED"

    elif [[ "$2" == "science" ]]; then
      echo "SCIENCE NOT YET IMPLEMENTED"

    elif [[ "$2" == "realsense" ]]; then
      echo "REALSENSE NOT YET IMPLEMENTED"

    elif [[ "$2" == "autonomy" ]]; then
      echo "AUTONOMY NOT YET IMPLEMENTED"

    elif [[ "$2" == "help" ]]; then
      echo "Supported bag commands are:"
      echo ""
      echo "    help        : Displays this message"
      echo ""
      echo "    all         : Every Topic being Published" 
      echo "    autonomy    : /?"
      echo "    base        : /?"
      echo "    chassis     : /drivebase/cmd_vel, /? "
      echo "    realsense   : /?"
      echo "    manipulator : /?"
      echo "    science     : /?"
      
    elif [[ "$2" == "all" ]]; then
      ros2 bag record -a -o $(eval echo ~$USER)/rosbags/$NAME

    else
      echo "Error: argument not supported. Run \`sheetz bag help\` for a list of supported arguments";

    fi
    return 1

  fi

  echo "Error: command does not exist. Run \`sheetz help\` for a list of commands";
}
