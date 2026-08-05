from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    launch_description = LaunchDescription()

    server_ip = DeclareLaunchArgument(name = 'server_ip',        default_value = '192.168.1.69',   description = 'The IP address of the Discovery Server')

    launch_description.add_action(server_ip)

    ds_launch = \
        ExecuteProcess(
            cmd=[['fastdds discovery -i 0 -t ', LaunchConfiguration('server_ip'), ' -p 11811']],
            shell=True,
            output='screen'
        )
    
    launch_description.add_action(ds_launch)

    return launch_description