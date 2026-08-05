import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, TextSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch.conditions import LaunchConfigurationEquals

def generate_launch_description():
    launch_description = LaunchDescription()

    SHOULDER_ID = 0x14A
    ELBOW_ID = 0x145
    WRIST_PITCH_ID = 0x148
    WRIST_ROLL_ID = 0x149
    RAIL_ID = 0x147
    GRIPPER_ID = 0x14C
    

    # Name of the Purple Controller --> Look into changing this name
    arm_controller = '/dev/urc/js/daedalus_arm'


    # Launch Arguments
    joy_config_arg  = DeclareLaunchArgument(name = 'joy_config',        default_value = '8bit-s-arm',   description = 'The config file name for the controller [8bit-p-arm, 8bit-g-arm]')
    joy_arg         = DeclareLaunchArgument(name = 'doJoy',             default_value = 'true',     description = 'Are you running the teleop with the joy control? [true, false]')
    ik_arg          = DeclareLaunchArgument(name = 'doIK',              default_value = 'false',    description = 'Are we running with inverse kinematic control? [true, false]')
    config_path_arg = DeclareLaunchArgument(name = 'config_filepath',   default_value = [
                                                                        TextSubstitution(text=os.path.join('launches/config', '')),
                                                                        LaunchConfiguration('joy_config'),
                                                                        TextSubstitution(text='.config.yaml')
                                                                        ],                          description='The direct filepath to the controller config file')

    launch_description.add_action(joy_config_arg)
    launch_description.add_action(joy_arg)
    launch_description.add_action(ik_arg)
    launch_description.add_action(config_path_arg)


    # Get Value
    config_filepath = LaunchConfiguration('config_filepath')

    joy_mux = \
        Node(
            namespace='manipulator',
            package='controls_pkg',
            executable='joy_mux',
            name='joy_mux_node'
        )

    # Launch the CAN Interface
    can_interface = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/components/can_interface.launch.py'
            ),
            launch_arguments={
                'current_rover': 'daedalus',
                'can_network_id' : 'can3'
            }.items(),
        )

    # Arm Control Launch File
    manipulator = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([
                    FindPackageShare('controls_pkg'),
                    'launch',
                    'manipulator.launch.py'
                ]),
            ),
            launch_arguments={
                'shoulder_id': str(SHOULDER_ID),
                'elbow_id': str(ELBOW_ID),
                'wrist_pitch_id': str(WRIST_PITCH_ID),
                'wrist_roll_id' : str(WRIST_ROLL_ID),
                'rail_id' : str(RAIL_ID),
                'gripper_id' : str(GRIPPER_ID),
                'joy_config' : config_filepath,
                'can_network_id' : 'can3'
            }.items(),
            condition = LaunchConfigurationEquals('doIK', 'false'),
        )

    # Joint Control
    joint_control = \
        Node(
            package='controls_pkg',
            executable='joint_control',
            name='joint_control_node',
            namespace='manipulator',
            parameters=[config_filepath]
        )

    # IK Control
    # ik_control = \
    #     Node(
    #         package='controls_pkg',
    #         executable='ik_control',
    #         name='ik_control_node',
    #         namespace='manipulator'
    #     )

    # Arm Zeroing
    zeroing = \
        Node(
            package='controls_pkg',
            executable='arm_zeroing',
            name='arm_zeroing_node',
            namespace='manipulator'
        )

    # Arm Monitor
    arm_monitor = \
        Node(
            package='health_monitor_pkg',
            executable='arm_monitor',
            name='arm_monitor_node',
            namespace='manipulator',
            parameters=[
                {
                    'shoulder_id': SHOULDER_ID,
                    'elbow_id': ELBOW_ID,
                    'wrist_pitch_id': WRIST_PITCH_ID,
                    'wrist_roll_id' : WRIST_ROLL_ID,
                    'rail_id' : RAIL_ID,
                    'grippper_id' : GRIPPER_ID,
                    'timeout_period' : 0.5,
                    'can_network_id' : 'can3'
                }
            ]
        )
    
    #Pico communication node
    pico_node = \
        Node(
            namespace='manipulator',
            package='pico_interface_pkg',
            executable='pico_arm_node',
            name='pico_arm_node_0',
            parameters=[{'pico_path': '/dev/urc/mc/pi_pico'}]  
        )

    # Led Interface
    led_interface = \
        Node(
            namespace='autonomy',
            package='autonomy_2025',
            executable='led_interface',
            name='led_interface'
        )
    #yolo and distance est node
    yolo_node = \
        Node(
            namespace='autonomy',
            package='eris_planning',
            executable='motion_planner',
            name='motion_planner'
        )

    launch_description.add_action(joy_mux)
    launch_description.add_action(can_interface)
    #launch_description.add_action(zeroing)
    launch_description.add_action(joint_control)
    # launch_description.add_action(ik_control)
    launch_description.add_action(manipulator)
    launch_description.add_action(yolo_node)
    #launch_description.add_action(arm_monitor)
    #launch_description.add_action(pico_node)
    #launch_description.add_action(led_interface)

    return launch_description
