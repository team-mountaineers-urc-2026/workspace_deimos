import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, LogInfo, DeclareLaunchArgument
from ament_index_python import get_package_share_directory
from launch.event_handlers import OnShutdown
from time import sleep
from launch.conditions import LaunchConfigurationEquals
from launch.substitutions import TextSubstitution, LaunchConfiguration

def generate_launch_description():
    launch_description = LaunchDescription()

    # Arguments
    curr_rover_arg = DeclareLaunchArgument(name = 'current_rover', default_value = 'heimdall', description = 'What Rover are you running?')
    network_name_arg = DeclareLaunchArgument(name = 'can_network_id', default_value = 'can0', description = 'What network are you using?')
    
    launch_description.add_action(curr_rover_arg)
    launch_description.add_action(network_name_arg)

    # Bring the network up
    can_network_up = \
        ExecuteProcess(
            cmd=[["echo ", LaunchConfiguration('current_rover'), " | sudo -S /sbin/ip link set ", LaunchConfiguration('can_network_id'), " up type can bitrate 1000000"]],
            shell=True,
            output='screen'
        )

    # Launch the interface node
    can_interface_node = \
        Node(
            package='controls_pkg',
            executable='can',
            name=[LaunchConfiguration('can_network_id'), '_subscriber_node'],
            namespace=['/',LaunchConfiguration('can_network_id'), '_interface'],
            parameters= [{'can_network_id' : LaunchConfiguration('can_network_id')}]
        )

    launch_description.add_action(can_network_up)
    launch_description.add_action(can_interface_node)
 
    return launch_description
