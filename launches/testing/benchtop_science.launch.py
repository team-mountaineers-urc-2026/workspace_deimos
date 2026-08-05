from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os

def generate_launch_description():
    launch_description = LaunchDescription()

    config_dir = os.path.join(get_package_share_directory('heimdall_gui'),('config')) # TODO this currently doesn't exist

    config = os.path.join(config_dir, 'gui_params.yaml')

    # Launches the GUI
    launch_description.add_action(
        Node(
            package='heimdall_gui',
            executable='gui',
        )
    )

    # Launches the spectrometer
    launch_description.add_action(
    Node(
        package='science_control_pkg',
        executable='ocean_optics_spectrometer_node',
        name='ocen_optics_spectrometer_node'
        )
    )

    # Launches the Dynamixels
    launch_description.add_action(
    Node(
        package='science_control_pkg',
        executable='dynamixel_control_node',
        name='dynamixel_control_node'
        )
    )

    # Launches the MyActuator motor used for the core drill
    launch_description.add_action(
    Node(
        package='science_control_pkg',
        executable='subsurface_motor_node',
        name='subsurface_motor_node'
        )
    )
    
    return launch_description
