#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO
import cv2
from rclpy.qos import qos_profile_sensor_data, QoSProfile, ReliabilityPolicy


class YoloPerceptionNode(Node):
    def __init__(self):
        super().__init__('yolo_perception_node')
        
        self.frame_count = 0
        
        self.get_logger().info("Loading YOLOv8 AI Model...")
        self.model = YOLO('yolov8n.pt')
        self.bridge = CvBridge()

        # 1. SUBSCRIBE TO THE REAL CAMERA TOPIC (/argus_camera/image_raw)
        self.subscription = self.create_subscription(
            Image,
            '/argus_camera/image_raw',
            self.image_callback,
            qos_profile_sensor_data
        )

        # 2. PUBLISH COMPATIBLE STREAM FOR RVIZ (Queue size 10, default Reliable)
        self.publisher = self.create_publisher(
            Image, 
            '/camera/yolo/image_raw', 
            10
        )
        self.get_logger().info("YOLOv8 Perception Node is ONLINE and listening to /argus_camera/image_raw")

    def image_callback(self, msg):
        # Process 1 out of every 5 frames for smooth performance
        self.frame_count += 1
        if self.frame_count % 5 != 0:
            return 

        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # Lower confidence to 0.15 for simulation objects
            results = self.model(cv_image, conf=0.15, verbose=False)
            
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    label = self.model.names[cls_id]
                    conf = float(box.conf[0])
                    self.get_logger().info(f"Target Spotted: {label} ({conf:.2f})")

            # Draw bounding boxes if objects detected
            if len(results) > 0 and len(results[0].boxes) > 0:
                annotated_frame = results[0].plot()
            else:
                annotated_frame = cv_image

            # Publish back to ROS 2
            ros_image = self.bridge.cv2_to_imgmsg(annotated_frame, "bgr8")
            self.publisher.publish(ros_image)

        except Exception as e:
            self.get_logger().error(f"Error processing image: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = YoloPerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()