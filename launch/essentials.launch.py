from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node, SetParameter
import os

def generate_launch_description():
    pkg_share = FindPackageShare('nav_hub').find('nav_hub')

    robot_description_launch = os.path.join(
        FindPackageShare('robot06_description').find('robot06_description'),
        'launch',
        'display.launch.py'
    )

    lidar_dir = os.path.join(
        FindPackageShare('ldlidar_stl_ros2').find('ldlidar_stl_ros2'),
        'launch',
        'stl27l.launch.py'
    )

    essential_canopen = os.path.join(
        FindPackageShare('canopen_ros').find('canopen_ros'),
        'launch', 
        'canopen.launch.py')
    
    essential_nav2 = os.path.join(pkg_share, 'launch', 'route_graph/nav_graph.launch.py')
 
    
    
    return LaunchDescription([
        SetParameter(name='use_sim_time', value=False),
        
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(robot_description_launch)
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(lidar_dir)
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(essential_canopen)
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(essential_nav2)
        )
    ])
