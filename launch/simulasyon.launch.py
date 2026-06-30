import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():

    # 1. Paketimizin adını ve yollarını sisteme tanıtıyoruz
    package_name = 'forklift_description'
    pkg_share = get_package_share_directory(package_name)
    
    # 2. Yazdığın o forklift.urdf dosyasının yerini buluyoruz
    urdf_file = os.path.join(pkg_share, 'urdf', 'forklift.urdf')
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    # 3. Robotun iskeletini ROS 2 sistemine yayınlayacak olan düğüm (Node)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )

    # 4. ROS 2'nin kendi içindeki resmi Gazebo başlatıcısını çağırıyoruz
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
    )

    # 5. Bizim yazdığımız o sanal robotu Gazebo dünyasının içine fırlatan düğüm (Spawn)
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'otonom_forklift'],
        output='screen'
    )

    # Hepsini tek bir paket halinde ROS 2'ye teslim ediyoruz
    return LaunchDescription([
        robot_state_publisher,
        gazebo,
        spawn_entity
    ])