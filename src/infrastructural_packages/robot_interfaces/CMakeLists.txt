cmake_minimum_required(VERSION 3.8)
project(robot_interfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(geometry_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Example.msg"
  "msg/Waypoint.msg"
  "msg/Pose2DArray.msg"
  "msg/ObjectPoint.msg"
  "srv/Example.srv"
  "action/Example.action"
  "msg/ImageMetadata.msg"
  "msg/SpectrometerData.msg"
  "msg/CameraManagerCommand.msg"
  "msg/TargetedFloat.msg"
  "msg/TargetedBool.msg"
  "msg/TargetedString.msg"
  "msg/TargetedInt.msg"
  "msg/STargetedFloat.msg"
  "msg/STargetedBool.msg"
  "msg/STargetedString.msg"
  "msg/StringArray.msg"
  DEPENDENCIES std_msgs geometry_msgs # Add packages that above messages depend on
)

ament_package()
