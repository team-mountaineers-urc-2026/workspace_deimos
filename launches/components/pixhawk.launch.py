

def generate_launch_description():

    import os
    from launch import LaunchDescription
    from launch.launch_description_sources import PythonLaunchDescriptionSource
    from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
    from launch.actions import IncludeLaunchDescription, ExecuteProcess
    from launch_ros.actions import Node, RosTimer
    from launch_ros.substitutions import FindPackageShare
    import launch_ros
    from launch.substitutions import PathJoinSubstitution

    ld = LaunchDescription()

    ld.add_action(
        RosTimer(
            period = 5.0,
            actions = [
                IncludeLaunchDescription(
                    XMLLaunchDescriptionSource('./launches/components/urc_px4.launch'),
                    launch_arguments={
                        'fcu_url': '/dev/urc/mtc/pixhawk',
                        'config_yaml': './launches/config/urc_px4_config.yaml',
                    }.items()
                )
            ]
        )
    )

    return ld