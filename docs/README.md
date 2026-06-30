# 包文档索引

本目录包含四轮移动机器人仿真工作空间中各 ROS 2 包的详细说明。

## 工作空间概览

基于 **ROS 2 Humble** + **Gazebo Fortress**（`ros_gz`）的四轮差速驱动移动机器人仿真环境，集成 3D LiDAR、IMU、RGB-D 相机，适用于传感器联调与导航算法开发。底盘由 **Gazebo DiffDrive 插件**驱动，里程计经 **quadrover_localization** 融合后发布。

## 包依赖关系

```
quadrover_bringup                    ← 顶层入口（场景 launch）
    ├── quadrover_gazebo             ← Gazebo 仿真、桥接、世界文件
    │       └── quadrover_description   ← URDF/xacro Quadrover 模型
    └── quadrover_localization  ← 里程计融合与 /odom 发布
```

## 各包文档

| 包 | 文档 | 职责 |
|----|------|------|
| `quadrover_bringup` | [quadrover_bringup.md](quadrover_bringup.md) | 高层场景 launch（example） |
| `quadrover_description` | [quadrover_description.md](quadrover_description.md) | 模块化 URDF/xacro Quadrover 描述 |
| `quadrover_gazebo` | [quadrover_gazebo.md](quadrover_gazebo.md) | Gazebo 世界、launch、ROS-GZ 桥接、map TF |
| `quadrover_localization` | [quadrover_localization.md](quadrover_localization.md) | 里程计融合，发布 `/odom` 与 `odom→base_link` TF |

## 跨包 ROS 话题总览（默认配置）

| 话题 | 类型 | 方向 | 来源 |
|------|------|------|------|
| `/cmd_vel` | `geometry_msgs/Twist` | 订阅 | Gazebo DiffDrive 插件 |
| `/odom/wheel` | `nav_msgs/Odometry` | 发布 | Gazebo DiffDrive 插件（原始轮式里程计） |
| `/odom/ground_truth` | `nav_msgs/Odometry` | 发布 | Gazebo OdometryPublisher（真值） |
| `/odom` | `nav_msgs/Odometry` | 发布 | quadrover_localization（融合后里程计） |
| `/tf` | `tf2_msgs/TFMessage` | 发布 | map_tf_broadcaster + odom_relay + robot_state_publisher |
| `/joint_states` | `sensor_msgs/JointState` | 发布 | Gazebo JointStatePublisher |
| `/imu/data` | `sensor_msgs/Imu` | 发布 | Gazebo IMU 传感器 |
| `/lidar/points` | `sensor_msgs/PointCloud2` | 发布 | Gazebo GPU LiDAR（经 remap） |
| `/camera/color/image_raw` | `sensor_msgs/Image` | 发布 | RGB 相机 |
| `/camera/color/camera_info` | `sensor_msgs/CameraInfo` | 发布 | RGB 相机 |
| `/camera/depth/image_raw` | `sensor_msgs/Image` | 发布 | 深度相机 |
| `/camera/depth/camera_info` | `sensor_msgs/CameraInfo` | 发布 | 深度相机 |
| `/clock` | `rosgraph_msgs/Clock` | 发布 | Gazebo 仿真时钟 |

## 快速启动

```bash
# 室内主要测试用例（默认含 localization + map TF）
ros2 launch quadrover_bringup sim_example.launch.py

# 空世界传感器联调
ros2 launch quadrover_gazebo spawn_quadrover_sensors.launch.py rviz:=true gui:=true
```

自定义 mesh 场景导入见 [quadrover_gazebo.md — 自定义 mesh 场景](quadrover_gazebo.md#自定义-mesh-场景)。
