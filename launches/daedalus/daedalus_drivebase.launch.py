import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, TextSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from launch.conditions import LaunchConfigurationEquals
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

def generate_launch_description():
    launch_description = LaunchDescription()

    FRONT_LEFT_ID = 0x141
    FRONT_RIGHT_ID = 0x143

    BACK_LEFT_ID = 0x142
    BACK_RIGHT_ID = 0x144

    drive_controller = '/dev/urc/js/daedalus_drive'

    # Launch Arguments
    joy_config_arg  = DeclareLaunchArgument(name = 'joy_config',        default_value = 'xbox',   description = 'The config file name for the controller [8bit-p-drive, 8bit-g-drive]')
    joy_arg         = DeclareLaunchArgument(name = 'doJoy',             default_value = 'true',     description = 'Are you running the teleop with the joy control? [true, false]')
    config_path_arg = DeclareLaunchArgument(name = 'config_filepath',   default_value = [
                                                                        TextSubstitution(text=os.path.join('launches/config', '')),
                                                                        LaunchConfiguration('joy_config'),
                                                                        TextSubstitution(text='.config.yaml')
                                                                        ],                          description='The direct filepath to the controller config file')

    launch_description.add_action(joy_config_arg)
    launch_description.add_action(joy_arg)
    launch_description.add_action(config_path_arg)

    # Get Value
    config_filepath = LaunchConfiguration('config_filepath')
    print(os.path.join('launches/config', ''))

    # Launch the Joystick
    # Joy Control
    joy_node = \
        Node(
            condition=LaunchConfigurationEquals('doJoy', 'true'),
            namespace='base_station',
            package='joy_controller',
            executable='JoyController',
            name='joy_node',
            parameters=[
                {
                'device' : drive_controller,
                'deadzone': 0.3,
                'JC_publish_rate': 20,
                }
            ]
        )
    
    # Teleop Joy Decypherer
    teleop_node = \
        Node(
            namespace='base_station',
            condition=LaunchConfigurationEquals('doJoy', 'true'),
            package='teleop_twist_joy',
            executable='teleop_node',
            name='teleop_twist_joy_node',
            parameters=[config_filepath]
            # remappings={('/cmd_vel', joy_vel)},
        )

    # CAN Interface
    can_interface = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/components/can_interface.launch.py'
            ),
            launch_arguments={
                'current_rover': 'daedalus',
                'can_network_id' : 'can2'
            }.items(),
        )

    # Drivetrain
    drivetrain = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([
                    FindPackageShare('controls_pkg'),
                    'launch',
                    'drivetrain.launch.py'
                ]),
            ),
            launch_arguments={
                'front_left_id': str(FRONT_LEFT_ID),
                'front_right_id': str(FRONT_RIGHT_ID),
                'back_left_id': str(BACK_LEFT_ID),
                'back_right_id' : str(BACK_RIGHT_ID),
                'can_network_id' : 'can2'
            }.items()
        )

    # Chassis Monitor
    chassis_monitor = \
        Node(
            namespace='health_monitor',
            package='health_monitor_pkg',
            executable='chassis_monitor',
            name='chassis_monitor_node',
            parameters=[
                {
                    'front_left_id' : FRONT_LEFT_ID,
                    'front_right_id' : FRONT_RIGHT_ID,
                    'back_left_id' : BACK_LEFT_ID,
                    'back_right_id' : BACK_RIGHT_ID,
                    'timeout_period' : 0.5,
                    'can_network_id' : 'can2'
                }
            ]
        )

    # Velocity Mux
    velocity_mux = \
        Node(
            namespace='drivetrain',
            package='autonomy_2025',
            executable='velocity_mux',
            name='vel_mux'
        )
    
    # Mavros
    mavros = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource('./launches/components/urc_px4.launch.py'),
            launch_arguments={
                'fcu_url': '/dev/urc/mtc/pixhawk',
                'config_yaml': './launches/config/urc_px4_config.yaml',
            }.items()
        )
    
    # Gimbal
    gimbal = \
        Node(
            namespace='drivetrain',
            package='daedalus_science',
            executable='gimbal_control',
            name='gimbal_control_node',
            parameters=[{'u2d2_port' : '/dev/urc/mtc/gimbal_u2d2'}]
        )

    launch_description.add_action(joy_node)
    launch_description.add_action(teleop_node)
    launch_description.add_action(can_interface)
    launch_description.add_action(drivetrain)
    launch_description.add_action(chassis_monitor)
    launch_description.add_action(velocity_mux)
    launch_description.add_action(mavros)
    launch_description.add_action(gimbal)

    return launch_description
