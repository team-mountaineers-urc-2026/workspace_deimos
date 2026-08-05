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

        # # Launch Aruco Detect for specifc camera
        # launch_ros.actions.Node(
        #     name='logitech22_aruco',
        #     package='ros2_aruco',
        #     executable='aruco_node',
        #     parameters=["test_level"],
        #     namespace='logitech_22'
        # ),

        # # Launch Mastcam Front 
        launch_ros.actions.Node(
            name='logitech27_aruco',
            package='ros2_aruco',
            executable='aruco_node',
            parameters=["test_level"],
            namespace='logitech_27',
            remappings={('/camera_info', '/logitech_27/camera_info')},
        ),

    #     # # Launch Mastcam Back 
    #     launch_ros.actions.Node(
    #         name='logitech29_aruco',
    #         package='ros2_aruco',
    #         executable='aruco_node',
    #         parameters=["test_level"],
    #         namespace='logitech_29'
    #     ),
       
    #    # # Launch Mastcam Left
    #    launch_ros.actions.Node(
    #         name='logitech28_aruco',
    #         package='ros2_aruco',
    #         executable='aruco_node',
    #         parameters=["test_level"],
    #         namespace='logitech_28'
    #     ),
       
    #    # # Launch Mastcam Right 
    #    launch_ros.actions.Node(
    #         name='logitech30_aruco',
    #         package='ros2_aruco',
    #         executable='aruco_node',
    #         parameters=["test_level"],
    #         namespace='logitech_30'
    #     )
       
       
        # # Launch the Aruco Server Node
        # launch_ros.actions.Node(
        #     name='aruco_localization_node',
        #     package='object_localization_pkg',
        #     executable='aruco_localization_node',
        #     parameters=[
        #         {'global_origin_frame' : 'base_link'}
        #     ],
        #     namespace='object_localization'
        # ),
    ])

    return launch_desc
