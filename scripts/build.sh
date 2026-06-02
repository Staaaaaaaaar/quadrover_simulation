#!/usr/bin/env bash
# Build the robot simulation workspace.
set -eo pipefail

source /opt/ros/humble/setup.bash
cd "$(dirname "$0")/.."

colcon build --symlink-install
