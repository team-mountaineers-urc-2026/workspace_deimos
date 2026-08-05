import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions.node import Node
from launch.actions import ExecuteProcess
from ament_index_python import get_package_share_directory

def generate_launch_description():

    ld = LaunchDescription()

    # # Lidar Link (Not working)
    # ld.add_action(
    #     Node(
    #         package="tf2_ros",
    #         executable="static_transform_publisher",
    #         output="screen" ,
    #         # X, Y, Z, Yaw, Pitch, Roll
    #         arguments=["0", "0", "0", "0", "0", "0", "base_link", "velodyne"]
    #     ))
    
    # Pixhawk GPS Link (Not working)
    ld.add_action(
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            output="screen",
            # X, Y, Z, Yaw, Pitch, Roll
            arguments=["0.145", "0.0875", "0.095", "1.57079632679", "0.0", "3.14159265359", "base_link", "pixhawk_gps"]
        )
    )
    
    # Pixhawk IMU link (Not Working)
    ld.add_action(
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            output="screen",
            # X, Y, Z, Yaw, Pitch, Roll
            arguments=["0.145", "-0.09", "0.095", "1.57079632679", "0.0", "3.14159265359", "base_link", "pixhawk_imu"]
        )
    )

    # Front Camera Link
    ld.add_action(
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            output="screen",
            # X, Y, Z, Yaw, Pitch, Roll
            arguments=["0.184", "0.226", "0.1125", "3.14159265359", "-1.57079632679", "0.0", "base_link", "front"]
        )
    )

    # Left Camera Link
    ld.add_action(
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            output="screen",
            # X, Y, Z, Yaw, Pitch, Roll
            arguments=["0.159", "0.3255", "0.1125", "-1.57079632679", "-1.57079632679", "0.0", "base_link", "left"]
        )
    )

    # Right Camera Link
    ld.add_action(
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            output="screen",
            # X, Y, Z, Yaw, Pitch, Roll
            arguments=["0.159", "-0.3255", "0.1125", "1.57079632679", "-1.57079632679", "0.0", "base_link", "right"]
        )
    )

    return ld