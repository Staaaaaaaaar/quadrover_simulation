import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('four_wheel_localization')
    config = os.path.join(pkg, 'config', 'wheel_only.yaml')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument(
            'fusion_mode',
            default_value='wheel_only',
            description='Fusion method: wheel_only (future: ekf_wheel_imu, etc.)',
        ),
        Node(
            package='four_wheel_localization',
            executable='odom_relay.py',
            name='odom_relay',
            output='screen',
            parameters=[
                config,
                {'use_sim_time': LaunchConfiguration('use_sim_time')},
            ],
        ),
    ])
