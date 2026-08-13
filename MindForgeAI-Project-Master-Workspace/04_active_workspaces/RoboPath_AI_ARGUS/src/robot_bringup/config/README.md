# Runtime configuration

`argus_sim.launch.py` bridges `/cmd_vel`, `/scan`, `/camera/image`, `/odom`,
and `/clock` between Gazebo and ROS 2.  Use Nav2 for global planning; the
`argus_tasks` safety controller remains the final stop layer for both LiDAR
and camera detections.
