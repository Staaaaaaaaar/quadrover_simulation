import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_quadrover_gazebo = get_package_share_directory('quadrover_gazebo')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('rviz', default_value='false'),
        DeclareLaunchArgument(
            'gui',
            default_value='false',
            description='Launch Gazebo GUI',
        ),
        DeclareLaunchArgument(
            'render_engine',
            default_value='ogre2',
        ),
        DeclareLaunchArgument(
            'world',
            default_value=os.path.join(pkg_quadrover_gazebo, 'worlds', 'example.sdf'),
        ),
        DeclareLaunchArgument('spawn_x', default_value='0.0'),
        DeclareLaunchArgument('spawn_y', default_value='0.0'),
        DeclareLaunchArgument('spawn_z', default_value='0.23'),
        DeclareLaunchArgument('drive_mode', default_value='diff_drive'),
        DeclareLaunchArgument('publish_wheel_odom_tf', default_value='false'),
        DeclareLaunchArgument('wheel_odom_frame_id', default_value='odom'),
        DeclareLaunchArgument('wheel_base_frame_id', default_value='base_link'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_quadrover_gazebo, 'launch', 'spawn_quadrover_sensors.launch.py'),
            ),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'world': LaunchConfiguration('world'),
                'rviz': LaunchConfiguration('rviz'),
                'gui': LaunchConfiguration('gui'),
                'render_engine': LaunchConfiguration('render_engine'),
                'spawn_x': LaunchConfiguration('spawn_x'),
                'spawn_y': LaunchConfiguration('spawn_y'),
                'spawn_z': LaunchConfiguration('spawn_z'),
                'drive_mode': LaunchConfiguration('drive_mode'),
                'publish_wheel_odom_tf': LaunchConfiguration('publish_wheel_odom_tf'),
                'wheel_odom_frame_id': LaunchConfiguration('wheel_odom_frame_id'),
                'wheel_base_frame_id': LaunchConfiguration('wheel_base_frame_id'),
            }.items(),
        ),
    ])
