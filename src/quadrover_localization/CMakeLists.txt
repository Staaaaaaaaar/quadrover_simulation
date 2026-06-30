cmake_minimum_required(VERSION 3.8)
project(quadrover_localization)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

install(DIRECTORY config launch
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/odom_relay.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
