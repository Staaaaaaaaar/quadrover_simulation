import json
import os
import re

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    SetEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def _bridge_arguments(drive_mode):
    args = [
        '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        '/loc/gazebo@nav_msgs/msg/Odometry[gz.msgs.Odometry',
        '/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU',
        '/lidar/scan/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
        '/camera/color/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
        '/camera/color/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
        '/camera/depth/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
        '/camera/depth/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
        '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
        '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
    ]
    if drive_mode == 'mecanum_drive':
        # Fortress mecanum drive publishes OdometryWithCovariance on this topic.
        args.append(
            '/model/quadrover/odometry_with_covariance@nav_msgs/msg/Odometry[gz.msgs.OdometryWithCovariance'
        )
    else:
        args.append('/odom/wheel@nav_msgs/msg/Odometry[gz.msgs.Odometry')
    return args


def _read_world_name(world_path):
    with open(world_path, encoding='utf-8') as world_file:
        content = world_file.read()
    match = re.search(r'<world\s+name="([^"]+)"', content)
    if match:
        return match.group(1)
    return 'default'


def _load_drive_mode_profiles():
    pkg_quadrover_control = get_package_share_directory('quadrover_control')
    profile_path = os.path.join(pkg_quadrover_control, 'config', 'drive_modes.json')
    with open(profile_path, encoding='utf-8') as profile_file:
        return json.load(profile_file)


def _resolve_drive_config(context):
    drive_mode = LaunchConfiguration('drive_mode').perform(context)

    profiles = _load_drive_mode_profiles()
    if drive_mode not in profiles:
        available_modes = ', '.join(sorted(profiles.keys()))
        raise RuntimeError(
            f'Unsupported drive_mode "{drive_mode}". Available: {available_modes}'
        )

    return drive_mode


def _launch_setup(context, *args, **kwargs):
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    world = LaunchConfiguration('world').perform(context)
    world_name = LaunchConfiguration('world_name').perform(context)
    if not world_name:
        world_name = _read_world_name(world)

    use_sim_time = LaunchConfiguration('use_sim_time').perform(context) == 'true'
    drive_mode = _resolve_drive_config(context)
    spawn_z = LaunchConfiguration('spawn_z').perform(context)
    spawn_x = LaunchConfiguration('spawn_x').perform(context)
    spawn_y = LaunchConfiguration('spawn_y').perform(context)
    rviz_enabled = LaunchConfiguration('rviz').perform(context) == 'true'
    gui_enabled = LaunchConfiguration('gui').perform(context) == 'true'
    render_engine = LaunchConfiguration('render_engine').perform(context)

    quadrover_description = Command([
        'xacro ',
        PathJoinSubstitution([
            FindPackageShare('quadrover_description'),
            'urdf',
            'quadrover.urdf.xacro',
        ]),
        f' drive_mode:={drive_mode}',
    ])

    render_flags = f'--render-engine {render_engine}'
    if gui_enabled:
        gz_args = f'-r {render_flags} {world}'
    else:
        gz_args = f'-r -s --headless-rendering {render_flags} {world}'

    bridge_remappings = [
        ('/lidar/scan/points', '/lidar/points'),
    ]
    if drive_mode == 'mecanum_drive':
        bridge_remappings.append(
            ('/model/quadrover/odometry_with_covariance', '/odom/wheel')
        )

    nodes = [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py'),
            ),
            launch_arguments={'gz_args': gz_args}.items(),
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'robot_description': quadrover_description,
            }],
        ),
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-world', world_name,
                '-name', 'quadrover',
                '-allow_renaming', 'true',
                '-param', 'robot_description',
                '-x', spawn_x,
                '-y', spawn_y,
                '-z', spawn_z,
            ],
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'robot_description': quadrover_description,
            }],
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=_bridge_arguments(drive_mode),
            remappings=bridge_remappings,
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen',
        ),
    ]

    if rviz_enabled:
        pkg_quadrover_gazebo = get_package_share_directory('quadrover_gazebo')
        nodes.append(
            Node(
                package='rviz2',
                executable='rviz2',
                arguments=['-d', os.path.join(pkg_quadrover_gazebo, 'rviz', 'quadrover.rviz')],
                parameters=[{'use_sim_time': use_sim_time}],
            )
        )

    return nodes


def generate_launch_description():
    pkg_quadrover_gazebo = get_package_share_directory('quadrover_gazebo')
    gz_resource_path = (
        pkg_quadrover_gazebo + ':' + os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    )

    return LaunchDescription([
        SetEnvironmentVariable(
            name='GZ_SIM_RESOURCE_PATH',
            value=gz_resource_path,
        ),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument(
            'world',
            default_value=os.path.join(pkg_quadrover_gazebo, 'worlds', 'empty.sdf'),
        ),
        DeclareLaunchArgument(
            'world_name',
            default_value='',
            description='Gazebo world name (auto-detected from SDF when empty)',
        ),
        DeclareLaunchArgument(
            'drive_mode',
            default_value='diff_drive',
            description='Drive profile from quadrover_control',
        ),
        DeclareLaunchArgument('spawn_z', default_value='0.23'),
        DeclareLaunchArgument('spawn_x', default_value='0.0'),
        DeclareLaunchArgument('spawn_y', default_value='0.0'),
        DeclareLaunchArgument('rviz', default_value='false'),
        DeclareLaunchArgument(
            'gui',
            default_value='false',
            description='Launch Gazebo GUI (single process with server)',
        ),
        DeclareLaunchArgument(
            'render_engine',
            default_value='ogre2',
            description='Gazebo rendering backend (ogre2 is the Fortress default)',
        ),
        OpaqueFunction(function=_launch_setup),
    ])
