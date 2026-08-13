import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    
    # We must provide the map we generated earlier so AMCL knows where it is!
    map_yaml_file = os.path.join(
        os.path.expanduser('~'), 
        'argus_ws/MindForgeAI-Project-Master-Workspace/04_active_workspaces/RoboPath_AI/src/robot_navigation/maps/factory_map.yaml'
    )
    
    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')),
            launch_arguments={
                'map': map_yaml_file,
                'use_sim_time': 'true',
                # This activates AMCL, A*, and DWB configurations!
                'params_file': os.path.join(os.path.expanduser('~'), 'argus_ws/MindForgeAI-Project-Master-Workspace/04_active_workspaces/RoboPath_AI/src/robot_navigation/config/nav2_params.yaml')
            }.items(),
        )
    ])
