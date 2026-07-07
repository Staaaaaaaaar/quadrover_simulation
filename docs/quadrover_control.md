# quadrover_control

## 概述

| 属性 | 值 |
|------|-----|
| 版本 | 0.1.0 |
| 构建类型 | ament_cmake |
| 描述 | Quadrover 驱动模式（`drive_mode`）预设配置 |

本包用于集中管理四轮车驱动方式，当前由 `quadrover_gazebo/launch/spawn_quadrover_sensors.launch.py` 读取并生效。目标是将“驱动策略”从仿真启动逻辑中分离，便于后续扩展不同底盘控制方式。

## 文件结构

```text
quadrover_control/
├── CMakeLists.txt
├── package.xml
└── config/
    └── drive_modes.json
```

## drive_mode 预设

配置文件：`config/drive_modes.json`

| drive_mode | wheel_joint_type | use_diff_drive | use_joint_state_publisher | 说明 |
|-----------|------------------|----------------|---------------------------|------|
| `diff_drive` | `continuous` | `true` | `false` | 启用 Gazebo DiffDrive，可通过 `/cmd_vel` 驱动 |
| `passive_fixed` | `fixed` | `false` | `true` | 关闭驱动并固定车轮，适合纯传感器联调 |
| `passive_free` | `continuous` | `false` | `false` | 关闭驱动，车轮连续关节（自由滚动） |
| `custom` | 手动指定 | 手动指定 | 手动指定 | 不使用预设，直接采用 launch 参数 |

## 使用方式

```bash
# 预设：差速驱动
ros2 launch quadrover_bringup sim_example.launch.py drive_mode:=diff_drive

# 预设：纯传感器调试（固定轮）
ros2 launch quadrover_gazebo spawn_quadrover_sensors.launch.py drive_mode:=passive_fixed

# 自定义：保留旧参数接口
ros2 launch quadrover_gazebo spawn_quadrover_sensors.launch.py \
  drive_mode:=custom use_diff_drive:=true wheel_joint_type:=continuous
```
