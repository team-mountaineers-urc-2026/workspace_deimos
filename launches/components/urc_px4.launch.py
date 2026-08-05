import os
from launch import LaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription, ExecuteProcess, DeclareLaunchArgument
from launch_ros.actions import Node, RosTimer
from launch_ros.substitutions import FindPackageShare
import launch_ros
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterFile

def generate_launch_description():

    ld = LaunchDescription()

    # Arguments
    ld.add_action(DeclareLaunchArgument('fcu_url',            default_value='/dev/urc/mtc/pixhawk'))
    ld.add_action(DeclareLaunchArgument('gcs_url',            default_value=''))
    ld.add_action(DeclareLaunchArgument('tgt_system',         default_value='1'))
    ld.add_action(DeclareLaunchArgument('tgt_component',      default_value='1'))
    ld.add_action(DeclareLaunchArgument('pluginlists_yaml',   default_value=PathJoinSubstitution([FindPackageShare('mavros'), 'launch', 'px4_pluginlists.yaml'])))
    ld.add_action(DeclareLaunchArgument('config_yaml',        default_value='./launches/config/urc_px4_config.yaml'))
    ld.add_action(DeclareLaunchArgument('log_output',         default_value='log'))
    ld.add_action(DeclareLaunchArgument('fcu_protocol',       default_value='v2.0'))
    ld.add_action(DeclareLaunchArgument('respawn_mavros',     default_value='false'))
    ld.add_action(DeclareLaunchArgument('namespace',          default_value='mavros'))

    fcu_url          = LaunchConfiguration('fcu_url')
    gcs_url          = LaunchConfiguration('gcs_url')
    tgt_system       = LaunchConfiguration('tgt_system')
    tgt_component    = LaunchConfiguration('tgt_component')
    pluginlists_yaml = LaunchConfiguration('pluginlists_yaml')
    config_yaml      = LaunchConfiguration('config_yaml')
    log_output       = LaunchConfiguration('log_output')
    fcu_protocol     = LaunchConfiguration('fcu_protocol')
    respawn_mavros   = LaunchConfiguration('respawn_mavros')
    namespace        = LaunchConfiguration('namespace')

    mavros_node = \
        Node(
            package='mavros',
            executable='mavros_node',
            namespace=namespace,
            parameters=[
                {'fcu_url' : fcu_url},
                {'gcs_url' : gcs_url},
                {'tgt_system' : tgt_system},
                {'tgt_component' : tgt_component},
                {'fcu_protocol' : fcu_protocol},
                ParameterFile(pluginlists_yaml, allow_substs=True),
                ParameterFile(config_yaml, allow_substs=True)
            ],
            output={'both' : 'log'},
        )

    ld.add_action(mavros_node)

    return ld