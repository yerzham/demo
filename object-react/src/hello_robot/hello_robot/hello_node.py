#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import socket
import os
import sys
import time
import json
from booster_robotics_sdk_python import (
    B1HandAction,
    B1LocoClient,
    ChannelFactory,
    RobotMode,
)


class HelloNode(Node):
    def __init__(self, network_interface):
        super().__init__("hello_node")

        # Basic info
        self.hostname = socket.gethostname()
        self.deployment_version = self.get_deployment_version()

        # Subscribe to detections topic
        self.detections_sub = self.create_subscription(
            String, "/detections", self.detections_callback, 10
        )

        # Robot SDK setup
        self.get_logger().info(
            f"Initializing robot client on interface: {network_interface}"
        )
        ChannelFactory.Instance().Init(0, network_interface)
        self.robot_client = B1LocoClient()
        self.robot_client.Init()

        # Detection state
        self.last_wave_time = 0
        self.wave_cooldown = 5.0  # seconds between waves
        self.person_detected = False
        self.last_detection_time = 0
        self.detection_timeout = 2.0  # seconds

        # Status publisher
        self.status_publisher = self.create_publisher(String, "hello_topic", 10)
        self.timer = self.create_timer(1.0, self.status_callback)

        self.get_logger().info(f"Hello Node started on {self.hostname}")
        self.get_logger().info(f"Deployment version: {self.deployment_version}")
        self.get_logger().info("Subscribed to /detections topic")

        # Set robot to prepare mode
        res = self.robot_client.ChangeMode(RobotMode.kPrepare)
        if res != 0:
            self.get_logger().error(f"Failed to set robot to prepare mode: {res}")
        else:
            self.get_logger().info("Robot set to prepare mode")

    def get_deployment_version(self):
        """Read deployment version from file if exists"""
        version_file = os.path.expanduser("~/ros2_ws/.deployment_version")
        if os.path.exists(version_file):
            with open(version_file, "r") as f:
                return f.read().strip()
        return "unknown"

    def detections_callback(self, msg):
        """Process detections from /detections topic"""
        try:
            # Parse the JSON string
            detections = json.loads(msg.data)
            
            # Check if person is detected
            person_found = self.check_for_person(detections)

            if person_found:
                self.handshake()
            else:
                self.cancel_handshake()

        except json.JSONDecodeError as e:
            self.get_logger().error(f"Error parsing detections JSON: {str(e)}")
        except Exception as e:
            self.get_logger().error(f"Error processing detections: {str(e)}")

    def check_for_person(self, detections):
        """Check if there is a person in the detections"""
        if not isinstance(detections, list):
            return False
            
        for detection in detections:
            # Person class_id is 0 in COCO dataset (used by YOLO)
            if detection.get("class_id") == 0 and detection.get("confidence", 0) > 0.5:
                return True
        return False

    def wave_hand(self):
        """Make the robot wave its hand"""
        try:
            # Open hand
            res = self.robot_client.WaveHand(B1HandAction.kHandOpen)
            time.sleep(0.5)
            if res != 0:
                self.get_logger().error(f"Failed to open hand: {res}")
                return


        except Exception as e:
            self.get_logger().error(f"Error waving hand: {str(e)}")

    def cancel_wave(self):
        """Cancel the wave hand action"""
        try:
            res = self.robot_client.WaveHand(B1HandAction.kHandClose)
            time.sleep(0.5)
            if res != 0:
                self.get_logger().error(f"Failed to cancel wave hand: {res}")
                return

            
        except Exception as e:
            self.get_logger().error(f"Error canceling wave hand: {str(e)}")

    def handshake(self):
        """Make the robot shake hands"""
        try:
            res = self.robot_client.Handshake(B1HandAction.kHandOpen)
            time.sleep(0.5)
            if res != 0:
                self.get_logger().error(f"Failed to shake hands: {res}")
                return

        except Exception as e:
            self.get_logger().error(f"Error shaking hands: {str(e)}")

    def cancel_handshake(self):
        """Cancel the handshake action"""
        try:
            res = self.robot_client.Handshake(B1HandAction.kHandClose)
            time.sleep(0.5)
            if res != 0:
                self.get_logger().error(f"Failed to cancel handshake: {res}")
                return

        except Exception as e:
            self.get_logger().error(f"Error canceling handshake: {str(e)}")

    def status_callback(self):
        """Publish status information"""
        msg = String()
        status = "PERSON DETECTED" if self.person_detected else "No person detected"
        msg.data = (
            f"Robot: {self.hostname} (v{self.deployment_version}) - Status: {status}"
        )
        self.status_publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    # Get network interface from environment variable or default
    network_interface = os.environ.get("ROBOT_NETWORK_INTERFACE", "eth0")

    # Allow override from command line
    if len(sys.argv) > 1:
        network_interface = sys.argv[1]

    node = HelloNode(network_interface)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
