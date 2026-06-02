# four_wheel_localization

## 概述

| 属性 | 值 |
|------|-----|
| 版本 | 0.1.0 |
| 构建类型 | ament_cmake + ament_cmake_python |
| 描述 | 四轮机器人里程计融合与定位 |

本包整合 `/odom/*` 命名空间下的各里程计源，根据参数选择融合方法，最终发布 `/odom` 话题与 `odom→base_link` TF 变换。

## 文件结构

```
four_wheel_localization/
├── CMakeLists.txt
├── package.xml
├── config/
│   └── wheel_only.yaml          # wheel_only 模式参数
├── launch/
│   └── localization.launch.py   # fusion_mode 参数入口
└── scripts/
    └── odom_relay.py              # wheel_only 透传实现
```

## 依赖

- `rclpy`, `nav_msgs`, `geometry_msgs`, `tf2_ros`
- 后续 EKF 模式将依赖系统包 `robot_localization`（`ros-humble-robot-localization`）

## 融合模式

| 模式 | 说明 | 状态 |
|------|------|------|
| `wheel_only` | 透传 `/odom/wheel` → `/odom`，发布 `odom→base_link` TF | 已实现 |
| `ekf_wheel_imu` | EKF 融合轮式里程计 + IMU | 预留 |
| `rtk` / `slam` | 外部定位源接入 | 预留 |

通过 launch 参数 `fusion_mode` 选择（默认 `wheel_only`）。

## Launch 文件

### localization.launch.py

**参数：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `use_sim_time` | `true` | 仿真时钟 |
| `fusion_mode` | `wheel_only` | 融合方法 |

**启动示例：**

```bash
ros2 launch four_wheel_localization localization.launch.py
ros2 launch four_wheel_localization localization.launch.py fusion_mode:=wheel_only
```

## 节点

### odom_relay（wheel_only 模式）

| 属性 | 值 |
|------|-----|
| 节点名 | `odom_relay` |
| 语言 | Python 3 |

**订阅：**

| 话题 | 类型 | 说明 |
|------|------|------|
| `/odom/wheel` | `nav_msgs/Odometry` | Gazebo DiffDrive 轮式里程计 |

**发布：**

| 话题 / TF | 类型 | 说明 |
|-----------|------|------|
| `/odom` | `nav_msgs/Odometry` | 融合后里程计（`odom` → `base_link`） |
| `/tf` | TF | `odom` → `base_link` |

**参数（`config/wheel_only.yaml`）：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `input_topic` | `/odom/wheel` | 输入里程计话题 |
| `output_topic` | `/odom` | 输出里程计话题 |
| `odom_frame` | `odom` | 里程计父坐标系 |
| `base_frame` | `base_link` | 里程计子坐标系 |

## TF 树（完整模式）

```
map ──(robot_gazebo/map_tf_broadcaster)──► odom ──(odom_relay)──► base_link ──(URDF)──► 传感器
```

## 后续扩展

新增里程计源时：

1. 在 Gazebo 或外部节点发布 `/odom/<source>` 话题
2. 在 `config/` 添加对应融合参数文件
3. 在 `localization.launch.py` 中按 `fusion_mode` 分支启动对应节点

例如 IMU 融合需安装 `ros-humble-robot-localization` 并添加 EKF 配置文件，订阅 `/odom/wheel` 与 `/imu/data`。
