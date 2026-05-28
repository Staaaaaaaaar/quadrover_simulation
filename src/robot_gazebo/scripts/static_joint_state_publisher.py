#!/usr/bin/env python3
"""Publish empty joint states for robots with only fixed joints."""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class StaticJointStatePublisher(Node):
    def __init__(self):
        super().__init__('static_joint_state_publisher')
        self.declare_parameter('rate', 30.0)
        rate = self.get_parameter('rate').get_parameter_value().double_value
        self._publisher = self.create_publisher(JointState, 'joint_states', 10)
        self._timer = self.create_timer(1.0 / rate, self._publish)

    def _publish(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        self._publisher.publish(msg)


def main():
    rclpy.init()
    node = StaticJointStatePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
