cmake_minimum_required(VERSION 3.8)
project(forklift_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Bağımlılıkları buluyoruz
find_package(ament_cmake REQUIRED)

# Yazdığımız launch, urdf ve rviz klasörlerini sisteme yüklüyoruz
install(
  DIRECTORY launch urdf rviz
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package() 