import os

from ament_index_python.packages import get_package_share_directory

import launch
import launch_ros.actions

def generate_launch_description():
    joy_config = launch.substitutions.LaunchConfiguration('joy_config')
    device_path = launch.substitutions.LaunchConfiguration('device_path')
    config_filepath = launch.substitutions.LaunchConfiguration('config_filepath')

    return launch.LaunchDescription([
        launch.actions.DeclareLaunchArgument('joy_vel', default_value='cmd_vel'),
        launch.actions.DeclareLaunchArgument('joy_config', default_value='xbox'),
        launch.actions.DeclareLaunchArgument('device_path', default_value='/dev/input/js0'),
        launch.actions.DeclareLaunchArgument('config_filepath', default_value=[
            launch.substitutions.TextSubstitution(text=os.path.join('launches/config', '')),
            joy_config, launch.substitutions.TextSubstitution(text='.config.yaml')]),

        launch_ros.actions.Node(
            package='joy_controller', executable='JoyController', name='joy_node',
            parameters=[{
                'device': device_path,
                'deadzone': 0.3,
                'JC_publish_rate': 20,
            }]),
        launch_ros.actions.Node(
            package='teleop_twist_joy',
            executable='teleop_node',
            name='teleop_twist_joy_node',
            parameters=[config_filepath],
            remappings={('/cmd_vel', launch.substitutions.LaunchConfiguration('joy_vel'))},
        ),
        launch.actions.LogInfo(msg=[config_filepath]),
    ])

