#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import math

class AStarCommander(Node):
    def __init__(self):
        super().__init__('astar_commander')
        self.navigator = BasicNavigator()
        
        # Wait for AMCL and A* to boot up
        self.get_logger().info("Waiting for AMCL and Nav2 algorithms to initialize...")
        self.navigator.waitUntilNav2Active()
        self.get_logger().info("A* and DWB Algorithms Online! Ready for coordinates.")

    def send_robot_to_goal(self, x, y, theta):
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.navigator.get_clock().now().to_msg()
        
        # Set X, Y
        goal_pose.pose.position.x = x
        goal_pose.pose.position.y = y
        
        # Convert Theta to Quaternion
        goal_pose.pose.orientation.z = math.sin(theta / 2.0)
        goal_pose.pose.orientation.w = math.cos(theta / 2.0)

        # Send to the A* Planner
        self.get_logger().info(f"Sending A* Path Request to X: {x}, Y: {y}...")
        self.navigator.goToPose(goal_pose)

        # Monitor the D* dynamic obstacle avoidance as it drives
        while not self.navigator.isTaskComplete():
            feedback = self.navigator.getFeedback()
            if feedback:
                self.get_logger().info(f'Estimated time remaining: {feedback.estimated_time_remaining.sec} seconds.', throttle_duration_sec=2.0)

        result = self.navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info('Goal reached successfully using A* and DWB!')
        elif result == TaskResult.CANCELED:
            self.get_logger().warn('Path was canceled!')
        elif result == TaskResult.FAILED:
            self.get_logger().error('A* failed to find a valid path! Obstacles blocking all routes.')

def main(args=None):
    rclpy.init(args=args)
    commander = AStarCommander()
    
    # Send the robot to a coordinate in the room!
    commander.send_robot_to_goal(5.0, -1.0, 1.57)
    
    rclpy.shutdown()

if __name__ == '__main__':
    main()
