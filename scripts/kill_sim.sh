#!/usr/bin/env bash
# Stop leftover Gazebo/ROS processes before launching simulation.
set -euo pipefail

killall -9 ign 2>/dev/null || true
killall -9 gz 2>/dev/null || true
pkill -9 -f "parameter_bridge" 2>/dev/null || true
pkill -9 -f "robot_state_publisher" 2>/dev/null || true
pkill -9 -f "spawn_robot_sensors" 2>/dev/null || true
sleep 2

echo "Simulation processes stopped."
