# Robot Simulation

基于 **ROS 2 Humble** 与 **Gazebo Fortress** 的四轮移动机器人仿真环境，集成 LiDAR、IMU、RGB-D 相机与 Gazebo DiffDrive 差速驱动，适用于原生 Linux 下的传感器联调与导航算法开发。

## 功能概览

- 四轮差速底盘，支持 `/cmd_vel` 控制与 `/odom` 反馈（经 `four_wheel_localization` 融合发布）
- 里程计源统一在 `/odom/*` 命名空间（轮式、真值；后续可扩展 RTK、SLAM、IMU 等）
- 3D LiDAR（`/lidar/points`）、IMU（`/imu/data`）、RGB/深度相机
- 内置室内 example 测试场景与空世界；支持自定义 mesh 场景导入
- RViz2 预配置（点云、图像、TF）

## 包结构

| 包 | 说明 |
|---|---|
| `robot_description` | 模块化 xacro：底盘、传感器、Gazebo 插件 |
| `robot_gazebo` | 世界文件、launch、RViz、bridge 配置、map TF 广播 |
| `four_wheel_localization` | 里程计融合，发布 `/odom` 与 `odom→base_link` TF |
| `robot_bringup` | 高层 launch：`sim_example` |

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
```

### 室内主要测试用例

10 m × 10 m 四面围墙 + 简单障碍物（默认无 GUI，以下示例开启 Gazebo GUI 与 RViz2）：

```bash
ros2 launch robot_bringup sim_example.launch.py rviz:=true gui:=true
```

### 传感器联调（空世界）

```bash
ros2 launch robot_gazebo spawn_robot_sensors.launch.py rviz:=true gui:=true
```

### 自定义 mesh 场景

将 OBJ/MTL/贴图放入 `src/robot_gazebo/meshes/`，编写 world SDF 后通过 `world` 与 `spawn_*` 参数启动。详见 [meshes/README.md](src/robot_gazebo/meshes/README.md) 与 [docs/robot_gazebo.md](docs/robot_gazebo.md)。

### 常用 launch 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `gui` | `false` | 是否打开 Gazebo GUI |
| `rviz` | `false` | 是否启动 RViz2 |
| `render_engine` | `ogre2` | 渲染后端（Fortress 默认） |
| `use_diff_drive` | `true` | Gazebo DiffDrive 插件 |
| `publish_map_tf` | `true` | 发布 map 帧 TF（有 `odom→base_link` 时发 `map→odom`，否则发 `map→base_link`） |
| `use_localization` | `true` | 启动 four_wheel_localization（wheel_only 透传） |
| `spawn_x/y/z` | 因场景而异 | 机器人初始位姿 |

### 里程计与 TF 架构

各里程计源发布在 `/odom/*` 下，由 `four_wheel_localization` 融合后输出 `/odom`：

| 话题 / TF | 类型 | 说明 |
|---|---|---|
| `/odom/wheel` | `nav_msgs/Odometry` | Gazebo DiffDrive 轮式里程计（有漂移） |
| `/odom/ground_truth` | `nav_msgs/Odometry` | 仿真真值（`map` → `base_link`） |
| `/odom` | `nav_msgs/Odometry` | 融合后里程计（`odom` → `base_link`） |
| `/tf` | TF | `map→odom→base_link`（完整模式）或 `map→base_link`（无 localization） |

**完整 TF 树（`publish_map_tf:=true` + `use_localization:=true`）：**

```
map ──(map_tf_broadcaster)──► odom ──(odom_relay)──► base_link ──(URDF)──► 传感器
```

查看 TF 树：

```bash
ros2 topic echo /odom/ground_truth --field pose.pose
ros2 run tf2_tools view_frames
```

关闭 localization 时（map 直接连 base_link）：

```bash
ros2 launch robot_bringup sim_example.launch.py use_localization:=false rviz:=true gui:=true
```

关闭 map TF：

```bash
ros2 launch robot_bringup sim_example.launch.py publish_map_tf:=false rviz:=true gui:=true
```

### 手动控制

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## ROS 话题

| 话题 | 类型 | 说明 |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/Twist` | 速度指令（→ Gazebo） |
| `/odom/wheel` | `nav_msgs/Odometry` | 轮式里程计（Gazebo 原始） |
| `/odom/ground_truth` | `nav_msgs/Odometry` | 仿真真值（`map` → `base_link`） |
| `/odom` | `nav_msgs/Odometry` | 融合后里程计（`odom` → `base_link`） |
| `/tf` | `tf2_msgs/TFMessage` | map / odom / base_link 变换 |
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
ros2 topic hz /odom/wheel
ros2 topic hz /odom/ground_truth
ros2 run tf2_tools view_frames
```

## 说明

- 默认渲染引擎为 **ogre2**，面向原生 Linux + 独显，建议在 Ubuntu 实机运行以获得最佳 GUI 体验。
- 详细包文档见 [docs/README.md](docs/README.md)。

## 参考

- [ROS 2 Humble + Gazebo Fortress](https://gazebosim.org/docs/fortress/ros2_integration)
