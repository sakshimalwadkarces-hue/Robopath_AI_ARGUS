"""Launch ARGUS in Gazebo Sim with ROS 2 sensor and drive bridges."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    description_share = get_package_share_directory('robot_description')
    bringup_share = get_package_share_directory('robot_bringup')
    sim_share = get_package_share_directory('ros_gz_sim')
    urdf_path = os.path.join(description_share, 'urdf', 'argus_robot.urdf')
    model_path = os.path.join(description_share, 'models', 'argus_robot.sdf')
    world_path = os.path.join(bringup_share, 'worlds', 'obstacle_course.sdf')
    with open(urdf_path, encoding='utf-8') as file:
        robot_description = file.read()

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        # Retained for any future world-model assets.  The robot SDF uses a
        # path relative to its installed `models/` directory because Gazebo
        # Sim does not resolve ROS `package://` mesh URIs.
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', description_share),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(
            os.path.join(sim_share, 'launch', 'gz_sim.launch.py')),
            launch_arguments={'gz_args': '-r ' + world_path}.items()),
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             parameters=[{'robot_description': robot_description,
                          'use_sim_time': LaunchConfiguration('use_sim_time')}]),
        Node(package='ros_gz_sim', executable='create', arguments=[
            '-name', 'argus_robot', '-file', model_path,
            '-x', '0.0', '-y', '0.0', '-z', '0.16']),
        Node(package='ros_gz_bridge', executable='parameter_bridge', arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/camera/image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry'], output='screen'),
        Node(package='argus_tasks', executable='odom_tf',
             parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}], output='screen'),
        Node(package='argus_tasks', executable='autonomous_navigation',
             parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}], output='screen'),
        Node(package='argus_tasks', executable='safety_navigation',
             parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}], output='screen'),
    ])
