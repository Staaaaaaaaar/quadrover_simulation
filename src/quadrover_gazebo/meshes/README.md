# 自定义 Mesh 场景资源

本目录用于存放 **本地** 大型 mesh 资源（OBJ / MTL / 贴图等），默认 **不纳入 Git**。

`spawn_quadrover_sensors.launch.py` 会自动将 `quadrover_gazebo` 包路径加入 `GZ_SIM_RESOURCE_PATH`，因此 world SDF 中可使用相对 URI：

```xml
<uri>file://meshes/YourScene/YourScene.obj</uri>
```

## 使用步骤

1. 将 mesh 文件放入子目录，例如 `meshes/YourScene/`（含 `.obj`、`.mtl`、贴图 PNG 等）。
2. 在 `worlds/` 下新建 world SDF，引用上述 mesh（可参考本地 `shenyangdong.sdf` 模板）。
3. 启动仿真并指定 world 与生成位姿：

```bash
ros2 launch quadrover_gazebo spawn_quadrover_sensors.launch.py \
  world:=$(ros2 pkg prefix quadrover_gazebo)/share/quadrover_gazebo/worlds/your_world.sdf \
  spawn_x:=0.0 spawn_y:=0.0 spawn_z:=0.23 \
  use_diff_drive:=true wheel_joint_type:=continuous \
  gui:=true rviz:=true
```

4. （可选）在 `quadrover_bringup/launch/` 下复制 `sim_example.launch.py` 为本地 launch，修改默认 `world` 与 `spawn_*` 参数。

## 注意事项

- LiDAR 对 mesh 法线方向敏感；若出现射线穿透或虚假远点，需在建模工具中检查/反转法线。
- Gazebo 不读取 OBJ 顶点行上的顶点色（`v x y z r g b`），外观请通过 MTL 与贴图配置。
- 大型 mesh 仅保留在本地；提交仓库时请只增加 SDF 示例或文档，勿提交二进制资源。
