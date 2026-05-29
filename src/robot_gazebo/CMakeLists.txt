cmake_minimum_required(VERSION 3.8)
project(robot_gazebo)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

install(DIRECTORY config launch worlds rviz meshes
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS scripts/static_joint_state_publisher.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
