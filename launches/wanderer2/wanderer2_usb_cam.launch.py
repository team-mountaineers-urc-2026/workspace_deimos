from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import TextSubstitution, LaunchConfiguration
import os


def generate_launch_description():

    logitech_info = LaunchConfiguration('logitech_info')


    ld = LaunchDescription()

    ld.add_action(
        DeclareLaunchArgument('logitech_info', default_value=[
            TextSubstitution(text=os.path.normpath(os.path.join(os.path.abspath(__file__), '../../config'))),
            TextSubstitution(text='/logitech_info'),
            TextSubstitution(text='.yaml')
        ])
    )

    # This file launches the following cameras
    # Camera    Compression?
    # 7         Y
    # 8         Y
    # 9         Y


    # Launch Logitech 07 w/ compression
    ld.add_action(
        Node(
            package='usb_camera_pkg',
            executable='camera_node',
            name=f'camera_node_7',
            parameters=[
                {'device_path': '/dev/urc/cam/logitech_07'},
                {'frame_id': f'right_side'},
                {'img_height': 1920},
                {'img_width': 1080},
                {'pub_rate_hz': 60.0},
                logitech_info
                ],
            )
        )
    
    ld.add_action(
        Node(
            package='image_transport',
            executable='republish',
            name='camera_node_7_republisher',
            arguments=['raw', 'compressed'],
            remappings=[
                ('in', 'logitech_07/image_raw'),
                ('out/compressed', 'logitech_07/compressed')
            ],
        )
    )

    # Launch Logitech 08 w/ compression
    ld.add_action(
        Node(
            package='usb_camera_pkg',
            executable='camera_node',
            name=f'camera_node_8',
            parameters=[
                {'device_path': '/dev/urc/cam/logitech_08'},
                {'frame_id': f'front'},
                {'img_height': 640},
                {'img_width': 480},
                {'pub_rate_hz': 60.0},
                logitech_info
                ],
            )
        )
    
    ld.add_action(
        Node(
            package='image_transport',
            executable='republish',
            name='camera_node_8_republisher',
            arguments=['raw', 'compressed'],
            remappings=[
                ('in', 'logitech_08/image_raw'),
                ('out/compressed', 'logitech_08/compressed')
            ]
        )
    )

    # Launch Logitech 09 w/ compression
    ld.add_action(
        Node(
            package='usb_camera_pkg',
            executable='camera_node',
            name=f'camera_node_9',
            parameters=[
                {'device_path': '/dev/urc/cam/logitech_09'},
                {'frame_id': f'left_side'},
                {'img_height': 1920},
                {'img_width': 1080},
                {'pub_rate_hz': 60.0},
                logitech_info
                ],
            )
        )
    
    ld.add_action(
        Node(
            package='image_transport',
            executable='republish',
            name='camera_node_9_republisher',
            arguments=['raw', 'compressed'],
            remappings=[
                ('in', 'logitech_09/image_raw'),
                ('out/compressed', 'logitech_09/compressed')
            ]
        )
    )

    return ld
