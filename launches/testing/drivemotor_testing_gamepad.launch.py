import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import launch_ros
from launch.actions import ExecuteProcess
from ament_index_python import get_package_share_directory
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare



def generate_launch_description():
    launch_description = LaunchDescription()


    # launch_description.add_action(
    #     launch_ros.actions.Node(
    #     package='comms_heartbeat_pkg',
    #     executable='heartbeat_reciever',
    #     name='heartbeat_reciever')
    # )

    # launch_description.add_action(
    #         ExecuteProcess(
    #             cmd=["sudo", "/sbin/ip", "link", "set", "can0", "up", "type", "can", "bitrate", "1000000",],
    #             output='screen'
    #         )
    #     )

    launch_description.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/components/joy.launch.py'
                ),
                launch_arguments={
            'joy_config': '8bit-p',
                }.items(),
        )
    )

    launch_description.add_action(
            launch_ros.actions.Node(
            package='can_interface_pkg',
            executable='can_subscriber_node',
            name='can_subscriber_node')
        )
    
    launch_description.add_action(
         IncludeLaunchDescription(
             PythonLaunchDescriptionSource(
                 PathJoinSubstitution([
                     FindPackageShare('drivebase_control_pkg'),
                     'launch',
                     'drivebase_control_node.launch.py'
                 ])
                 
                 ),
                 launch_arguments={
                'track_width': '0.914',
                'wheel_radius': '0.2540'
                }.items()
         )
    )
    
    return launch_description
