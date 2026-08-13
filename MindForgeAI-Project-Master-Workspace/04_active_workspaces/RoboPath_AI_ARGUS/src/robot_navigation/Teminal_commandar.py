#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped

class TerminalCommander(Node):
    def __init__(self):
        super().__init__('terminal_commander')
        self.publisher_ = self.create_publisher(PoseStamped, '/goal_pose', 10)
        self.get_logger().info("Terminal Commander Online! Bypassing RViz.")

    def send_goal(self, x, y):
        msg = PoseStamped()
        msg.header.frame_id = 'odom'
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.pose.position.x = float(x)
        msg.pose.position.y = float(y)
        msg.pose.orientation.w = 1.0 # Point straight ahead
        
        self.publisher_.publish(msg)
        self.get_logger().info(f"Target sent to AI Brain -> X: {x}, Y: {y}")

def main(args=None):
    rclpy.init(args=args)
    node = TerminalCommander()
    
    try:
        while rclpy.ok():
            print("\n" + "="*35)
            print(" 🚀 ARGUS TERMINAL COMMAND CENTER")
            print("="*35)
            user_x = input("Enter X coordinate (e.g., 4.0): ")
            user_y = input("Enter Y coordinate (e.g., -2.0): ")
            
            try:
                node.send_goal(user_x, user_y)
            except ValueError:
                print("Error: Please type numbers only!")
                
    except KeyboardInterrupt:
        print("\nShutting down Command Center...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()