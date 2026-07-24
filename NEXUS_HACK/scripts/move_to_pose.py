#!/usr/bin/env python3

import os
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from nav2_msgs.action import NavigateToPose

CHECK_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "./check_file.txt")) 


class Navigator(Node):

    def __init__(self):
        super().__init__("navigator")

        self.nav_client = ActionClient(
            self,
            NavigateToPose,
            "/navigate_to_pose"
        )

        self.status = None

    def send_goal(self, goal_x, goal_y):

        self.get_logger().info(
            f"Sending Goal: x={goal_x}, y={goal_y}"
        )

        goal_msg = NavigateToPose.Goal()

        goal_msg.pose.header.frame_id = "odom"

        goal_msg.pose.pose.position.x = float(goal_x)
        goal_msg.pose.pose.position.y = float(goal_y)
        goal_msg.pose.pose.position.z = 0.0

        goal_msg.pose.pose.orientation.x = 0.0
        goal_msg.pose.pose.orientation.y = 0.0
        goal_msg.pose.pose.orientation.z = 0.0
        goal_msg.pose.pose.orientation.w = 1.0

        self.nav_client.wait_for_server()

        future = self.nav_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback,
        )

        future.add_done_callback(
            self.goal_response_callback
        )

    def goal_response_callback(self, future):

        goal_handle = future.result()

        if not goal_handle.accepted:

            self.get_logger().error("Goal Rejected")

            self.status = 0

            rclpy.shutdown()

            return

        self.get_logger().info("Goal Accepted")

        result_future = goal_handle.get_result_async()

        result_future.add_done_callback(
            self.result_callback
        )

    def feedback_callback(self, feedback_msg):

        try:
            distance = feedback_msg.feedback.distance_remaining

            self.get_logger().info(
                f"Distance Remaining: {distance:.2f}"
            )

        except Exception:
            pass

    def result_callback(self, future):

        result = future.result()

        if result.status == 4:  # STATUS_SUCCEEDED

            self.get_logger().info(
                "Goal reached successfully!"
            )

            self.status = 1

        else:

            self.get_logger().error(
                f"Navigation failed. Status={result.status}"
            )

            self.status = 0

        rclpy.shutdown()


def main(args=None):

    while True:

        try:

            with open(CHECK_FILE, "r") as f:
                data = f.read().strip().split()

            if len(data) < 3:
                time.sleep(0.1)
                continue

            status_flag = data[0]

            if status_flag != "True":
                time.sleep(0.1)
                continue

            goal_x = float(data[1])
            goal_y = float(data[2])

            print(f"Received Goal: {goal_x}, {goal_y}")

            rclpy.init(args=args)

            navigator = Navigator()

            navigator.send_goal(goal_x, goal_y)

            rclpy.spin(navigator)

            nav_status = navigator.status

            navigator.destroy_node()

            ret_status = (
                True if nav_status == 1 else False
            )

            with open(CHECK_FILE, "w") as f:
                f.write(
                    f"False {goal_x} {goal_y} {ret_status}"
                )

            print(
                f"Wrote: False {goal_x} {goal_y} {ret_status}"
            )

        except Exception as e:

            print(f"Error: {e}")

        time.sleep(0.1)


if __name__ == "__main__":
    main()