#!/usr/bin/env bash
# Build the robot simulation workspace without miniconda Python.
set -eo pipefail

export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/opt/ros/humble/bin"
unset CONDA_PREFIX CONDA_DEFAULT_ENV CONDA_SHLVL CONDA_PYTHON_EXE

source /opt/ros/humble/setup.bash
cd "$(dirname "$0")/.."

colcon build --packages-select robot_description robot_gazebo robot_bringup \
  --allow-overriding robot_description robot_gazebo robot_bringup \
  --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3 "$@"

source install/setup.bash
echo "Build complete. Examples:"
echo "  ros2 launch robot_bringup sim_example.launch.py gui:=true"
echo "  ros2 launch robot_gazebo spawn_robot_sensors.launch.py rviz:=true gui:=true"
