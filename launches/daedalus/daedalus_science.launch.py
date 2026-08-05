import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, TextSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node, RosTimer
from launch.conditions import LaunchConfigurationEquals

DRILL_ID = 0x145

def generate_launch_description():
    launch_description = LaunchDescription()

    drive_tethered_arg      = DeclareLaunchArgument(name = 'is_tethered_drive', default_value = 'true',  description = 'Is the drive controllers plugged in to daedalus? [\'true\', \'false\']')
    launch_description.add_action(drive_tethered_arg)

    # Get the values out
    is_drive_tethered = LaunchConfiguration('is_tethered_drive')

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
    
    # Computer Monitor
    computer_monitor = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/components/latte_panda_monitor.launch.py'
            )
        ) 

    # Science Drill
    drill_motor = \
        Node(
            namespace="science/drill", 
            package='controls_pkg',
            executable='motor',
            parameters=[
                {'arbitration_id': DRILL_ID},
                {'can_network_id': 'can2'}]  
        )
    
    # Callsign stuff
    callsign_launch = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/components/callsign.launch.py'
            ),
            launch_arguments={
                'callsign': 'KD3BCH'
            }.items(),
        )

    # Pico Control Node
    pico_science_node = \
        Node(
            namespace='science',
            package='pico_interface_pkg',
            executable='pico_science_node',
            name='pico_science_node_0',
            parameters=[{'pico_path': '/dev/urc/mc/pi_pico'}]  
        )

    # Dynamixel Control Node
    dynamixel_interface = \
        Node(
            namespace="science",
            package='daedalus_science',
            executable='dynamixel_interface',
            name='dynamixel_interface_node',
            parameters=[{'u2d2_portd' : '/dev/urc/mtc/sci_u2d2'}]
        )

    # Spectrometer Node
    spectrometer = \
        Node(
            namespace='science',
            package='daedalus_science',
            executable='spectrometer'
        )

    # Camera Manager Node
    camera_manager = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([
                    FindPackageShare('camera_manager'),
                    'launch',
                    'cm_science.launch.py'
                ]),
            )
        )

    # Panorama Node
    panorama = \
        Node(
            namespace="science",
            package='daedalus_pano',
            executable='panorama',
            name='panorama_node',
            parameters=[{'pano_cam_id' : 22}]
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
    
    # Science ping motor status
    drill_ping = \
        ExecuteProcess(
            cmd=[['ros2 topic pub /science/drill/send/status1 controls_msgs/msg/ReadMotorStatus1MsgSentParams "{}"']],
            shell=True,
            output='log'
        )

    

    # Set up timers for each launch
    # group_0 = RosTimer(period = 0.0, actions = [discovery_launch])
    group_1 = RosTimer(period = 2.0, actions = [callsign_launch, daedalus_drive, drill_motor, drill_ping])
    group_2 = RosTimer(period = 4.0, actions = [computer_monitor, camera_manager, panorama])
    group_3 = RosTimer(period = 4.0, actions = [pico_science_node, dynamixel_interface, spectrometer])

    # launch_description.add_action(group_0)
    launch_description.add_action(group_1)
    launch_description.add_action(group_2)
    launch_description.add_action(group_3)

    return launch_description
