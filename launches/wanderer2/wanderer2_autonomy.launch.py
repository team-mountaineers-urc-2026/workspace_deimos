import os
from launch import LaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

    
    ld = LaunchDescription()

    # Do Transform
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/wanderer2/wanderer2_static_tf.launch.py'
            )
        )
    )

    # Launch Cameras
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/wanderer2/wanderer2_usb_cam.launch.py'
            )
        )
    )

    # Launch Aruco
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/wanderer2/wanderer2_aruco.launch.py'
            )
        )
    )

    # Launch the drivebase node
    ld.add_action(
         IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([
                    FindPackageShare('drivebase_control_pkg'),
                    'launch',
                    'drivebase_control_node.launch.py'
                ])
            ),
            launch_arguments={
                'isHeimdall': 'False'
            }.items()
        )
    )

    # Launch the can interface
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/components/can_interface.launch.py'
                ),
                launch_arguments={
                'current_rover': 'wanderer2'
            }.items()
        )
    )

    return ld