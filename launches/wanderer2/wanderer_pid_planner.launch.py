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

    # Luanch the PID planner
    launch_description.add_action(
            launch_ros.actions.Node(
            package='ros2_pid_planner_pkg',
            executable='pid_planner_node',
            name='pid_planner_node',
            parameters=[
                {'angle_threshold': 0.174533},
            ]
            )
        )
    
    # launch the GPS to ENU republished node
    launch_description.add_action(
            launch_ros.actions.Node(
            package='ros2_pid_planner_pkg',
            executable='gps2enu_repub_node',
            name='gps2enu_repub_node')
        )
    
    # launch the pixhawk localization solution
    launch_description.add_action(
            launch_ros.actions.Node(
            package='ros2_pid_planner_pkg',
            executable='pixhawk_node',
            name='pixhawk_node')
        )
    
    # Launch the CAN bus interface
    launch_description.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/components/can_interface.launch.py'
                ),
                launch_arguments={
                'current_rover': 'wanderer',
            }.items()
        )
    )

    # Launch the drivebase node
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
                'wheel_radius': '0.2540',
                'isHeimdall': 'False',
                'doHeartbeat' : 'False'
            }.items()
        )
    )
    
    return launch_description
