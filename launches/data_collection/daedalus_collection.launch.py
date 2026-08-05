import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, TextSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch.conditions import LaunchConfigurationEquals

def generate_launch_description():
    ld = LaunchDescription()

    rosbag_stuff = ExecuteProcess(
            cmd=['ros2', 'bag', 'record', '-a'],
            output='screen'
        )