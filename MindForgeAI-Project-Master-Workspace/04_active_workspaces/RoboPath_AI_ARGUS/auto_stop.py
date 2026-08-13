import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class AutoStopNode(Node):
    def __init__(self):
        super().__init__('auto_stop_node')
        # This talks to the wheels
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        # This listens to the LiDAR eyes
        self.subscription = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.get_logger().info("AI Brain Activated! Driving forward...")

    def scan_callback(self, msg):
        # Look at the lasers pointing directly in front of the robot (a 30-degree cone)
        front_lasers = msg.ranges[0:15] + msg.ranges[-15:]
        min_distance = min(front_lasers)

        cmd = Twist()
        
        # If an obstacle is closer than 1.0 meter, STOP!
        if min_distance < 1.0:
            self.get_logger().info(f"Obstacle at {min_distance:.2f} meters! SLAMMING BRAKES!")
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
        # Otherwise, keep driving forward safely
        else:
            cmd.linear.x = 0.4
            cmd.angular.z = 0.0

        # Send the command to the wheels
        self.publisher_.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = AutoStopNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
