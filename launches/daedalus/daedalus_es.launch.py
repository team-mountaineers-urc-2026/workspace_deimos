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

    drive_tethered_arg      = DeclareLaunchArgument(name = 'is_tethered_drive', default_value = 'true',  description = 'Is the drive controllers plugged in to daedalus? [\'true\', \'false\']')
    arm_tethered_arg        = DeclareLaunchArgument(name = 'is_tethered_arm',   default_value = 'true',  description = 'Is the drive controllers plugged in to daedalus? [\'true\', \'false\']')
    inverse_kinematics_arg  = DeclareLaunchArgument(name = 'ik_manipulator',    default_value = 'false', description = 'Should we launch the manipulator with Inverse Kinematic Controls or not? [\'true\', \'false\']')

    launch_description.add_action(drive_tethered_arg)
    launch_description.add_action(arm_tethered_arg)
    launch_description.add_action(inverse_kinematics_arg)

    # Get the values out
    is_drive_tethered = LaunchConfiguration('is_tethered_drive')
    is_arm_tethered = LaunchConfiguration('is_tethered_arm')

    # Daedalus Drive
    daedalus_drive = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/daedalus/daedalus_drivebase.launch.py'
            ),
            launch_arguments={
                'doJoy': is_drive_tethered
            }.items(),
        )

    # Heimdall Arm Launch
    daedalus_arm = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/daedalus/daedalus_arm.launch.py'
            ),
            launch_arguments={
                'doJoy': is_arm_tethered
            }.items(),
        )

    # Computer Monitor
    computer_monitor = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/components/latte_panda_monitor.launch.py'
            )
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
            PathJoinSubstitution([FindPackageShare('camera_manager'), 'launch', 'cm_basic.launch.py'])
        )
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
    daedalus_drive_d        = RosTimer(period = 2.0, actions = [callsign_launch, daedalus_drive, computer_monitor])
    daedalus_arm_d          = RosTimer(period = 4.0, actions = [daedalus_arm, camera_manager_launch])

    # Launch each individual thing
    # launch_description.add_action(discover_server_d)
    launch_description.add_action(daedalus_drive_d)
    launch_description.add_action(daedalus_arm_d)

    return launch_description
