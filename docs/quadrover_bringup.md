# quadrover_bringup

## 概述

| 属性 | 值 |
|------|-----|
| 版本 | 0.1.0 |
| 构建类型 | ament_cmake |
| 描述 | Quadrover 仿真的顶层 launch 入口 |

本包不包含自定义节点，提供面向用户的场景级 launch 文件，将参数转发至 `quadrover_gazebo`。

## 文件结构

```
quadrover_bringup/
├── CMakeLists.txt
├── package.xml
└── launch/
    └── sim_example.launch.py        # 室内主要测试用例（10 m 封闭房间）
```

## 依赖

### 运行时依赖（exec_depend）

- `quadrover_gazebo`
- `quadrover_description`
- `quadrover_control`

## Launch 文件

### sim_example.launch.py

启动 10 m × 10 m 封闭测试房间，含简单障碍物，适合算法快速验证（主要室内测试用例）。

**默认参数：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `use_sim_time` | `true` | 使用仿真时钟 |
| `rviz` | `false` | 启动 RViz2 |
| `gui` | `false` | 启动 Gazebo GUI |
| `render_engine` | `ogre2` | Gazebo 渲染后端 |
| `world` | `quadrover_gazebo/worlds/example.sdf` | 世界文件 |
| `spawn_x/y/z` | `0.0 / 0.0 / 0.23` | 机器人生成位置 |
| `drive_mode` | `diff_drive` | 驱动模式（来自 `quadrover_control`）：`diff_drive` / `mecanum_drive` |
| `publish_wheel_odom_tf` | `false` | 是否发布 `odom→base_link` TF |
| `wheel_odom_frame_id` | `odom` | `/odom/wheel.header.frame_id` |
| `wheel_base_frame_id` | `base_link` | `/odom/wheel.child_frame_id` |

**启动示例：**

```bash
ros2 launch quadrover_bringup sim_example.launch.py rviz:=true gui:=true
```

## 自定义 mesh 场景

仓库内仅提交 `sim_example` 作为标准测试入口。若需加载本地 mesh 世界：

- 直接使用 `spawn_quadrover_sensors.launch.py` 并传入 `world` / `spawn_*` 参数；或
- 复制 `sim_example.launch.py` 为本地 launch（勿提交大型 mesh 与专用 world），修改默认 world 与生成位姿。

详见 [quadrover_gazebo.md — 自定义 mesh 场景](quadrover_gazebo.md#自定义-mesh-场景)。

## 启动的组件

`sim_example` 通过 `IncludeLaunchDescription` 调用：

1. `quadrover_gazebo/spawn_quadrover_sensors.launch.py`（Gazebo + 传感器桥接）

实际启动的进程包括：

1. Gazebo Sim（`ros_gz_sim/gz_sim.launch.py`）
2. `robot_state_publisher`
3. `ros_gz_sim/create`（生成机器人模型）
4. `ros_gz_bridge/parameter_bridge`（传感器与控制桥接）
5. `quadrover_gazebo/wheel_odom_normalizer.py`（统一里程计帧，可选发布 TF）
6. RViz2（可选）

## 节点

本包无自定义节点。

## 话题 / 服务

本包不直接发布或订阅任何话题，所有 ROS 接口由被包含的 launch 提供。参见 [quadrover_gazebo.md](quadrover_gazebo.md) 和 [README.md](README.md)。

## CMake 目标

仅安装 `launch/` 目录，无编译目标。
