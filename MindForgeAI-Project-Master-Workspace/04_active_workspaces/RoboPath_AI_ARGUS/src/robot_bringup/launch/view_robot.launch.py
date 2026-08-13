"""Launch ARGUS in RViz with a complete, centred CAD assembly."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Start the state publishers and RViz for the ARGUS CAD model."""
    description_share = get_package_share_directory('robot_description')
    urdf_path = os.path.join(description_share, 'urdf', 'argus_robot.urdf')
    rviz_path = os.path.join(description_share, 'rviz', 'argus.rviz')

    with open(urdf_path, encoding='utf-8') as urdf_file:
        robot_description = urdf_file.read()

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen'),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            output='screen'),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_path],
            output='screen'),
    ])
