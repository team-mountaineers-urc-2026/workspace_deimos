from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    launch_description = LaunchDescription()

    callsign_arg  = DeclareLaunchArgument(name = 'callsign',        default_value = 'W8CUL',   description = 'The Callsign for West Virginia University')
    period_arg    = DeclareLaunchArgument(name = 'callsign_period', default_value = '300',     description = 'The Callsign publish period in seconds [netcat will try for 10 seconds regardless]')

    launch_description.add_action(callsign_arg)
    launch_description.add_action(period_arg)

    callsign_broadcast = \
        ExecuteProcess(
            cmd=[['echo "\n\033[31mARE YOU ', LaunchConfiguration('callsign'),'? IF NOT CHANGE THE LAUNCH ARGUMENT !!!!\033[0m\n"; while true; do echo "CALLSIGN: ', LaunchConfiguration('callsign'), '" | nc -u -b 192.168.1.255 5000 -q 10; sleep ', LaunchConfiguration('callsign_period'), '; done']],
            shell=True,
            output='screen'
        )
    
    launch_description.add_action(callsign_broadcast)

    return launch_description