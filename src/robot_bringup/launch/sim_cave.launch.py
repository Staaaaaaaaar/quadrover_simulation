import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_robot_gazebo = get_package_share_directory('robot_gazebo')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument(
            'gui',
            default_value='false',
            description='Launch Gazebo GUI',
        ),
        DeclareLaunchArgument(
            'render_engine',
            default_value='ogre2',
            description='Gazebo rendering backend',
        ),
        DeclareLaunchArgument(
            'world',
            default_value=os.path.join(pkg_robot_gazebo, 'worlds', 'cave.sdf'),
        ),
        DeclareLaunchArgument('spawn_x', default_value='3.0'),
        DeclareLaunchArgument('spawn_y', default_value='0.0'),
        DeclareLaunchArgument('spawn_z', default_value='0.15'),
        DeclareLaunchArgument('wheel_joint_type', default_value='continuous'),
        DeclareLaunchArgument('use_diff_drive', default_value='true'),
        DeclareLaunchArgument('use_ros2_control', default_value='false'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_robot_gazebo, 'launch', 'spawn_robot_sensors.launch.py'),
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
                'wheel_joint_type': LaunchConfiguration('wheel_joint_type'),
                'use_diff_drive': LaunchConfiguration('use_diff_drive'),
                'use_ros2_control': LaunchConfiguration('use_ros2_control'),
                'use_joint_state_publisher': 'false',
            }.items(),
        ),
    ])
