import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnShutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import LaunchConfigurationEquals, IfCondition
from launch.actions import ExecuteProcess, LogInfo, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression, PathJoinSubstitution, TextSubstitution
from ament_index_python import get_package_share_directory
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node, RosTimer

def generate_launch_description():
    launch_description = LaunchDescription()

    # Controller Names
    drive_controller = '/dev/urc/js/daedalus_drive'

    # Declare Each Argument
    joy_config_arg  = DeclareLaunchArgument(name = 'joy_config',        default_value = 'xbox',   description = 'The config file name for the controller [8bit-p, 8bit-g]')
    config_path_arg = DeclareLaunchArgument(name = 'config_filepath',   default_value = [
                                                                        TextSubstitution(text=os.path.join('launches/config', '')),
                                                                        LaunchConfiguration('joy_config'),
                                                                        TextSubstitution(text='.config.yaml')
                                                                        ],                          description='The direct filepath to the controller config file')

    # Add each argument
    launch_description.add_action(joy_config_arg)
    launch_description.add_action(config_path_arg)

    # Get the important values
    config_filepath     = LaunchConfiguration('config_filepath')
    
    # Joy Control
    drive_joy_node = \
        Node(
            namespace='base_station',
            package='joy_controller',
            executable='JoyController',
            name='joy_node',
            parameters=[
                {
                'device' : drive_controller,
                'deadzone': 0.3,
                'JC_publish_rate': 20,
                }
            ]
        )
    
    # Teleop Joy Decypherer
    drive_teleop_node = \
        Node(
            namespace='base_station',
            package='teleop_twist_joy',
            executable='teleop_node',
            name='teleop_twist_joy_node',
            parameters=[config_filepath],
            # remappings={('cmd_vel', 'cmd_vel_rfmux')},
        )

    # Callsign stuff
    callsign_launch = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/components/callsign.launch.py'
            ),
            launch_arguments={
                'callsign': 'KD3BCH'
            }.items(),
        )
    
    # # Discovery Server
    # discovery_launch  = \
    #     IncludeLaunchDescription(
    #         PythonLaunchDescriptionSource(
    #             'launches/components/discovery_server.launch.py'
    #         ),
    #         launch_arguments={
    #             'server_ip': '192.168.1.94'
    #         }.items(),
    #     )

    launch_description.add_action(drive_joy_node)
    launch_description.add_action(drive_teleop_node)
    launch_description.add_action(callsign_launch)

    return launch_description