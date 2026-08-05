# import os
# from launch import LaunchDescription
# from launch.actions import IncludeLaunchDescription, RegisterEventHandler
# from launch.event_handlers import OnShutdown
# from launch.launch_description_sources import PythonLaunchDescriptionSource
# from launch.conditions import LaunchConfigurationEquals
# from launch.actions import ExecuteProcess, LogInfo, DeclareLaunchArgument
# from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
# from ament_index_python import get_package_share_directory
# from launch_ros.substitutions import FindPackageShare
# from launch_ros.actions import Node


# def generate_launch_description():
#     launch_description = LaunchDescription()

#     launch_description.add_action(
#         DeclareLaunchArgument(name = 'self_contained', default_value = 'true', description = 'Are you running the rover self-contained or with a basestation')#ID 3  
#     )

#     # If it is not self contained, launch the heartbeat reciever
#     launch_description.add_action(
#         Node(
#             condition=LaunchConfigurationEquals('self_contained', 'false'),
#             name='heartbeat_reciever',
#             package='comms_heartbeat_pkg',
#             executable='heartbeat_reciever',
#         ),
#     )
    
#     # If it is self-contained, launch the game controller
#     launch_description.add_action(
#         IncludeLaunchDescription(
#             PythonLaunchDescriptionSource(
#                 'launches/components/joy.launch.py'
#             ),
#             launch_arguments={
#                 'joy_config': '8bit-p',
#                 'joy_dev' : '/dev/urc/js/wanderer2_drive'
#             }.items(),
#             condition=LaunchConfigurationEquals('self_contained', 'true'),
#         ),
#     )

#     # Launch the can interface
#     launch_description.add_action(
#         IncludeLaunchDescription(
#             PythonLaunchDescriptionSource(
#                 'launches/components/can_interface.launch.py'
#                 ),
#                 launch_arguments={
#                 'current_rover': 'wanderer2'
#             }.items()
#         )
#     )
   
#     # Launch the drivebase node
#     launch_description.add_action(
#          IncludeLaunchDescription(
#             PythonLaunchDescriptionSource(
#                 PathJoinSubstitution([
#                     FindPackageShare('drivebase_control_pkg'),
#                     'launch',
#                     'drivebase_control_node.launch.py'
#                 ])
#             ),
#             launch_arguments={
#                 'isHeimdall': 'False',
#                 'self_contained' : LaunchConfiguration('self_contained')
#             }.items()
#         )
#     )
    
#     # Log info on shutdown
#     launch_description.add_action(RegisterEventHandler(
#         OnShutdown(
#             on_shutdown=[LogInfo(
#                 msg=['Launch was asked to shutdown'],
#             )]
#         )
#     )
#     ),

        
#     return launch_description

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnShutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import LaunchConfigurationEquals
from launch.actions import ExecuteProcess, LogInfo, DeclareLaunchArgument
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, TextSubstitution
from ament_index_python import get_package_share_directory
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():
    launch_description = LaunchDescription()

    # Name of the Purple Controller --> Look into changing this name
    drive_name = '8BitDo Pro 2 Wired Controller'

    # Declare Each Argument
    launch_level    = DeclareLaunchArgument(name = 'launch_level',      default_value = '',         description = 'Level at which to display the launch logs')
    heartbeat_arg   = DeclareLaunchArgument(name = 'doHeartbeat',       default_value = 'false',    description = 'Are you running teleop with the heartbeat node? [true, false]')
    joy_arg         = DeclareLaunchArgument(name = 'doJoy',             default_value = 'true',     description = 'Are you running the teleop with the joy control? [true, false]')
    can_arg         = DeclareLaunchArgument(name = 'doCan',             default_value = 'true',     description = 'Should Teleop launch the can interface node? [true, false]')
    vel_arg         = DeclareLaunchArgument(name = 'joy_vel',           default_value = 'cmd_vel',  description = 'The output topic for the command velocity [cmd_vel]')
    joy_config_arg  = DeclareLaunchArgument(name = 'joy_config',        default_value = '8bit-p',   description = 'The config file name for the controller [8bit-p, 8bit-g]')
    config_path_arg = DeclareLaunchArgument(name = 'config_filepath',   default_value = [
                                                                        TextSubstitution(text=os.path.join('launches/config', '')),
                                                                        LaunchConfiguration('joy_config'),
                                                                        TextSubstitution(text='.config.yaml')
                                                                        ],                          description='The direct filepath to the controller config file')

    # Add each argument
    launch_description.add_action(heartbeat_arg)
    launch_description.add_action(joy_arg)
    launch_description.add_action(can_arg)
    launch_description.add_action(vel_arg)
    launch_description.add_action(joy_config_arg)
    launch_description.add_action(config_path_arg)
    launch_description.add_action(launch_level)

    # Get the important values
    config_filepath = LaunchConfiguration('config_filepath')
    do_heartbeat    = LaunchConfiguration('doHeartbeat')
    joy_vel         = LaunchConfiguration('joy_vel')
    teleop_log_depth       = LaunchConfiguration('launch_level')

    # Heartbeat Reciever
    heartbeat_reciever = \
        Node(
            condition=LaunchConfigurationEquals('doHeartbeat', 'true'),
            name='heartbeat_reciever',
            package='comms_heartbeat_pkg',
            executable='heartbeat_reciever',
        )
    
    # Joy Control
    joy_node = \
        Node(
            condition=LaunchConfigurationEquals('doJoy', 'true'),
            package='joy', executable='joy_node', name='joy_node',
            parameters=[
                {
                'device_name' : drive_name,
                'deadzone': 0.3,
                'autorepeat_rate': 20.0,
                }
            ]
        )
    
    # Teleop Joy Decypherer
    teleop_node = \
        Node(
            condition=LaunchConfigurationEquals('doJoy', 'true'),
            package='teleop_twist_joy', executable='teleop_node',
            name='teleop_twist_joy_node', parameters=[config_filepath],
            remappings={('/cmd_vel', joy_vel)},
        )

    # Launch the CAN Interface
    can_interface = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/components/can_interface.launch.py'
            ),
            launch_arguments={
                'current_rover': 'wanderer2'
            }.items(),
            condition=LaunchConfigurationEquals('doCan', 'true'),
        )
   
    # Launch the drivebase node
    drivebase_node = \
         IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([
                    FindPackageShare('drivebase_control_pkg'),
                    'launch',
                    'drivebase_control_node.launch.py'
                ])
            ),
            launch_arguments={
                # 'track_width': '0.914',
                # 'wheel_radius': '0.2540',
                'isHeimdall': 'False',
                'doHeartbeat' : do_heartbeat
            }.items()
        )
    
    # Logging Outputs
    heartbeat_true = \
        LogInfo(
            condition=LaunchConfigurationEquals('doHeartbeat', 'true'),
            msg=['[wanderer2_teleop.launch.py]\t', teleop_log_depth, '\033[34m> Launching the Drive Heartbeat Node\033[0m']
        )
    
    heartbeat_false = \
        LogInfo(
            condition=LaunchConfigurationEquals('doHeartbeat', 'false'),
            msg=['[wanderer2_teleop.launch.py]\t', teleop_log_depth, '\033[93m> Drive Heartbeat Node not launching\033[0m']
        )
    
    joy_true = \
        LogInfo(
            condition=LaunchConfigurationEquals('doJoy', 'true'),
            msg=['[wanderer2_teleop.launch.py]\t', teleop_log_depth, '\033[34m> Launching the Drive Joy Node\033[0m']
        )
    
    joy_false = \
        LogInfo(
            condition=LaunchConfigurationEquals('doJoy', 'false'),
            msg=['[wanderer2_teleop.launch.py]\t', teleop_log_depth, '\033[93m> Drive Joy Node not launching\033[0m']
        )
    
    teleop_true = \
        LogInfo(
            condition=LaunchConfigurationEquals('doJoy', 'true'),
            msg=['[wanderer2_teleop.launch.py]\t', teleop_log_depth, '\033[34m> Launching the Drive Teleop Node\033[0m']
        )
    
    teleop_false = \
        LogInfo(
            condition=LaunchConfigurationEquals('doJoy', 'false'),
            msg=['[wanderer2_teleop.launch.py]\t', teleop_log_depth, '\033[93m> Drive Teleop Node not launching\033[0m']
        )
    
    can_true = \
        LogInfo(
            condition=LaunchConfigurationEquals('doCan', 'true'),
            msg=['[wanderer2_teleop.launch.py]\t', teleop_log_depth, '\033[34m> Launching the Drive CAN Interface\033[0m']
        )
    
    can_false = \
        LogInfo(
            condition=LaunchConfigurationEquals('doCan', 'false'),
            msg=['[wanderer2_teleop.launch.py]\t', teleop_log_depth, '\033[93m> Drive CAN Interface not launching\033[0m']
        )
    
    drivebase_true = \
        LogInfo(
            msg=['[wanderer2_teleop.launch.py]\t', teleop_log_depth, '\033[34m> zzLaunching the Drivebase Node\033[0m']
        )
    
    controller = \
        LogInfo(
            msg=['[wanderer2_teleop.launch.py]\t', teleop_log_depth, '\033[34m> Controller #' + drive_name +'\033[0m']
        )
    
    # Launch each individual thing
    launch_description.add_action(controller)
    launch_description.add_action(heartbeat_true)
    launch_description.add_action(heartbeat_false)
    launch_description.add_action(heartbeat_reciever)
    launch_description.add_action(joy_true)
    launch_description.add_action(joy_false)
    launch_description.add_action(joy_node)
    launch_description.add_action(teleop_true)
    launch_description.add_action(teleop_false)
    launch_description.add_action(teleop_node)
    launch_description.add_action(can_true)
    launch_description.add_action(can_false)
    launch_description.add_action(can_interface)
    launch_description.add_action(drivebase_true)
    launch_description.add_action(drivebase_node)
        
    return launch_description
