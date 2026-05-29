# robot_control

## 概述

| 属性 | 值 |
|------|-----|
| 版本 | 0.1.0 |
| 构建类型 | ament_cmake |
| 描述 | 洞穴探索机器人的 ros2_control 配置 |

本包提供可选的 ros2_control 驱动路径，通过 `gz_ros2_control` 插件在 Gazebo 内启动 `controller_manager` 并加载标准控制器。**默认 bringup 不启用此路径**（`use_ros2_control=false`），实际使用 Gazebo DiffDrive 插件驱动。

## 文件结构

```
robot_control/
├── CMakeLists.txt
├── package.xml
├── config/
│   └── controllers.yaml              # 控制器参数
└── urdf/
    └── robot.ros2_control.xacro      # ros2_control 硬件接口宏
```

## 依赖

### 运行时依赖（exec_depend）

- `ros2_control`, `ros2_controllers`
- `gz_ros2_control`, `controller_manager`
- `diff_drive_controller`, `joint_state_broadcaster`
- `xacro`

> 完整 ros2_control 路径还需系统安装：
> `ros-humble-gz-ros2-control`、`ros-humble-ros2-controllers`

## 启用方式

在 launch 中设置以下参数（需同时关闭 DiffDrive）：

```bash
ros2 launch robot_bringup sim_example.launch.py \
  use_diff_drive:=false \
  use_ros2_control:=true \
  wheel_joint_type:=continuous
```

`robot_description/urdf/robot.urdf.xacro` 在 `use_ros2_control=true` 时会 include 本包的 xacro 并实例化 `<xacro:robot_ros2_control/>`。

## ros2_control 硬件接口

定义于 `urdf/robot.ros2_control.xacro` 宏 `robot_ros2_control`：

| 配置项 | 值 |
|--------|-----|
| 硬件插件 | `gz_ros2_control/GazeboSimSystem` |
| Gazebo 插件 | `gz_ros2_control-system` |
| 参数文件 | `$(find robot_control)/config/controllers.yaml` |

### 关节接口

四个轮子关节均暴露：

| 接口类型 | 名称 |
|----------|------|
| 命令接口 | `velocity` |
| 状态接口 | `velocity`, `position` |

| 关节名 |
|--------|
| `left_front_wheel_joint` |
| `right_front_wheel_joint` |
| `left_rear_wheel_joint` |
| `right_rear_wheel_joint` |

## 控制器配置

定义于 `config/controllers.yaml`：

### controller_manager

| 参数 | 值 |
|------|-----|
| `update_rate` | 50 Hz |
| `use_sim_time` | true |

### joint_state_broadcaster

| 参数 | 值 |
|------|-----|
| `use_sim_time` | true |

**典型接口：**

| 方向 | 话题/服务 | 类型 |
|------|-----------|------|
| 发布 | `/joint_states` | `sensor_msgs/JointState` |
| 服务 | `/controller_manager/list_controllers` 等 | controller_manager 标准服务 |

### diff_drive_controller

| 参数 | 值 |
|------|-----|
| `left_wheel_names` | `left_front_wheel_joint`, `left_rear_wheel_joint` |
| `right_wheel_names` | `right_front_wheel_joint`, `right_rear_wheel_joint` |
| `wheel_separation` | 0.5 m |
| `wheel_radius` | 0.15 m |
| `publish_rate` | 30 Hz |
| `odom_frame_id` | `odom` |
| `base_frame_id` | `base_link` |
| `open_loop` | false |
| `enable_odom_tf` | true |
| `cmd_vel_timeout` | 0.5 s |

**典型接口：**

| 方向 | 话题/服务 | 类型 |
|------|-----------|------|
| 订阅 | `/diff_drive_controller/cmd_vel_unstamped` | `geometry_msgs/Twist` |
| 发布 | `/odom` | `nav_msgs/Odometry` |
| 发布 | `/tf` | TF（`odom` → `base_link`） |
| 服务 | `/diff_drive_controller/configure` 等 | 控制器生命周期服务 |

> **注意：** `diff_drive_controller` 默认订阅 `/diff_drive_controller/cmd_vel_unstamped`，而非 `/cmd_vel`。启用 ros2_control 后需手动 remap 或使用对应话题名。

## 节点

本包无自定义节点。启用 ros2_control 时，由 Gazebo 插件 `gz_ros2_control-system` 在仿真进程内启动 `controller_manager`，并自动加载 `controllers.yaml` 中定义的控制器。

## Launch 文件

本包无 launch 文件。控制器通过 URDF 中的 Gazebo 插件在仿真启动时加载。

## 与默认 DiffDrive 模式的对比

| 特性 | Gazebo DiffDrive（默认） | ros2_control |
|------|--------------------------|--------------|
| 启用参数 | `use_diff_drive:=true` | `use_ros2_control:=true` |
| 速度指令话题 | `/cmd_vel` | `/diff_drive_controller/cmd_vel_unstamped` |
| 里程计 | Gazebo 插件 → bridge | diff_drive_controller |
| 关节状态 | Gazebo JointStatePublisher → bridge | joint_state_broadcaster |
| 额外依赖 | 无 | `gz-ros2-control` |
| bridge 需求 | 需桥接 cmd_vel/odom/tf/joint_states | 控制器直接在 ROS 侧发布 |

## CMake 目标

- 安装 `config/` 和 `urdf/` 目录
- 无编译目标
