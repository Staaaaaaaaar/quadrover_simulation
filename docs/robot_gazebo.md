# robot_gazebo

## 概述

| 属性 | 值 |
|------|-----|
| 版本 | 0.1.0 |
| 构建类型 | ament_cmake + ament_cmake_python |
| 描述 | Gazebo Fortress 仿真 launch、世界文件与 ROS-GZ 桥接 |

本包是仿真的核心运行时包，负责启动 Gazebo、生成机器人、桥接 Gazebo 与 ROS 2 话题，并提供预配置的 RViz 与世界场景。

## 文件结构

```
robot_gazebo/
├── CMakeLists.txt
├── package.xml
├── config/
│   └── ros_gz_bridge.yaml           # 声明式桥接配置（当前未被 launch 引用）
├── launch/
│   └── spawn_robot_sensors.launch.py # 核心仿真 launch
├── meshes/
│   ├── README.md                   # 自定义 mesh 导入说明
│   └── .gitkeep                    # 保留目录；实际资源本地放置（gitignore）
├── rviz/
│   └── robot.rviz                    # RViz2 预配置
├── scripts/
│   └── static_joint_state_publisher.py  # 空 joint_states 发布器
└── worlds/
    ├── empty.sdf                     # 空世界
    └── example.sdf                   # 室内主要测试用例（10 m 封闭房间）
```

## 依赖

### 运行时依赖（exec_depend）

- `robot_description`, `robot_control`
- `ros_gz_sim`, `ros_gz_bridge`, `ros_gz_image`
- `robot_state_publisher`, `rclpy`, `xacro`, `rviz2`

## Launch 文件

### spawn_robot_sensors.launch.py

核心仿真 launch，启动完整 Gazebo + 机器人 + 传感器桥接栈。

**Launch 参数：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `use_sim_time` | `true` | 仿真时钟 |
| `world` | `worlds/empty.sdf` | SDF 世界路径 |
| `world_name` | `''` | Gazebo world 名称（空则自动从 SDF 解析） |
| `wheel_joint_type` | `fixed` | 传给 xacro |
| `use_diff_drive` | `false` | 传给 xacro |
| `use_ros2_control` | `false` | 传给 xacro |
| `use_joint_state_publisher` | `false` | 启动空 joint_states 发布器 |
| `spawn_x/y/z` | `0.0 / 0.0 / 0.23` | 生成位置 |
| `rviz` | `false` | 启动 RViz2 |
| `gui` | `false` | Gazebo GUI |
| `render_engine` | `ogre2` | 渲染引擎 |

**启动示例：**

```bash
ros2 launch robot_gazebo spawn_robot_sensors.launch.py rviz:=true gui:=true
ros2 launch robot_gazebo spawn_robot_sensors.launch.py \
  world:=$(ros2 pkg prefix robot_gazebo)/share/robot_gazebo/worlds/example.sdf \
  use_diff_drive:=true wheel_joint_type:=continuous
```

**启动的进程：**

| # | 组件 | 包/可执行文件 |
|---|------|---------------|
| 1 | Gazebo Sim | `ros_gz_sim/gz_sim.launch.py` |
| 2 | robot_state_publisher | `robot_state_publisher/robot_state_publisher` |
| 3 | 机器人生成 | `ros_gz_sim/create` |
| 4 | ROS-GZ 桥接 | `ros_gz_bridge/parameter_bridge` |
| 5 | *(可选)* static_joint_state_publisher | `robot_gazebo/static_joint_state_publisher.py` |
| 6 | *(可选)* RViz2 | `rviz2/rviz2` |

## 自定义节点

### static_joint_state_publisher.py

为仅有 fixed 关节、无 Gazebo JointStatePublisher 的机器人发布空 `JointState`，保持 TF 链活跃。

| 属性 | 值 |
|------|-----|
| 节点名 | `static_joint_state_publisher` |
| 语言 | Python 3 |

**发布：**

| 话题 | 类型 | 说明 |
|------|------|------|
| `/joint_states` | `sensor_msgs/JointState` | 空消息（仅 header） |

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `rate` | double | 30.0 | 发布频率 (Hz) |
| `use_sim_time` | bool | — | 由 launch 传入 |

## 外部节点接口

### robot_state_publisher

| 参数 | 说明 |
|------|------|
| `use_sim_time` | 仿真时钟 |
| `robot_description` | xacro 生成的 URDF 字符串 |

| 方向 | 话题 | 类型 |
|------|------|------|
| 订阅 | `/joint_states` | `sensor_msgs/JointState` |
| 发布 | `/tf`, `/tf_static` | TF transforms |

### ros_gz_sim/create

在指定 world 中生成名为 `robot` 的机器人模型。

| CLI 参数 | 说明 |
|----------|------|
| `-world` | Gazebo world 名称 |
| `-name robot` | 模型名称 |
| `-allow_renaming true` | 允许重命名 |
| `-param robot_description` | URDF 参数 |
| `-x/-y/-z` | 生成位置 |

### ros_gz_bridge/parameter_bridge

#### 始终桥接（传感器 + 时钟）

| ROS 话题 | 方向 | GZ 类型 ↔ ROS 类型 |
|----------|------|---------------------|
| `/clock` | GZ→ROS | `gz.msgs.Clock` ↔ `rosgraph_msgs/Clock` |
| `/imu/data` | GZ→ROS | `gz.msgs.IMU` ↔ `sensor_msgs/Imu` |
| `/lidar/scan/points` → `/lidar/points` | GZ→ROS | `gz.msgs.PointCloudPacked` ↔ `sensor_msgs/PointCloud2` |
| `/camera/color/image_raw` | GZ→ROS | `gz.msgs.Image` ↔ `sensor_msgs/Image` |
| `/camera/color/camera_info` | GZ→ROS | `gz.msgs.CameraInfo` ↔ `sensor_msgs/CameraInfo` |
| `/camera/depth/image_raw` | GZ→ROS | `gz.msgs.Image` ↔ `sensor_msgs/Image` |
| `/camera/depth/camera_info` | GZ→ROS | `gz.msgs.CameraInfo` ↔ `sensor_msgs/CameraInfo` |

> LiDAR 点云经 remapping：`/lidar/scan/points` → `/lidar/points`

#### 当 `use_diff_drive=true` 时额外桥接

| ROS 话题 | 方向 | 类型 |
|----------|------|------|
| `/cmd_vel` | ROS→GZ | `geometry_msgs/Twist` |
| `/odom` | GZ→ROS | `nav_msgs/Odometry` |
| `/tf` | GZ→ROS | `tf2_msgs/TFMessage` |
| `/joint_states` | GZ→ROS | `sensor_msgs/JointState` |

### rviz2（可选）

加载 `rviz/robot.rviz`，订阅以下可视化话题：

| Display | 话题 |
|---------|------|
| PointCloud2 | `/lidar/points` |
| RGB Camera | `/camera/color/image_raw` |
| Depth Camera | `/camera/depth/image_raw` |
| Odometry（默认禁用） | `/odom` |
| TF | 全部 frames |
| Fixed Frame | `base_link` |

## 世界文件

### empty.sdf

| 属性 | 值 |
|------|-----|
| World 名 | `empty` |
| 用途 | 最小测试环境 |
| 地面 | 100×100 m 平面 |
| 物理引擎 | ODE，1 ms 步长，实时因子 1.0 |

### example.sdf

| 属性 | 值 |
|------|-----|
| World 名 | `example` |
| 用途 | 10 m × 10 m 封闭测试房间（主要室内测试用例） |
| 内容 | 四面墙 + 地板（高 2.5 m）+ 4 个障碍物 |
| 默认相机 | pose `(0, -6, 3)` |

## 自定义 mesh 场景

大型 mesh 资源（OBJ / MTL / 贴图）放在 `meshes/` 下，**默认不提交 Git**。`spawn_robot_sensors.launch.py` 启动时会将本包 share 路径写入 `GZ_SIM_RESOURCE_PATH`，world SDF 中可用：

```xml
<uri>file://meshes/YourScene/YourScene.obj</uri>
```

**推荐流程：**

1. 将 mesh 放入 `src/robot_gazebo/meshes/YourScene/`。
2. 在 `worlds/` 新建 SDF，添加 static model 引用上述 URI（visual + collision）。
3. 用 launch 参数指定 world 与生成位姿：

```bash
ros2 launch robot_gazebo spawn_robot_sensors.launch.py \
  world:=$(ros2 pkg prefix robot_gazebo)/share/robot_gazebo/worlds/your_world.sdf \
  spawn_x:=0.0 spawn_y:=0.0 spawn_z:=0.23 \
  use_diff_drive:=true wheel_joint_type:=continuous \
  gui:=true rviz:=true
```

4. （可选）复制 `robot_bringup/launch/sim_example.launch.py` 为本地 launch，修改默认 `world` 与 `spawn_*`。

更多细节见 [meshes/README.md](../src/robot_gazebo/meshes/README.md)。

**注意：** LiDAR 对 mesh 法线方向敏感；Gazebo 不读取 OBJ 顶点行颜色，外观请用 MTL/贴图。

## 配置文件

### config/ros_gz_bridge.yaml

声明式 ROS-GZ 桥接规则，与 launch 中 `_bridge_arguments()` 函数内容等效（不含 `/clock`）。**当前未被任何 launch 文件引用**，实际桥接在 launch 中内联配置。

## 话题数据流

```
                    ┌─────────────────┐
  /cmd_vel ────────►│ Gazebo DiffDrive│──────► /odom, /tf (GZ)
  (ROS)             │     Plugin      │──────► /joint_states (GZ)
                    └────────┬────────┘
                             │ parameter_bridge
                             ▼
  /cmd_vel, /odom, /tf, /joint_states ────────► ROS 侧

  Gazebo Sensors ──bridge──► /imu/data, /lidar/points,
                             /camera/color/*, /camera/depth/*, /clock

  /joint_states ──► robot_state_publisher ──► /tf, /tf_static
```

## CMake 目标

- 安装 `config/`, `launch/`, `worlds/`, `rviz/`, `meshes/` 目录
- 安装 `scripts/static_joint_state_publisher.py` 至 `lib/robot_gazebo`
- 无 C++ 编译目标
