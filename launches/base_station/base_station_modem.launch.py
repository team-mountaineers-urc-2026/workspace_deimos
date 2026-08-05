from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.conditions import LaunchConfigurationEquals

def generate_launch_description():
    launch_description = LaunchDescription()

    # launch argz
    level_arg = DeclareLaunchArgument(name = 'initial_modem_level', default_value = '0', description = 'Initial value for the modem level, a bitfield indicating which messages are and aren\'t being sent over the modem (0 is no modem, 0xFF is all modem)')
    do_modem_arg = DeclareLaunchArgument(name = 'doModem', default_value = 'false', description = 'Are you actually running the modem, or are just running the launch for the rf mux? [true, false]')
    launch_description.add_action(level_arg)
    launch_description.add_action(do_modem_arg)

    # launch nodes
    rf_mux = \
        Node(
            namespace='modem',
            package='rf_modem_pkg',
            executable='mux_basestation',
            name='mux_basestation',
            parameters= [
                {'initial_modem_level': LaunchConfiguration('initial_modem_level')}
            ]
        )
    rf_modem = \
        Node(
            # condition=LaunchConfigurationEquals('doModem', 'true'),
            namespace='modem',
            package='rf_modem_pkg',
            executable='modem_basestation',
            name='modem_basestation',
        )
    
    launch_description.add_action(rf_mux)
    launch_description.add_action(rf_modem)

    return launch_description