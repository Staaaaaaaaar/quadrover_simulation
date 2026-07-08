#!/usr/bin/env python3
"""Normalize wheel odometry frame ids and optionally publish odom TF."""

from copy import deepcopy

import rclpy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


class WheelOdomNormalizer(Node):
    def __init__(self):
        super().__init__('wheel_odom_normalizer')

        self.declare_parameter('input_topic', '/odom/wheel_raw')
        self.declare_parameter('output_topic', '/odom/wheel')
        self.declare_parameter('odom_frame_id', 'odom')
        self.declare_parameter('base_frame_id', 'base_link')
        self.declare_parameter('publish_tf', False)

        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value
        self._odom_frame_id = self.get_parameter('odom_frame_id').value
        self._base_frame_id = self.get_parameter('base_frame_id').value
        self._publish_tf = self.get_parameter('publish_tf').value

        self._publisher = self.create_publisher(Odometry, output_topic, 20)
        self._subscriber = self.create_subscription(
            Odometry, input_topic, self._odom_callback, 20
        )
        self._tf_broadcaster = TransformBroadcaster(self) if self._publish_tf else None

    def _odom_callback(self, msg: Odometry):
        normalized = deepcopy(msg)
        normalized.header.frame_id = self._odom_frame_id
        normalized.child_frame_id = self._base_frame_id
        self._publisher.publish(normalized)

        if not self._tf_broadcaster:
            return

        transform = TransformStamped()
        transform.header.stamp = normalized.header.stamp
        transform.header.frame_id = self._odom_frame_id
        transform.child_frame_id = self._base_frame_id
        transform.transform.translation.x = normalized.pose.pose.position.x
        transform.transform.translation.y = normalized.pose.pose.position.y
        transform.transform.translation.z = normalized.pose.pose.position.z
        transform.transform.rotation = normalized.pose.pose.orientation
        self._tf_broadcaster.sendTransform(transform)


def main():
    rclpy.init()
    node = WheelOdomNormalizer()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
