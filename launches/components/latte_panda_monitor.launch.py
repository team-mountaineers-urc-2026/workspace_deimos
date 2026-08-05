import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    ld = LaunchDescription()

    # Computer Monitor
    computer_monitor = \
        Node(
            name='computer_monitor_node',
            package='health_monitor_pkg',
            executable='computer_monitor',
            output='log',
            parameters= [
                        {'poll_period' : 1.0},
                        {'cpu_count' : 16},
                        {'network_interface' : 'enp2s0'},
                        {'partition' : '/dev/nvme0n1p2'}],
        )

    ld.add_action(computer_monitor)

    return ld
