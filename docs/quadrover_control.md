# quadrover_control

## 概述

| 属性 | 值 |
|------|-----|
| 版本 | 0.1.0 |
| 构建类型 | ament_cmake |
| 描述 | Quadrover 独立驱动子包（Gazebo 轮驱插件封装） |

本包将底盘驱动逻辑从 `quadrover_description` 与 launch 逻辑中解耦，集中提供可选驱动插件。当前由 `quadrover_gazebo/launch/spawn_quadrover_sensors.launch.py` 读取 `drive_mode` 后传给 xacro。

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

## drive_mode 预设

配置文件：`config/drive_modes.json`  
插件定义：`urdf/drive_plugins.xacro`

| drive_mode | Gazebo System | 说明 |
|-----------|---------------|------|
| `diff_drive` | `gz::sim::systems::DiffDrive` | 常见差速轮驱，适用于多数移动机器人 |
| `mecanum_drive` | `ignition::gazebo::systems::MecanumDrive` | 全向麦克纳姆轮驱，支持平面全向运动 |

> 已移除 `custom`、`passive_fixed`、`passive_free` 等非驱动模式。
> `mecanum_drive` 在 Fortress 中输出 `OdometryWithCovariance`，并在 launch 中先桥接为 `/odom/wheel_raw`，再统一归一化到 ROS 侧 `/odom/wheel`（默认 `odom→base_link`）。

## 使用方式

```bash
# 差速驱动（默认）
ros2 launch quadrover_bringup sim_example.launch.py drive_mode:=diff_drive

# 麦克纳姆全向驱动
ros2 launch quadrover_gazebo spawn_quadrover_sensors.launch.py drive_mode:=mecanum_drive
```
