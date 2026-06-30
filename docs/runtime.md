# 运行时信息

本文档介绍 Quadrover 仿真**运行时**的 ROS 节点、话题与 TF 结构，供联调与对接外部算法时查阅。

适用 launch：`quadrover_gazebo/spawn_quadrover_sensors.launch.py` 及其上层封装（如 `quadrover_bringup` 下的场景 launch）。默认参数下 `use_diff_drive=true` 时发布完整话题集；`rviz:=true` 时额外启动 RViz2。

> 本仿真包**不发布** `map→odom` 或 `odom→base_link` TF；位姿以 `/odom/wheel`、`/loc/gazebo` 话题形式提供。

## 进程架构

仿真运行时包含 **Gazebo 后端**（非 ROS 节点）与若干 **ROS 2 节点**（经桥接通信）：

```
┌─────────────────────────────────────────────────────────────┐
│  Gazebo Sim（gz sim，非 ROS 节点）                            │
│  ├── 物理引擎、世界场景、Quadrover 模型                        │
│  ├── DiffDrive / OdometryPublisher / JointState 插件         │
│  └── IMU / LiDAR / RGB-D 传感器                              │
└──────────────────────────┬──────────────────────────────────┘
                           │ GZ 话题
                           ▼
              ┌────────────────────────┐
              │  ros_gz_bridge         │  ← 传感器/控制桥接
              └───────────┬────────────┘
                          │ ROS 话题
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
  robot_state_publisher   rviz2      （外部节点，如 teleop）
```

| 组件 | 类型 | 一句话 |
|------|------|--------|
| Gazebo Sim | 独立进程 | 在仿真世界中计算物理运动并生成传感器数据，是整个数字孪生的核心引擎。 |
| `ros_gz_sim create` | 一次性 CLI | 将 URDF 模型实例化到 Gazebo 场景中，完成机器人「入场」的一次性操作。 |
| `ros_gz_bridge` | ROS 节点 | 把 Gazebo 侧的数据与控制指令转换为 ROS 2 话题，是仿真与 ROS 生态之间的唯一通道。 |
| `robot_state_publisher` | ROS 节点 | 根据 URDF 和关节状态发布机器人本体 TF，使传感器坐标系相对 `base_link` 可被正确定标。 |
| `rviz2` | ROS 节点 | 实时可视化点云、图像与 TF，用于人工确认仿真输出是否正常。 |

---

## ROS 节点

`use_diff_drive=true` 且 `rviz:=true` 时，`ros2 node list` 典型输出：

| 节点 | 包 | 一句话 |
|------|-----|--------|
| `/ros_gz_bridge` | `ros_gz_bridge` | 桥接 Gazebo 与 ROS 2，把仿真传感器、位姿和时钟暴露为 ROS 话题，并接收 `/cmd_vel` 驱动机器人。 |
| `/robot_state_publisher` | `robot_state_publisher` | 将 URDF 运动学链与 `/joint_states` 合成为 TF，让 LiDAR、相机等传感器拥有正确的空间参考。 |
| `/rviz` | `rviz2` | 订阅仿真话题并图形化展示，便于开发阶段快速验证数据流与机器人状态。 |
| `/transform_listener_impl_*` | （RViz 内部） | RViz 内置的 TF 查询客户端，用于在可视化中解析坐标变换，无需关注。 |

### `/ros_gz_bridge`

仿真与 ROS 之间的翻译层：没有它，Gazebo 内的传感器和控制插件无法被 ROS 节点订阅或驱动。

| 方向 | 话题 | 类型 |
|------|------|------|
| 订阅 | `/cmd_vel` | `geometry_msgs/Twist` |
| 订阅 | `/clock` | `rosgraph_msgs/Clock` |
| 发布 | `/clock` | `rosgraph_msgs/Clock` |
| 发布 | `/odom/wheel` | `nav_msgs/Odometry` |
| 发布 | `/loc/gazebo` | `nav_msgs/Odometry` |
| 发布 | `/joint_states` | `sensor_msgs/JointState` |
| 发布 | `/imu/data` | `sensor_msgs/Imu` |
| 发布 | `/lidar/points` | `sensor_msgs/PointCloud2` |
| 发布 | `/camera/color/image_raw` | `sensor_msgs/Image` |
| 发布 | `/camera/color/camera_info` | `sensor_msgs/CameraInfo` |
| 发布 | `/camera/depth/image_raw` | `sensor_msgs/Image` |
| 发布 | `/camera/depth/camera_info` | `sensor_msgs/CameraInfo` |

> `use_diff_drive=false` 时不桥接 `/cmd_vel`、`/odom/wheel`、`/joint_states`。

### `/robot_state_publisher`

负责维护机器人**本体**坐标系：它不处理定位，但确保各传感器相对底盘的位置关系正确，是点云投影、图像标注等算法的前提。

| 方向 | 话题 | 类型 |
|------|------|------|
| 订阅 | `/joint_states` | `sensor_msgs/JointState` |
| 订阅 | `/clock` | `rosgraph_msgs/Clock` |
| 发布 | `/tf` | `tf2_msgs/TFMessage` |
| 发布 | `/tf_static` | `tf2_msgs/TFMessage` |
| 发布 | `/robot_description` | `std_msgs/String` |

### `/rviz`（可选）

开发调试用的可视化前端，不参与控制或定位，但能直观确认传感器数据是否按预期发布。

| 方向 | 话题 | 类型 | 说明 |
|------|------|------|------|
| 订阅 | `/lidar/points` | `sensor_msgs/PointCloud2` | 点云显示 |
| 订阅 | `/camera/color/image_raw` | `sensor_msgs/Image` | RGB 图像 |
| 订阅 | `/camera/depth/image_raw` | `sensor_msgs/Image` | 深度图像 |
| 发布 | `/clicked_point` | `geometry_msgs/PointStamped` | RViz 交互（无消费者） |
| 发布 | `/goal_pose` | `geometry_msgs/PoseStamped` | RViz 交互（无消费者） |
| 发布 | `/initialpose` | `geometry_msgs/PoseWithCovarianceStamped` | RViz 交互（无消费者） |

---

## 话题详解

### 控制

#### `/cmd_vel`

| 属性 | 值 |
|------|-----|
| 类型 | `geometry_msgs/Twist` |
| 发布者 | 外部节点（如 `teleop_twist_keyboard`） |
| 订阅者 | `/ros_gz_bridge` → Gazebo DiffDrive |

**内容：** 速度指令。`linear.x` 为前进速度（m/s），`angular.z` 为绕 z 轴角速度（rad/s）。

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

---

### 位姿

#### `/odom/wheel`

| 属性 | 值 |
|------|-----|
| 类型 | `nav_msgs/Odometry` |
| 发布者 | `/ros_gz_bridge`（← Gazebo DiffDrive 插件） |
| 频率 | ~30 Hz（配置值；实测约 28 Hz） |
| 坐标系 | `header.frame_id=odom`，`child_frame_id=base_link` |

**内容：** 轮式里程计位姿与速度。由 DiffDrive 根据轮速积分，**有累积漂移**。包含 `pose.pose`（位姿）、`twist.twist`（速度）；协方差当前均为 0。DiffDrive 为 2D 里程计，静止时 `z=0`。

#### `/loc/gazebo`

| 属性 | 值 |
|------|-----|
| 类型 | `nav_msgs/Odometry` |
| 发布者 | `/ros_gz_bridge`（← Gazebo OdometryPublisher 插件） |
| 频率 | ~30 Hz（配置值；实测约 28 Hz） |
| 坐标系 | `header.frame_id=map`，`child_frame_id=base_link` |

**内容：** 仿真真值位姿。来自 Gazebo 物理引擎中的模型位姿，**无噪声、无漂移**，供 loc 层融合或算法评测。`z` 反映机器人在世界系中的实际高度（与 `spawn_z` 一致）。本包仅发布话题，**不**转为 TF。

---

### 本体状态

#### `/joint_states`

| 属性 | 值 |
|------|-----|
| 类型 | `sensor_msgs/JointState` |
| 发布者 | `/ros_gz_bridge`（← Gazebo JointStatePublisher） |
| 订阅者 | `/robot_state_publisher` |
| 频率 | 随 Gazebo 物理步进（实测约 1 kHz 量级） |

**内容：** 四个轮子关节状态：

| 关节名 | 说明 |
|--------|------|
| `left_front_wheel_joint` | 左前轮 |
| `left_rear_wheel_joint` | 左后轮 |
| `right_front_wheel_joint` | 右前轮 |
| `right_rear_wheel_joint` | 右后轮 |

每条消息含 `position`（rad）、`velocity`（rad/s）、`effort`（N·m）。`robot_state_publisher` 据此发布轮子连杆动态 TF。

#### `/robot_description`

| 属性 | 值 |
|------|-----|
| 类型 | `std_msgs/String` |
| 发布者 | `/robot_state_publisher` |

**内容：** xacro 展开后的完整 URDF 字符串。

---

### 传感器

#### `/imu/data`

| 属性 | 值 |
|------|-----|
| 类型 | `sensor_msgs/Imu` |
| 发布者 | `/ros_gz_bridge` |
| 频率 | ~95 Hz（实测） |
| 坐标系 | `header.frame_id=imu_link` |

**内容：** `orientation`（四元数）、`angular_velocity`（rad/s）、`linear_acceleration`（m/s²，静止时 z ≈ 9.8）。协方差均为 0。

#### `/lidar/points`

| 属性 | 值 |
|------|-----|
| 类型 | `sensor_msgs/PointCloud2` |
| 发布者 | `/ros_gz_bridge`（Gazebo `/lidar/scan/points` 经 remap） |
| 频率 | 10 Hz（配置值） |
| 坐标系 | `header.frame_id=lidar_link` |

**内容：** 3D 点云（`lidar.xacro` 配置）：

| 参数 | 值 |
|------|-----|
| 水平 | 720 点，360° |
| 垂直 | 16 线，±15° |
| 量程 | 0.1 – 50 m |
| 字段 | `x`, `y`, `z`, `intensity`, `ring` |
| 规模 | `width=720`, `height=16` |

#### `/camera/color/image_raw`

| 属性 | 值 |
|------|-----|
| 类型 | `sensor_msgs/Image` |
| 发布者 | `/ros_gz_bridge` |
| 频率 | 15 Hz（配置值；实测约 10 Hz） |

**内容：** RGB 图像，`640×480`，`R8G8B8`，水平 FOV 1.047 rad（≈60°）。

#### `/camera/color/camera_info`

| 属性 | 值 |
|------|-----|
| 类型 | `sensor_msgs/CameraInfo` |
| 发布者 | `/ros_gz_bridge` |

**内容：** RGB 内参，fx/fy ≈ 554.38，cx=320，cy=240，`distortion_model=plumb_bob`。

#### `/camera/depth/image_raw`

| 属性 | 值 |
|------|-----|
| 类型 | `sensor_msgs/Image` |
| 发布者 | `/ros_gz_bridge` |
| 频率 | 与 RGB 同步 |

**内容：** 深度图，`640×480`，量程 0.1 – 10 m。

#### `/camera/depth/camera_info`

| 属性 | 值 |
|------|-----|
| 类型 | `sensor_msgs/CameraInfo` |
| 发布者 | `/ros_gz_bridge` |

**内容：** 深度相机内参，分辨率与 RGB 一致。

---

### 仿真时钟

#### `/clock`

| 属性 | 值 |
|------|-----|
| 类型 | `rosgraph_msgs/Clock` |
| 发布者 | `/ros_gz_bridge`（← Gazebo 仿真时钟） |
| 订阅者 | `/robot_state_publisher`、`/rviz` 等 |

**内容：** 仿真时间。各节点在 `use_sim_time=true` 下以此为准。

---

### 系统话题

| 话题 | 类型 | 说明 |
|------|------|------|
| `/rosout` | `rcl_interfaces/Log` | 节点日志 |
| `/parameter_events` | `rcl_interfaces/ParameterEvent` | 参数变更事件 |

---

## TF 树

仿真运行时**不发布** `map` 或 `odom` 帧。`/tf` 仅含 URDF 定义的本体链：

```
base_link
├── camera_link          （静态，tf_static）
├── imu_link             （静态，tf_static）
├── lidar_link           （静态，tf_static）
├── left_front_wheel_link   （动态，随 joint_states 更新）
├── left_rear_wheel_link
├── right_front_wheel_link
└── right_rear_wheel_link
```

**静态变换（`/tf_static`）：**

| 父帧 | 子帧 | 平移 (x, y, z) m |
|------|------|------------------|
| `base_link` | `camera_link` | (0.30, 0, 0.075) |
| `base_link` | `imu_link` | (0, 0, 0) |
| `base_link` | `lidar_link` | (0, 0, 0.19) |

**动态变换（`/tf`）：** 四轮连杆随 `/joint_states` 更新。RViz 预配置 Fixed Frame 为 `base_link`。

---

## 数据流

```
                         Gazebo Sim
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    DiffDrive           OdometryPublisher    传感器插件
         │                    │                    │
    /odom/wheel          /loc/gazebo      imu / lidar / camera
    /joint_states                             /clock
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                      ros_gz_bridge
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
  robot_state_publisher      rviz2            外部算法节点
         │                                      （订阅传感器/位姿）
    /tf, /tf_static
    base_link → 传感器/轮子
```

---

## 发布频率参考

| 话题 | 频率 (Hz) | 来源 |
|------|-----------|------|
| `/clock` | ~1000 | Gazebo 物理步进 |
| `/joint_states` | ~1000 | 同上 |
| `/imu/data` | ~95 | IMU 传感器 |
| `/odom/wheel` | ~30 | DiffDrive 插件 |
| `/loc/gazebo` | ~30 | OdometryPublisher 插件 |
| `/lidar/points` | 10 | LiDAR 配置 |
| `/camera/color/image_raw` | 15 | RGB 相机配置 |

---

## 调试命令

```bash
ros2 node list
ros2 topic list -t

ros2 topic echo /odom/wheel --field pose.pose
ros2 topic echo /loc/gazebo --field pose.pose

ros2 topic hz /odom/wheel
ros2 topic hz /loc/gazebo
ros2 topic hz /lidar/points

ros2 run tf2_tools view_frames
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
