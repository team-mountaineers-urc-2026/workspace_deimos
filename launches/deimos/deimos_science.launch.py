import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, TextSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch.conditions import LaunchConfigurationEquals

def generate_launch_description():
    launch_description = LaunchDescription()


    # Launch Arguments
    drive_joy_config_arg  = DeclareLaunchArgument(name = 'drive_joy_config',        default_value = 'xbox',   description = 'The config file name for the controller [8bit-p-drive, 8bit-g-drive]')
    drive_config_path_arg = DeclareLaunchArgument(name = 'drive_config_filepath',   default_value = [
                                                                        TextSubstitution(text=os.path.join('launches/config', '')),
                                                                        LaunchConfiguration('drive_joy_config'),
                                                                        TextSubstitution(text='.config.yaml')
                                                                        ],                          description='The direct filepath to the controller config file')


    # Get Value
    drive_config_filepath = LaunchConfiguration('drive_config_filepath')

    # Launch Arguments
    arm_joy_config_arg  = DeclareLaunchArgument(name = 'arm_joy_config',        default_value = '8bit-s-arm-science',   description = 'The config file name for the controller [8bit-p-arm, 8bit-g-arm]')
    joy_arg                 = DeclareLaunchArgument(name = 'doJoy',             default_value = 'true',     description = 'Are you running the teleop with the joy control? [true, false]')
    ik_arg                  = DeclareLaunchArgument(name = 'doIK',              default_value = 'false',    description = 'Are we running with inverse kinematic control? [true, false]')
    arm_config_path_arg = DeclareLaunchArgument(name = 'arm_config_filepath',   default_value = [
                                                                        TextSubstitution(text=os.path.join('launches/config', '')),
                                                                        LaunchConfiguration('arm_joy_config'),
                                                                        TextSubstitution(text='.config.yaml')
                                                                        ],                          description='The direct filepath to the controller config file')
    
    launch_description.add_action(drive_joy_config_arg)
    launch_description.add_action(drive_config_path_arg)
    launch_description.add_action(joy_arg)
    launch_description.add_action(ik_arg)
    launch_description.add_action(arm_joy_config_arg)
    launch_description.add_action(arm_config_path_arg)


    arm_config_filepath = LaunchConfiguration('arm_config_filepath')
    do_joy_arg = LaunchConfiguration('doJoy')




#####################################
##          Arm Control            ##
#####################################

    science_arm = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/deimos/deimos_science_arm.launch.py'
            ),
            launch_arguments={
                'doJoy': do_joy_arg,
                'joy_config': '8bit-s-arm-science',
                'config_filepath': arm_config_filepath,
            }.items(),
        )



#####################################
##         Drive Control           ##
#####################################

    deimos_drive = \
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                'launches/deimos/deimos_drive.launch.py'
            ),
            launch_arguments={
                'doJoy': do_joy_arg,
                'joy_config': 'xbox',
                'config_filepath': drive_config_filepath,
            }.items(),
        )



    

#####################################
##        Science Devices          ##
#####################################


    # Pico Science Node
    pico_science = \
        Node(
            namespace='science',
            package='pico_interface_pkg',
            executable='pico_science_node'
        )
    
    # Pico Science Node
    qtpy_science = \
        Node(
            namespace='science',
            package='pico_interface_pkg',
            executable='qtpy_science_node'
        )

    # Spectrometer Node
    spectrometer = \
        Node(
            namespace='',
            package='deimos_science',
            executable='spectrometer'
        )
    
     # Calibrate Spectrometer Node
    # spectrometer = \
    #     Node(
    #         namespace='',
    #         package='deimos_science',
    #         executable='spectro_calibrate'
    #     )



    # Led Interface
    led_interface = \
        Node(
            namespace='autonomy',
            package='autonomy_led_pkg',
            executable='autonomy_led_subscriber',
            name='led_interface'
        )

    # Dynamixel Interface
    dynamixel_interface = \
        Node(
            namespace='science',
            package='deimos_science',
            executable='dynamixel_interface'
	)

    # Dynamixel Interface
    gimbal_cam = \
        Node(
            namespace='science',
            package='deimos_science',
            executable='gimbal_control'
	)

    panorama_node = \
        Node(
            namespace='science',
            package='deimos_pano',
            executable='panorama',
            name='pano_subscriber',
            output='screen',
            parameters=[{
                'pano_cam_id': '39',
                'base_ips': ['192.168.1.64', '192.168.1.65'],
                'base_user': 'lenovo',
                'target_width': 800,
                'target_height': 800
            }]
        )


    # camera_manager autonomy launch
    camera_manager_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('camera_manager'), 'launch', 'cm_basic.launch.py'])
        )
    )
    
    # Comms Monitor
    comms_monitor = \
        Node(
            namespace='health_monitor',
            package='health_monitor_pkg',
            executable='comms_monitor'
        )


    # Arm Launch Descriptions
    launch_description.add_action(science_arm)

    # Drive Launch Descriptions
    launch_description.add_action(deimos_drive)

    # Science Devices
    launch_description.add_action(led_interface)
    launch_description.add_action(spectrometer)
    launch_description.add_action(pico_science)
    launch_description.add_action(qtpy_science)
    launch_description.add_action(panorama_node)
    # launch_description.add_action(gimbal_cam)
    launch_description.add_action(dynamixel_interface)
    launch_description.add_action(camera_manager_launch)
    launch_description.add_action(comms_monitor)

    return launch_description
