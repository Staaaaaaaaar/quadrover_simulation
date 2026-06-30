#!/usr/bin/python3
"""Publish map TF from ground-truth odometry with adaptive frame selection."""

import math

import rclpy
from geometry_msgs.msg import Transform, TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from tf2_ros import Buffer, TransformBroadcaster, TransformListener


def _transform_to_matrix(transform: Transform):
    x = transform.rotation.x
    y = transform.rotation.y
    z = transform.rotation.z
    w = transform.rotation.w
    xx = x * x
    yy = y * y
    zz = z * z
    xy = x * y
    xz = x * z
    yz = y * z
    wx = w * x
    wy = w * y
    wz = w * z

    return [
        [1.0 - 2.0 * (yy + zz), 2.0 * (xy - wz), 2.0 * (xz + wy), transform.translation.x],
        [2.0 * (xy + wz), 1.0 - 2.0 * (xx + zz), 2.0 * (yz - wx), transform.translation.y],
        [2.0 * (xz - wy), 2.0 * (yz + wx), 1.0 - 2.0 * (xx + yy), transform.translation.z],
        [0.0, 0.0, 0.0, 1.0],
    ]


def _invert_matrix(matrix):
    rotation = [
        [matrix[0][0], matrix[1][0], matrix[2][0]],
        [matrix[0][1], matrix[1][1], matrix[2][1]],
        [matrix[0][2], matrix[1][2], matrix[2][2]],
    ]
    translation = [matrix[0][3], matrix[1][3], matrix[2][3]]
    inv_translation = [
        -(rotation[0][0] * translation[0] + rotation[0][1] * translation[1] + rotation[0][2] * translation[2]),
        -(rotation[1][0] * translation[0] + rotation[1][1] * translation[1] + rotation[1][2] * translation[2]),
        -(rotation[2][0] * translation[0] + rotation[2][1] * translation[1] + rotation[2][2] * translation[2]),
    ]
    return [
        [rotation[0][0], rotation[0][1], rotation[0][2], inv_translation[0]],
        [rotation[1][0], rotation[1][1], rotation[1][2], inv_translation[1]],
        [rotation[2][0], rotation[2][1], rotation[2][2], inv_translation[2]],
        [0.0, 0.0, 0.0, 1.0],
    ]


def _multiply_matrix(a, b):
    result = [[0.0] * 4 for _ in range(4)]
    for row in range(4):
        for col in range(4):
            result[row][col] = sum(a[row][k] * b[k][col] for k in range(4))
    return result


def _matrix_to_transform(matrix):
    transform = Transform()
    transform.translation.x = matrix[0][3]
    transform.translation.y = matrix[1][3]
    transform.translation.z = matrix[2][3]

    trace = matrix[0][0] + matrix[1][1] + matrix[2][2]
    if trace > 0.0:
        s = math.sqrt(trace + 1.0) * 2.0
        transform.rotation.w = 0.25 * s
        transform.rotation.x = (matrix[2][1] - matrix[1][2]) / s
        transform.rotation.y = (matrix[0][2] - matrix[2][0]) / s
        transform.rotation.z = (matrix[1][0] - matrix[0][1]) / s
    elif matrix[0][0] > matrix[1][1] and matrix[0][0] > matrix[2][2]:
        s = math.sqrt(1.0 + matrix[0][0] - matrix[1][1] - matrix[2][2]) * 2.0
        transform.rotation.w = (matrix[2][1] - matrix[1][2]) / s
        transform.rotation.x = 0.25 * s
        transform.rotation.y = (matrix[0][1] + matrix[1][0]) / s
        transform.rotation.z = (matrix[0][2] + matrix[2][0]) / s
    elif matrix[1][1] > matrix[2][2]:
        s = math.sqrt(1.0 + matrix[1][1] - matrix[0][0] - matrix[2][2]) * 2.0
        transform.rotation.w = (matrix[0][2] - matrix[2][0]) / s
        transform.rotation.x = (matrix[0][1] + matrix[1][0]) / s
        transform.rotation.y = 0.25 * s
        transform.rotation.z = (matrix[1][2] + matrix[2][1]) / s
    else:
        s = math.sqrt(1.0 + matrix[2][2] - matrix[0][0] - matrix[1][1]) * 2.0
        transform.rotation.w = (matrix[1][0] - matrix[0][1]) / s
        transform.rotation.x = (matrix[0][2] + matrix[2][0]) / s
        transform.rotation.y = (matrix[1][2] + matrix[2][1]) / s
        transform.rotation.z = 0.25 * s

    return transform


class MapTfBroadcaster(Node):
    def __init__(self):
        super().__init__('map_tf_broadcaster')
        self.declare_parameter('ground_truth_topic', '/odom/ground_truth')
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('odom_tf_timeout', 0.1)

        self._map_frame = self.get_parameter('map_frame').value
        self._odom_frame = self.get_parameter('odom_frame').value
        self._base_frame = self.get_parameter('base_frame').value
        self._odom_tf_timeout = self.get_parameter('odom_tf_timeout').value

        self._broadcaster = TransformBroadcaster(self)
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self)
        self._latest_ground_truth = None

        ground_truth_topic = self.get_parameter('ground_truth_topic').value
        self.create_subscription(
            Odometry,
            ground_truth_topic,
            self._on_ground_truth,
            10,
        )
        self.create_timer(1.0 / 30.0, self._publish_map_tf)

    def _on_ground_truth(self, msg: Odometry):
        self._latest_ground_truth = msg

    def _publish_map_tf(self):
        if self._latest_ground_truth is None:
            return

        msg = self._latest_ground_truth
        stamp = msg.header.stamp

        if self._has_odom_to_base_link(stamp):
            try:
                odom_to_base = self._tf_buffer.lookup_transform(
                    self._odom_frame,
                    self._base_frame,
                    stamp,
                )
            except Exception:
                self._publish_map_to_base_link(msg)
                return

            map_to_base = self._odom_to_transform(msg, self._map_frame, self._base_frame)
            t_map_base = _transform_to_matrix(map_to_base.transform)
            t_odom_base = _transform_to_matrix(odom_to_base.transform)
            t_map_odom = _multiply_matrix(t_map_base, _invert_matrix(t_odom_base))

            map_to_odom = TransformStamped()
            map_to_odom.header.stamp = stamp
            map_to_odom.header.frame_id = self._map_frame
            map_to_odom.child_frame_id = self._odom_frame
            map_to_odom.transform = _matrix_to_transform(t_map_odom)
            self._broadcaster.sendTransform(map_to_odom)
        else:
            self._publish_map_to_base_link(msg)

    def _has_odom_to_base_link(self, stamp) -> bool:
        return self._tf_buffer.can_transform(
            self._odom_frame,
            self._base_frame,
            stamp,
            timeout=rclpy.duration.Duration(seconds=self._odom_tf_timeout),
        )

    def _publish_map_to_base_link(self, msg: Odometry):
        transform = self._odom_to_transform(msg, self._map_frame, self._base_frame)
        self._broadcaster.sendTransform(transform)

    @staticmethod
    def _odom_to_transform(msg: Odometry, parent_frame: str, child_frame: str):
        transform = TransformStamped()
        transform.header = msg.header
        transform.header.frame_id = parent_frame
        transform.child_frame_id = child_frame
        transform.transform.translation.x = msg.pose.pose.position.x
        transform.transform.translation.y = msg.pose.pose.position.y
        transform.transform.translation.z = msg.pose.pose.position.z
        transform.transform.rotation = msg.pose.pose.orientation
        return transform


def main():
    rclpy.init()
    node = MapTfBroadcaster()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
