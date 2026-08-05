import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, TextSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node, RosTimer
from launch.conditions import LaunchConfigurationEquals

def generate_launch_description():
    launch_description = LaunchDescription()

    # Waypoint Manager
    waypoint_manager = \
        Node(
            namespace='autonomy',
            package='autonomy_2025',
            executable='waypoint_manager',
            name='waypoint_manager'
        )

    # Brian Node
    brian = \
        Node(
            namespace='autonomy',
            package='autonomy_2025',
            executable='brian',
            name='brian'
        )

    # Local Path Planner
    local_path_planner = \
        Node(
            namespace='autonomy',
            package='autonomy_2025',
            executable='local_path_planner',
            name='local_path_planner'
        )
    
    # Pose Controller Mux
    pose_controller_mux = \
        Node(
            namespace='autonomy',
            package='autonomy_2025',
            executable='control_mux',
            name='pose_mux'
        )
    
    # P2P vel controller
    static_p2p_vel = \
        Node(
            namespace='autonomy',
            package='autonomy_2025',
            executable='static_p2p',
            name='static_p2p'
        )
    
    # P2P vel controller
    pid_planner_node = \
        Node(
            namespace='autonomy',
            package='autonomy_2025',
            executable='pid_planner_node',
            name='pid_node'
        )
    
    # Led Interface
    led_interface = \
        Node(
            namespace='autonomy',
            package='autonomy_led_pkg',
            executable='autonomy_led_subscriber',
            name='led_interface',
            parameters=[{'device_path' : '/dev/urc/mc/co_processor'}]
        )

    # Position Localizer
    position_localizer = \
        Node(
            namespace='autonomy',
            package='autonomy_2025',
            executable='pose_localizer',
            name='position_localizer'
        )
    
    # Camera Info Autonomy Cameras
    camera_info = \
        Node(
            namespace='autonomy',
            package='autonomy_2025',
            executable='camera_info',
            name='camera_info'
        )

    # camera_manager autonomy launch
    camera_manager_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('camera_manager'), 'launch', 'cm_autonomy.launch.py'])
        )
    )

    # Aruco Detect
    aruco_detect = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            'launches/components/daedalus_aruco.launch.py'
        )
    )

    # Tf Tree
    static_tf = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            'launches/components/daedalus_static_tf.launch.py'
        )
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

    # Daedalus Drivebase
    daedalus_drivebase = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/daedalus/daedalus_drivebase.launch.py'
            ),
            launch_arguments={
                'doJoy': "false"
            }.items(),
        )
    

    task_0 = RosTimer(period = 0.0, actions = [callsign_launch, led_interface, static_tf, camera_info])
    task_1 = RosTimer(period = 2.0, actions = [daedalus_drivebase, camera_manager_launch, waypoint_manager])
    task_2 = RosTimer(period = 4.0, actions = [brian, local_path_planner, pose_controller_mux, static_p2p_vel])
    task_3 = RosTimer(period = 6.0, actions = [pid_planner_node, position_localizer, aruco_detect])


    launch_description.add_action(task_0)
    launch_description.add_action(task_1)
    launch_description.add_action(task_2)
    launch_description.add_action(task_3)

    return launch_description
