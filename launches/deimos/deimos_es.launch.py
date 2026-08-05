from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, DeclareLaunchArgument, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, RosTimer
from launch.conditions import LaunchConfigurationEquals, IfCondition
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
import os 
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import TextSubstitution

def generate_launch_description():

    # Create the Launch Description
    launch_description = LaunchDescription()

    drive_joy_config_arg  = DeclareLaunchArgument(name = 'drive_joy_config',        default_value = 'xbox',   description = 'The config file name for the controller [8bit-p-drive, 8bit-g-drive]')
    drive_config_path_arg = DeclareLaunchArgument(name = 'drive_config_filepath',   default_value = [
                                                                        TextSubstitution(text=os.path.join('launches/config', '')),
                                                                        LaunchConfiguration('drive_joy_config'),
                                                                        TextSubstitution(text='.config.yaml')
                                                                        ],                          description='The direct filepath to the controller config file')

    drive_config_filepath = LaunchConfiguration('drive_config_filepath')
    

    joy_config_arg  = DeclareLaunchArgument(name = 'joy_config',        default_value = '8bit-s-arm',   description = 'The config file name for the controller [8bit-p-arm, 8bit-g-arm]')
    joy_arg         = DeclareLaunchArgument(name = 'doJoy',             default_value = 'true',     description = 'Are you running the teleop with the joy control? [true, false]')
    ik_arg          = DeclareLaunchArgument(name = 'doIK',              default_value = 'false',    description = 'Are we running with inverse kinematic control? [true, false]')
    arm_config_path_arg = DeclareLaunchArgument(name = 'arm_config_filepath',   default_value = [
                                                                        TextSubstitution(text=os.path.join('launches/config', '')),
                                                                        LaunchConfiguration('joy_config'),
                                                                        TextSubstitution(text='.config.yaml')
                                                                        ],                          description='The direct filepath to the controller config file')
    arm_config_filepath = LaunchConfiguration('arm_config_filepath')
    do_joy_arg = LaunchConfiguration('doJoy')

    launch_description.add_action(joy_config_arg)
    launch_description.add_action(joy_arg)
    launch_description.add_action(ik_arg)
    launch_description.add_action(arm_config_path_arg)

    launch_description.add_action(drive_joy_config_arg)
    launch_description.add_action(drive_config_path_arg)


    # Daedalus Drive
    deimos_drive = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/deimos/deimos_drive.launch.py'
            ),
            launch_arguments={
                'doJoy': do_joy_arg,
                'joy_config': 'xbox',
                'config_filepath': drive_config_filepath,
            }.items(),
        )

    # Heimdall Arm Launch
    deimos_arm = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/deimos/deimos_arm.launch.py'
            ),
            launch_arguments={
                'doJoy': do_joy_arg,
                'joy_config': '8bit-s-arm',
                'config_filepath': arm_config_filepath,
            }.items(),
        )


    
    # Callsign stuff
    callsign_launch = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/components/callsign.launch.py'
            ),
            launch_arguments={
                'callsign': 'KF8CFI' # Izaak Whetsell's callsign
            }.items(),
        )

    # camera_manager autonomy launch
    camera_manager_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('camera_manager'), 'launch', 'cm_es.launch.py'])
        )
    )

    # Gimbal Cam
    gimbal_cam = \
        Node(
            namespace='',
            package='deimos_science',
            executable='gimbal_control'
	)

    # Pico Science Node
    pico_es = \
        Node(
            namespace='science',
            package='pico_interface_pkg',
            executable='pico_science_node'
        )
    
    # Pico Science Node
    qtpy_science = \
        Node(
            namespace='science',
            package='pico_interface_pkg',
            executable='qtpy_science_node'
        )

    # Comms Monitor
    comms_monitor = \
        Node(
            namespace='health_monitor',
            package='health_monitor_pkg',
            executable='comms_monitor'
        )

    # # Discovery Server
    # discovery_launch  = \
    #     IncludeLaunchDescription(
    #         PythonLaunchDescriptionSource(
    #             'launches/components/callsign.launch.py'
    #         ),
    #         launch_arguments={
    #             'callsign': 'KD3BCH'
    #         }.items(),
    #     )

    # Set up timers for each launch
    # discover_server_d       = RosTimer(period = 0.0, actions = [discovery_launch])
    # deimos_drive_d        = RosTimer(period = 2.0, actions = [callsign_launch, deimos_drive])
    # deimos_arm_d          = RosTimer(period = 4.0, actions = [deimos_arm, camera_manager_launch])
    # Arm Launch Descriptions
    launch_description.add_action(deimos_arm)

    # Drive Launch Descriptions
    launch_description.add_action(deimos_drive)
    launch_description.add_action(camera_manager_launch)
    launch_description.add_action(gimbal_cam)
    launch_description.add_action(pico_es)
    launch_description.add_action(qtpy_science)
    launch_description.add_action(comms_monitor)

    
    # Launch each individual thing
    # launch_description.add_action(discover_server_d)
    # launch_description.add_action(deimos_drive_d)
    # launch_description.add_action(deimos_arm_d)

    return launch_description
