# Quadrover

基于 **ROS 2 Humble** 与 **Gazebo Fortress** 的四轮移动机器人仿真环境，集成 LiDAR、IMU、RGB-D 相机，并支持多种 Gazebo 轮式驱动插件，适用于原生 Linux 下的传感器联调与导航算法开发。

## 功能概览

- 四轮底盘，支持 `/cmd_vel` 控制与 `/odom/wheel` 轮式里程计
- 仿真真值位姿发布在 `/loc/gazebo`（`map` → `base_link`）
- 3D LiDAR（`/lidar/points`）、IMU（`/imu/data`）、RGB/深度相机
- 内置室内 example 测试场景与空世界；支持自定义 mesh 场景导入
- RViz2 预配置（点云、图像、TF）

## 包结构

| 包 | 说明 |
|---|---|
| `quadrover_description` | 模块化 xacro：底盘、传感器、Gazebo 插件 |
| `quadrover_control` | 独立驱动子包：封装 Gazebo 轮式驱动插件与 `drive_mode` 配置 |
| `quadrover_gazebo` | 世界文件、launch、RViz、ROS-GZ 桥接 |
| `quadrover_bringup` | 高层 launch：`sim_example` |

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
cd ~/ws/quadrover_simulation
./scripts/build.sh
```

若系统同时安装了 Miniconda，`build.sh` 会使用 `/usr/bin/python3` 编译，避免缺少 `catkin_pkg` 等问题。

## 运行

```bash
source install/setup.bash
```

### 室内主要测试用例

10 m × 10 m 四面围墙 + 简单障碍物（默认无 GUI，以下示例开启 Gazebo GUI 与 RViz2）：

```bash
ros2 launch quadrover_bringup sim_example.launch.py rviz:=true gui:=true
```

### 传感器联调（空世界）

```bash
ros2 launch quadrover_gazebo spawn_quadrover_sensors.launch.py rviz:=true gui:=true
```

### 自定义 mesh 场景

将 OBJ/MTL/贴图放入 `src/quadrover_gazebo/meshes/`，编写 world SDF 后通过 `world` 与 `spawn_*` 参数启动。详见 [meshes/README.md](src/quadrover_gazebo/meshes/README.md) 与 [docs/quadrover_gazebo.md](docs/quadrover_gazebo.md)。

### 常用 launch 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `gui` | `false` | 是否打开 Gazebo GUI |
| `rviz` | `false` | 是否启动 RViz2 |
| `render_engine` | `ogre2` | 渲染后端（Fortress 默认） |
| `drive_mode` | `diff_drive` | 驱动模式：`diff_drive`/`mecanum_drive` |
| `publish_wheel_odom_tf` | `false` | 是否发布 `odom→base_link`（来自 `/odom/wheel`） |
| `wheel_odom_frame_id` | `odom` | `/odom/wheel.header.frame_id` |
| `wheel_base_frame_id` | `base_link` | `/odom/wheel.child_frame_id` |
| `spawn_x/y/z` | 因场景而异 | 机器人初始位姿 |

### 位姿话题

本仓库不维护 `map→odom`。轮式里程计由归一化节点统一发布，默认仅发布位姿话题；可按需启用 `odom→base_link` TF：

| 话题 | 类型 | 坐标系 | 说明 |
|---|---|---|---|
| `/odom/wheel` | `nav_msgs/Odometry` | `odom` → `base_link` | Gazebo 轮式驱动插件里程计（统一帧，仍有漂移） |
| `/loc/gazebo` | `nav_msgs/Odometry` | `map` → `base_link` | 仿真真值位姿 |

`robot_state_publisher` 仍发布 URDF 定义的 `base_link` → 传感器 TF。若需轮式里程计 TF，可在 launch 参数中开启 `publish_wheel_odom_tf:=true`。

### 手动控制

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

切换驱动模式示例：

```bash
ros2 launch quadrover_gazebo spawn_quadrover_sensors.launch.py \
  drive_mode:=mecanum_drive
```

## ROS 话题

| 话题 | 类型 | 说明 |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/Twist` | 速度指令（→ Gazebo） |
| `/odom/wheel` | `nav_msgs/Odometry` | 轮式里程计（统一为 `odom` → `base_link`） |
| `/loc/gazebo` | `nav_msgs/Odometry` | 仿真真值（`map` → `base_link`） |
| `/joint_states` | `sensor_msgs/JointState` | 关节状态 |
| `/imu/data` | `sensor_msgs/Imu` | IMU |
| `/lidar/points` | `sensor_msgs/PointCloud2` | 3D 点云 |
| `/camera/color/image_raw` | `sensor_msgs/Image` | RGB |
| `/camera/depth/image_raw` | `sensor_msgs/Image` | 深度 |

## 验收命令

```bash
ros2 topic hz /imu/data
ros2 topic hz /lidar/points
ros2 topic hz /odom/wheel
ros2 topic hz /loc/gazebo
ros2 topic echo /loc/gazebo --field pose.pose
```

## 说明

- 默认渲染引擎为 **ogre2**，面向原生 Linux + 独显，建议在 Ubuntu 实机运行以获得最佳 GUI 体验。
- 本仓库仅提供仿真传感器与位姿源，不包含 odom/loc 融合及 map/odom TF 维护。
- 详细包文档见 [docs/README.md](docs/README.md)；运行时节点与话题见 [docs/runtime.md](docs/runtime.md)。

## 参考

- [ROS 2 Humble + Gazebo Fortress](https://gazebosim.org/docs/fortress/ros2_integration)
