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

    # ld.add_action(
    #     Node(
    #         package='usb_camera_pkg',
    #         executable='camera_node',
    #         name=f'camera_node_1',
    #         parameters=[
    #             {'device_path': '/dev/urc/cam/logitech_01'},
    #             {'frame_id': f'logitech_01'},
    #             {'img_height': 1920},
    #             {'img_width': 1080},
    #             {'pub_rate_hz': 60.0},
    #             logitech_info
    #             ],
    #         )
    #     )
    
    # ld.add_action(
    #     Node(
    #         package='image_transport',
    #         executable='republish',
    #         name='camera_node_1_republisher',
    #         arguments=['raw', 'compressed'],
    #         remappings=[
    #             ('in', 'logitech_01'),
    #             ('out/compressed', 'logitech_01/compressed')
    #         ]
    #     )
    # )

    ld.add_action(
        Node(
            package='usb_camera_pkg',
            executable='camera_node',
            name=f'camera_node_2',
            parameters=[
                {'device_path': '/dev/urc/cam/logitech_02'},
                {'frame_id': f'left_internal'},
                {'img_height': 1920},
                {'img_width': 1080},
                {'pub_rate_hz': 60.0},
                logitech_info
                ],
            )
        )

    ld.add_action(
        Node(
            package='usb_camera_pkg',
            executable='camera_node',
            name=f'camera_node_4',
            parameters=[
                {'device_path': '/dev/urc/cam/logitech_04'},
                {'frame_id': f'right_internal'},
                {'img_height': 1920},
                {'img_width': 1080},
                {'pub_rate_hz': 60.0},
                logitech_info
                ],
            )
        )
    
    # ld.add_action(
    #     Node(
    #         package='usb_camera_pkg',
    #         executable='camera_node',
    #         name=f'camera_node_3',
    #         parameters=[
    #             {'device_path': '/dev/urc/cam/logitech_03'},
    #             {'frame_id': f'logitech_03'},
    #             {'img_height': 1920},
    #             {'img_width': 1080},
    #             {'pub_rate_hz': 60.0},
    #             logitech_info
    #             ],
    #         )
    #     )
    
    # ld.add_action(
    #     Node(
    #         package='image_transport',
    #         executable='republish',
    #         name='camera_node_3_republisher',
    #         arguments=['raw', 'compressed'],
    #         remappings=[
    #             ('in', 'logitech_03'),
    #             ('out/compressed', 'logitech_03/compressed')
    #         ]
    #     )
    # )

    # ld.add_action(
    #     Node(
    #         package='usb_camera_pkg',
    #         executable='camera_node',
    #         name=f'camera_node_6',
    #         parameters=[
    #             {'device_path': '/dev/urc/cam/logitech_06'},
    #             {'frame_id': f'logitech_06'},
    #             {'img_height': 1920},
    #             {'img_width': 1080},
    #             {'pub_rate_hz': 60.0},
    #             logitech_info
    #             ],
    #         )
    #     )
    
    # ld.add_action(
    #     Node(
    #         package='image_transport',
    #         executable='republish',
    #         name='camera_node_6_republisher',
    #         arguments=['raw', 'compressed'],
    #         remappings=[
    #             ('in', 'logitech_06'),
    #             ('out/compressed', 'logitech_06/compressed')
    #         ]
    #     )
    # )

    # ld.add_action(
    #     Node(
    #         package='usb_camera_pkg',
    #         executable='camera_node',
    #         name=f'camera_node_5',
    #         parameters=[
    #             {'device_path': '/dev/urc/cam/logitech_05'},
    #             {'frame_id': f'logitech_05'},
    #             {'img_height': 1920},
    #             {'img_width': 1080},
    #             {'pub_rate_hz': 60.0},
    #             logitech_info
    #             ],
    #         )
    #     )
    
    # ld.add_action(
    #     Node(
    #         package='image_transport',
    #         executable='republish',
    #         name='camera_node_5_republisher',
    #         arguments=['raw', 'compressed'],
    #         remappings=[
    #             ('in', 'logitech_05'),
    #             ('out/compressed', 'logitech_05/compressed')
    #         ]
    #     )
    # )
    
    return ld
