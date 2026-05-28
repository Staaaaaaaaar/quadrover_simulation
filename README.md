# Robot Simulation

基于 **ROS 2 Humble** 与 **Gazebo Fortress** 的四轮移动机器人仿真环境，集成 LiDAR、IMU、RGB-D 相机与差速驱动，适用于原生 Linux 下的传感器联调与导航算法开发。

## 功能概览

- 四轮差速底盘，支持 `/cmd_vel` 控制与 `/odom` 反馈
- 3D LiDAR（`/lidar/points`）、IMU（`/imu/data`）、RGB/深度相机
- 多种仿真场景：隧道/崎岖地形、封闭测试房间、空世界
- RViz2 预配置（点云、图像、TF）
- 可选 `ros2_control` 路径（需额外安装 `gz-ros2-control`）

## 包结构

| 包 | 说明 |
|---|---|
| `robot_description` | 模块化 xacro：底盘、传感器、Gazebo 插件 |
| `robot_gazebo` | 世界文件、launch、RViz、bridge 配置 |
| `robot_control` | ros2_control 与控制器配置（默认未启用） |
| `robot_bringup` | 高层 launch：`sim_cave`、`sim_test_room` |

## 依赖

在 **Ubuntu 22.04 + 原生 Linux** 上安装：

```bash
sudo apt update
sudo apt install -y \
  ros-humble-desktop \
  ros-humble-ros-gz \
  ros-humble-xacro \
  ros-humble-robot-state-publisher \
  ros-humble-rviz2
```

Gazebo Fortress 随 `ros-humble-ros-gz` 提供（`ign gazebo` / `gz sim`）。

## 编译

```bash
cd ~/ws/robot_simulation
./scripts/build.sh
```

若系统同时安装了 Miniconda，`build.sh` 会使用 `/usr/bin/python3` 编译，避免缺少 `catkin_pkg` 等问题。

## 运行

```bash
source install/setup.bash
./scripts/kill_sim.sh   # 启动前清理残留 Gazebo/bridge 进程（可选）
```

### 复杂场景仿真（默认 RViz，无 GUI）

含隧道结构与崎岖地形，适合测试运动与感知：

```bash
ros2 launch robot_bringup sim_cave.launch.py
```

### 复杂场景 + Gazebo GUI

```bash
ros2 launch robot_bringup sim_cave.launch.py gui:=true
```

### 封闭测试房间（默认 GUI + RViz）

10 m × 10 m 四面围墙 + 简单障碍物：

```bash
ros2 launch robot_bringup sim_test_room.launch.py
```

### 传感器联调（空世界）

```bash
ros2 launch robot_gazebo spawn_robot_sensors.launch.py rviz:=true gui:=true
```

### 常用 launch 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `gui` | 因 launch 而异 | 是否打开 Gazebo GUI |
| `rviz` | 因 launch 而异 | 是否启动 RViz2 |
| `render_engine` | `ogre2` | 渲染后端（Fortress 默认） |
| `use_diff_drive` | `true` | Gazebo DiffDrive 插件 |
| `spawn_x/y/z` | 因场景而异 | 机器人初始位姿 |

### 手动控制

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## ROS 话题

| 话题 | 类型 | 说明 |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/Twist` | 速度指令（→ Gazebo） |
| `/odom` | `nav_msgs/Odometry` | 里程计 |
| `/tf` | `tf2_msgs/TFMessage` | `odom` → `base_link` 等 |
| `/joint_states` | `sensor_msgs/JointState` | 关节状态 |
| `/imu/data` | `sensor_msgs/Imu` | IMU |
| `/lidar/points` | `sensor_msgs/PointCloud2` | 3D 点云 |
| `/camera/color/image_raw` | `sensor_msgs/Image` | RGB |
| `/camera/depth/image_raw` | `sensor_msgs/Image` | 深度 |

## 验收命令

```bash
ros2 topic hz /imu/data
ros2 topic hz /lidar/points
ros2 topic hz /odom
ros2 run tf2_tools view_frames
```

## 说明

- 默认渲染引擎为 **ogre2**，面向原生 Linux + 独显，建议在 Ubuntu 实机运行以获得最佳 GUI 体验。
- 完整 `ros2_control` 驱动需安装 `ros-humble-gz-ros2-control`、`ros-humble-ros2-controllers`，并在 launch 中设置 `use_ros2_control:=true`。

## 参考

- [ROS 2 Humble + Gazebo Fortress](https://gazebosim.org/docs/fortress/ros2_integration)
