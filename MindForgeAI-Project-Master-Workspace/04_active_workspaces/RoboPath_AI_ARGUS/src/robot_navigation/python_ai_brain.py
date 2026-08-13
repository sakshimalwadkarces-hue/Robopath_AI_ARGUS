#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry, OccupancyGrid
from std_msgs.msg import Header
import math

class PurePythonAIBrain(Node):
    def __init__(self):
        super().__init__('python_ai_brain')
        
        self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.create_subscription(PoseStamped, '/goal_pose', self.goal_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # --- NEW: MAP PUBLISHER ---
        self.map_pub = self.create_publisher(OccupancyGrid, '/map', 10) 
        
        self.timer = self.create_timer(0.05, self.control_loop)
        
        # --- NEW: BROADCAST MAP EVERY 1 SECOND ---
        self.map_timer = self.create_timer(1.0, self.publish_map) 

        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0
        self.goal_x = None
        self.goal_y = None
        self.lidar_ranges = []
        
        self.grid_resolution = 0.5 
        self.grid_size = 40 
        self.grid_offset = 20 
        self.map_grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        self.get_logger().info("PYTHON GRID MAPPER ACTIVATED. Broadcasting to RViz...")

    def publish_map(self):
        """ Translates the secret Python grid into a visual map for RViz """
        grid_msg = OccupancyGrid()
        grid_msg.header = Header()
        grid_msg.header.stamp = self.get_clock().now().to_msg()
        grid_msg.header.frame_id = 'odom'
        grid_msg.info.resolution = self.grid_resolution
        grid_msg.info.width = self.grid_size
        grid_msg.info.height = self.grid_size
        
        # Center the map under the robot
        grid_msg.info.origin.position.x = - (self.grid_size * self.grid_resolution) / 2.0
        grid_msg.info.origin.position.y = - (self.grid_size * self.grid_resolution) / 2.0
        grid_msg.info.origin.orientation.w = 1.0

        # Convert our 0s and 1s into RViz colors (0 = Free space, 100 = Solid Wall)
        flat_grid = []
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if self.map_grid[x][y] == 1:
                    flat_grid.append(100) 
                else:
                    flat_grid.append(0)   

        grid_msg.data = flat_grid
        self.map_pub.publish(grid_msg)

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)

    def goal_callback(self, msg):
        self.goal_x = msg.pose.position.x
        self.goal_y = msg.pose.position.y
        self.get_logger().info(f"CALCULATING PATH TO: X:{self.goal_x:.2f}, Y:{self.goal_y:.2f}")

    def scan_callback(self, msg):
        self.lidar_ranges = msg.ranges
        self.update_grid_map()

    def update_grid_map(self):
        if not self.lidar_ranges:
            return
            
        for i, distance in enumerate(self.lidar_ranges):
            if 0.1 < distance < 5.0: 
                angle = self.current_yaw + (i * math.pi / 180.0)
                wall_x = self.current_x + (distance * math.cos(angle))
                wall_y = self.current_y + (distance * math.sin(angle))
                grid_x = int((wall_x / self.grid_resolution) + self.grid_offset)
                grid_y = int((wall_y / self.grid_resolution) + self.grid_offset)
                
                if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
                    self.map_grid[grid_x][grid_y] = 1

    def control_loop(self):
        cmd = Twist()
        if self.goal_x is None or self.goal_y is None:
            self.cmd_pub.publish(cmd)
            return
            
        distance_to_goal = math.sqrt((self.goal_x - self.current_x)**2 + (self.goal_y - self.current_y)**2)
        if distance_to_goal < 0.2:
            self.get_logger().info("DESTINATION REACHED! Engine Stop.")
            self.goal_x = None
            self.goal_y = None
            self.cmd_pub.publish(cmd)
            return

        angle_to_goal = math.atan2(self.goal_y - self.current_y, self.goal_x - self.current_x)
        heading_error = angle_to_goal - self.current_yaw
        
        while heading_error > math.pi: heading_error -= 2.0 * math.pi
        while heading_error < -math.pi: heading_error += 2.0 * math.pi

        attractive_force = heading_error * 1.0
        repulsive_force = 0.0
        
        if len(self.lidar_ranges) > 0:
            for i, distance in enumerate(self.lidar_ranges):
                if 0.1 < distance < 3.0: 
                    angle = (i * math.pi / 180.0)
                    while angle > math.pi: angle -= 2.0 * math.pi
                    
                    force_magnitude = (3.0 - distance) / 3.0 
                    if angle > 0: 
                        repulsive_force -= force_magnitude * 0.7
                    else: 
                        repulsive_force += force_magnitude * 0.7

        final_steering = attractive_force + repulsive_force
        final_steering = max(-1.5, min(1.5, final_steering))

        speed = 0.4 * (1.0 - abs(final_steering) / 2.0)
        speed = max(0.1, speed)

        cmd.linear.x = float(speed)
        cmd.angular.z = float(final_steering)
        self.cmd_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = PurePythonAIBrain()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()