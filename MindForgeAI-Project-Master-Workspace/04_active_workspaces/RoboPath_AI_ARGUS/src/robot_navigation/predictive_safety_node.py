#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import math

class PredictiveSafetyNode(Node):
    def __init__(self):
        super().__init__('predictive_safety_node')
        
        # Subscribe to the LiDAR
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            rclpy.qos.qos_profile_sensor_data)
            
        # Publisher to override the wheels if needed
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel_override', 10)
        
        # We listen to what Nav2 WANTS to do
        self.nav_sub = self.create_subscription(
            Twist,
            '/cmd_vel_nav',
            self.nav_cmd_callback,
            10)

        self.get_logger().info("Predictive Safety Node Active: Scanning forward arc...")
        self.obstacle_detected = False
        self.current_nav_cmd = Twist()

    def nav_cmd_callback(self, msg):
        self.current_nav_cmd = msg
        
        # If no obstacle, pass the Nav2 smooth curves directly to the wheels
        if not self.obstacle_detected:
            self.cmd_pub.publish(self.current_nav_cmd)

    def scan_callback(self, msg):
        # We only care about the rays pointing FORWARD (a 60-degree cone in front of the robot)
        # 360 rays total, 1 ray per degree. Front is index 0.
        # We check index 0-30 and 330-359.
        
        forward_rays = msg.ranges[:30] + msg.ranges[-30:]
        
        emergency_stop = False
        
        for distance in forward_rays:
            # Ignore infinity or errors
            if distance > 0.1 and distance != float('inf'):
                # 4.0 meters is the planning range, but 1.0 meter is the HARD STOP reflex
                if distance < 1.0: 
                    emergency_stop = True
                    break
                    
        if emergency_stop:
            if not self.obstacle_detected:
                self.get_logger().warn("OBSTACLE IN FRONT! Hard braking. Nav2 will replan.")
                self.obstacle_detected = True
                
            # Send zero velocity to stop the wheels instantly
            stop_msg = Twist()
            stop_msg.linear.x = 0.0
            stop_msg.angular.z = 0.0
            self.cmd_pub.publish(stop_msg)
        else:
            if self.obstacle_detected:
                self.get_logger().info("Path clear. Resuming smooth trajectory.")
            self.obstacle_detected = False

def main(args=None):
    rclpy.init(args=args)
    safety_node = PredictiveSafetyNode()
    rclpy.spin(safety_node)
    safety_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()