#!/usr/bin/python3
"""Relay wheel odometry to /odom and publish odom→base_link TF."""

import rclpy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


class OdomRelay(Node):
    def __init__(self):
        super().__init__('odom_relay')
        self.declare_parameter('input_topic', '/odom/wheel')
        self.declare_parameter('output_topic', '/odom')
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')

        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value
        self._odom_frame = self.get_parameter('odom_frame').value
        self._base_frame = self.get_parameter('base_frame').value

        self._broadcaster = TransformBroadcaster(self)
        self._publisher = self.create_publisher(Odometry, output_topic, 10)
        self.create_subscription(Odometry, input_topic, self._on_odometry, 10)

    def _on_odometry(self, msg: Odometry):
        output = Odometry()
        output.header = msg.header
        output.header.frame_id = self._odom_frame
        output.child_frame_id = self._base_frame
        output.pose = msg.pose
        output.twist = msg.twist
        self._publisher.publish(output)

        transform = TransformStamped()
        transform.header = output.header
        transform.child_frame_id = self._base_frame
        transform.transform.translation.x = msg.pose.pose.position.x
        transform.transform.translation.y = msg.pose.pose.position.y
        transform.transform.translation.z = msg.pose.pose.position.z
        transform.transform.rotation = msg.pose.pose.orientation
        self._broadcaster.sendTransform(transform)


def main():
    rclpy.init()
    node = OdomRelay()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
