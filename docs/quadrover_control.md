# quadrover_control

## 概述

| 属性 | 值 |
|------|-----|
| 版本 | 0.1.0 |
| 构建类型 | ament_cmake |
| 描述 | Quadrover 独立驱动子包（Gazebo DiffDrive 插件封装） |

本包将底盘驱动逻辑从 `quadrover_description` 中解耦，集中提供 Gazebo `DiffDrive` 与 `JointStatePublisher` 插件配置。`quadrover_description/urdf/quadrover.urdf.xacro` 直接 include 本包的 `drive_plugins.xacro`。

## 文件结构

```text
quadrover_control/
├── CMakeLists.txt
├── package.xml
├── config/
│   └── drive_modes.json
└── urdf/
    └── drive_plugins.xacro
```

## 驱动插件

配置文件：`config/drive_modes.json`（元数据说明）  
插件定义：`urdf/drive_plugins.xacro`

| 插件 | Gazebo System | 说明 |
|------|---------------|------|
| DiffDrive | `gz::sim::systems::DiffDrive` | 差速轮驱，订阅 `/cmd_vel`，发布 `/odom/wheel` |
| JointStatePublisher | `gz::sim::systems::JointStatePublisher` | 发布 `/joint_states` |

DiffDrive 关键配置：

| 项 | 值 |
|----|-----|
| `odom_topic` | `/odom/wheel` |
| `frame_id` / `child_frame_id` | `odom` / `base_link` |
| `tf_topic` | `/odom/wheel/tf_internal`（Gazebo 内部，不桥接到 ROS） |
| `odom_publish_frequency` | 30 Hz |

> 仿真允许轮式里程计误差；本包不发布 `odom→base_link` TF，仅通过 Gazebo 插件输出 `/odom/wheel` 话题。

## 使用方式

无需 launch 参数切换驱动模式，直接启动仿真即可：

```bash
ros2 launch quadrover_bringup sim_example.launch.py
ros2 launch quadrover_gazebo spawn_quadrover_sensors.launch.py rviz:=true
```
