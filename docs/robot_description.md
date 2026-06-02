# robot_description

## 概述

| 属性 | 值 |
|------|-----|
| 版本 | 0.1.0 |
| 构建类型 | ament_cmake |
| 描述 | 四轮洞穴探索机器人的 URDF/xacro 描述 |

本包定义机器人 `robot` 的运动学树、物理属性、Gazebo 传感器与驱动插件。采用模块化 xacro 设计，通过参数切换驱动模式。

## 文件结构

```
robot_description/
├── CMakeLists.txt
├── package.xml
└── urdf/
    ├── robot.urdf.xacro       # 主入口
    ├── chassis.xacro          # 底盘与四轮
    ├── imu.xacro              # IMU 传感器
    ├── lidar.xacro            # 3D GPU LiDAR
    ├── camera.xacro           # RGB + 深度相机
    └── gazebo_plugins.xacro   # DiffDrive + JointStatePublisher
```

## 依赖

### 运行时依赖（exec_depend）

- `xacro`
- `robot_state_publisher`
- `joint_state_publisher`
- `rviz2`

## xacro 参数

主入口 `robot.urdf.xacro` 接受以下参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `wheel_joint_type` | `fixed` | 轮子关节类型（`fixed` 或 `continuous`） |
| `use_diff_drive` | `false` | 是否插入 Gazebo DiffDrive 插件 |

**xacro 调用示例：**

```bash
xacro src/robot_description/urdf/robot.urdf.xacro \
  wheel_joint_type:=continuous \
  use_diff_drive:=true
```

## 运动学树（TF 树）

```
base_link
├── lidar_joint (fixed) → lidar_link
├── imu_joint (fixed) → imu_link
├── camera_joint (fixed) → camera_link
├── left_front_wheel_joint → left_front_wheel_link
├── right_front_wheel_joint → right_front_wheel_link
├── left_rear_wheel_joint (mimic left_front) → left_rear_wheel_link
└── right_rear_wheel_joint (mimic right_front) → right_rear_wheel_link
```

## 物理参数

| 参数 | 值 |
|------|-----|
| 底盘尺寸 | 0.6 × 0.4 × 0.3 m |
| 底盘质量 | 30 kg |
| 轮半径 / 宽度 | 0.15 m / 0.1 m |
| 轮距 (track_width) | 0.5 m（左轮 +Y，右轮 -Y，符合 REP-103） |
| 轴距 (wheelbase) | 0.4 m |
| 轮子质量 | 2 kg/轮 |
| 轮子摩擦系数 (mu1/mu2) | 1.0 |
| 离地间隙 (ground_clearance) | 0.08 m |

## 各模块详解

### chassis.xacro

- 定义 `base_link`（红色 box），`ground_clearance=0.08` 抬高底盘离地间隙
- 四轮宏 `wheel`：支持 `mimic_joint`（后轴 mimic 前轴，实现差速联动）
- Gazebo 材质与摩擦配置

### imu.xacro

| 属性 | 值 |
|------|-----|
| 挂载位置 | `base_link` |
| Gazebo 话题 | `/imu/data` |
| 更新率 | 100 Hz |
| frame_id | `imu_link` |

### lidar.xacro

| 属性 | 值 |
|------|-----|
| 挂载位置 | `base_link` 顶面（低 profile 安装座） |
| 传感器类型 | `gpu_lidar` |
| Gazebo 话题 | `/lidar/scan`（点云发布于 `/lidar/scan/points`） |
| 水平采样 | 720，全周扫描 |
| 垂直线数 | 16，±15° |
| 量程 | 0.1–50 m |
| 更新率 | 10 Hz |
| frame_id | `lidar_link` |

### camera.xacro

| 传感器 | Gazebo 话题 | 分辨率 | 更新率 | FOV |
|--------|-------------|--------|--------|-----|
| RGB 相机 | `/camera/color/image_raw` | 640×480 | 15 Hz | 60° |
| 深度相机 | `/camera/depth/image_raw` | 640×480 | 15 Hz | 60°（远裁剪 10 m） |

相机挂载于底盘前方，`frame_id` 为 `camera_link`。

### gazebo_plugins.xacro

当 `use_diff_drive=true` 时加载：

#### DiffDrive 插件（`gz-sim-diff-drive-system`）

| 配置项 | 值 |
|--------|-----|
| 左轮关节 | `left_front_wheel_joint`, `left_rear_wheel_joint` |
| 右轮关节 | `right_front_wheel_joint`, `right_rear_wheel_joint` |
| 轮距 / 半径 | 0.5 m / 0.15 m |
| 订阅话题 | `/cmd_vel` (`geometry_msgs/Twist`) |
| 发布话题 | `/odom/wheel`（TF 发布到内部话题，不桥接） |
| 坐标系 | `odom` → `base_link` |
| 线速度限制 | ±1.0 m/s |
| 角速度限制 | ±1.5 rad/s |
| 里程计发布频率 | 30 Hz |

#### JointStatePublisher 插件

- 发布 Gazebo 侧 `/joint_states`

## ROS 话题（经 Gazebo 插件 / 传感器产生，由 robot_gazebo 桥接）

本包不直接运行节点，但 URDF 中定义的 Gazebo 插件和传感器产生以下话题：

| 话题 | 类型 | 方向 | 来源 |
|------|------|------|------|
| `/cmd_vel` | `geometry_msgs/Twist` | 订阅 | DiffDrive 插件 |
| `/odom/wheel` | `nav_msgs/Odometry` | 发布 | DiffDrive 插件 |
| `/odom/ground_truth` | `nav_msgs/Odometry` | 发布 | OdometryPublisher 插件（真值，map→base_link） |
| `/joint_states` | `sensor_msgs/JointState` | 发布 | JointStatePublisher 插件 |
| `/imu/data` | `sensor_msgs/Imu` | 发布 | IMU 传感器 |
| `/lidar/scan/points` | `sensor_msgs/PointCloud2` | 发布 | GPU LiDAR |
| `/camera/color/image_raw` | `sensor_msgs/Image` | 发布 | RGB 相机 |
| `/camera/color/camera_info` | `sensor_msgs/CameraInfo` | 发布 | RGB 相机 |
| `/camera/depth/image_raw` | `sensor_msgs/Image` | 发布 | 深度相机 |
| `/camera/depth/camera_info` | `sensor_msgs/CameraInfo` | 发布 | 深度相机 |

## 节点

本包无自定义节点。URDF 由外部 `robot_state_publisher` 和 Gazebo 消费。

## CMake 目标

仅安装 `urdf/` 目录，无编译目标。
