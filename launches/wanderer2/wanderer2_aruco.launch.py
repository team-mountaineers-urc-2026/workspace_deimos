import os
from launch import LaunchDescription
import launch
import launch_ros.actions

def generate_launch_description():

    aruco_info = launch.substitutions.LaunchConfiguration('aruco_info')
    
    launch_desc = LaunchDescription([

        launch.actions.DeclareLaunchArgument('aruco_info', default_value=[
            launch.substitutions.TextSubstitution(text=os.path.join('launches/config', '')),
            launch.substitutions.TextSubstitution(text='aruco_info'),
            launch.substitutions.TextSubstitution(text='.yaml')
        ]),

        # Launch Aruco Detect on the Right Side
        launch_ros.actions.Node(
            name='logitech07_aruco',
            package='ros2_aruco',
            executable='aruco_node',
            parameters=[aruco_info],
            namespace='logitech_07'
        ),

        # Launch Aruco Detect on the Front
        launch_ros.actions.Node(
            name='logitech08_aruco',
            package='ros2_aruco',
            executable='aruco_node',
            parameters=[aruco_info],
            namespace='logitech_08'
        ),

        # Launch Aruco Detect on the Left Side
        launch_ros.actions.Node(
            name='logitech09_aruco',
            package='ros2_aruco',
            executable='aruco_node',
            parameters=[aruco_info],
            namespace='logitech_09'
        ),

        # Launch the Aruco Server Node
        launch_ros.actions.Node(
            name='aruco_localization_node',
            package='object_localization_pkg',
            executable='aruco_localization_node',
            parameters=[
                {'global_origin_frame' : 'base_link'},
                {'subscription_topics': ['/logitech_07/aruco_markers', '/logitech_08/aruco_markers', '/logitech_09/aruco_markers']}
            ],
            namespace='object_localization'
        ),
    ])

    return launch_desc