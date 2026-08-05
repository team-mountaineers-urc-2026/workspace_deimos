# Copyright 2018 Lucas Walter
# All rights reserved.
#
# Software License Agreement (BSD License 2.0)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Lucas Walter nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import argparse
import os
from pathlib import Path  # noqa: E402
import sys

# Hack to get relative import of .camera_config file working
# dir_path = os.path.__file__
# sys.path.append(dir_path)
# 
from launch import LaunchDescription  # noqa: E402
from launch.actions import DeclareLaunchArgument  # noqa: E402
from launch_ros.actions import Node, RosTimer  # noqa: E402
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import TextSubstitution, LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    ld = LaunchDescription()

    camera_name_arg = DeclareLaunchArgument('camera_name', default_value=TextSubstitution(text='logitech_00'), description='Camera Name Value')
    param_file_arg  = DeclareLaunchArgument('param_file', default_value=TextSubstitution(text='params_1.yaml'), description='The Parameter file to be launched with')

    ld.add_action(camera_name_arg)
    ld.add_action(param_file_arg)

    param_path = PathJoinSubstitution([TextSubstitution(text=os.path.normpath(os.path.join(os.path.abspath(__file__), '../..'))), "config", LaunchConfiguration('param_file')])

    camera_node = \
        Node(
            package='usb_cam', executable='usb_cam_node_exe', output='screen',
            name=LaunchConfiguration('camera_name'),
            parameters= [param_path,
                        {'video_device' : ['/dev/urc/cam/',LaunchConfiguration('camera_name')]},
                        {'camera_parameters_url': param_path}],
            remappings = [
                ('image_raw', [LaunchConfiguration('camera_name'), '/image_raw']),
                ('image_raw/compressed', [LaunchConfiguration('camera_name'), '/image_compressed']),
                ('image_raw/compressedDepth', [LaunchConfiguration('camera_name'), '/compressedDepth']),
                ('image_raw/theora', [LaunchConfiguration('camera_name'), '/image_raw/theora']),
                ('camera_info', [LaunchConfiguration('camera_name'), '/camera_info']),
            ]
        )
    
    mux_node = \
        Node(
            package='theora_mux', executable='theora_mux_node', output='screen',
            name=[LaunchConfiguration('camera_name'), '_mux'],
            parameters= [
                {'theora_input' : [LaunchConfiguration('camera_name'), '/image_raw/theora']},
                {'theora_output' : [LaunchConfiguration('camera_name'), '/image_raw/theora_mux']},
                {'theora_service' : [LaunchConfiguration('camera_name'), '_mux/recall_header']}],
        )

    ld.add_action(camera_node)
    ld.add_action(mux_node)
    return ld
