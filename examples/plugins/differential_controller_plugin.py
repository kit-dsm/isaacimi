from isaacimi.robot_plugin import ImiRobotPlugin

from geometry_msgs.msg import Twist, Quaternion, TransformStamped
from nav_msgs.msg import Odometry
from rclpy.time import Time
from tf2_ros import TransformBroadcaster

from isaacsim.robot.wheeled_robots.controllers.differential_controller import DifferentialController
from isaacsim.core.utils.types import ArticulationAction

import numpy as np

class DifferentialControllerPlugin(ImiRobotPlugin):   
    def on_plugin_load(self, namespace, topic_name, wheel_radius, wheel_base, left_wheel_joint_name, right_wheel_joint_name):
        self.ros_node.create_subscription(Twist, f"/{namespace}/{topic_name}", self.twist_cmd_callback, 1)
        self.lin_vel_cmd = np.zeros(3)
        self.ang_vel_cmd = np.zeros(3)
        self.diff_controller = DifferentialController(name="differential_controller", wheel_radius=wheel_radius, wheel_base=wheel_base)
        self.left_wheel_joint_name = left_wheel_joint_name
        self.right_wheel_joint_name = right_wheel_joint_name

        # to be inititialized in self.initialize() after physics has been initialized
        self.wheel_joint_indices = None
        self.num_joints = None
        self.curr_robot_action = None
        return

    def initialize(self, robot):
        self.wheel_joint_indices = [
            robot.get_dof_index(self.left_wheel_joint_name),
            robot.get_dof_index(self.right_wheel_joint_name)
        ]
        self.num_joints = robot.num_dof
        self.curr_robot_action = ArticulationAction()
        self.curr_robot_action.joint_positions = np.zeros(self.num_joints)
        self.curr_robot_action.joint_velocities = np.zeros(self.num_joints)
        self.curr_robot_action.joint_efforts = np.zeros(self.num_joints)
        return

    def twist_cmd_callback(self, data: Twist) -> None:
        self.lin_vel_cmd[0] = data.linear.x
        self.lin_vel_cmd[1] = data.linear.y
        self.lin_vel_cmd[2] = data.linear.z
        self.ang_vel_cmd[0] = data.angular.x
        self.ang_vel_cmd[1] = data.angular.y
        self.ang_vel_cmd[2] = data.angular.z
        return

    def pre_physics_step(self, robot, time_step_index, simulation_time):
        controller_action = self.diff_controller.forward(command=[self.lin_vel_cmd[0], self.ang_vel_cmd[2]])
        if controller_action is not None:
            self.curr_robot_action.joint_velocities[self.wheel_joint_indices[0]] = controller_action.joint_velocities[0]
            self.curr_robot_action.joint_velocities[self.wheel_joint_indices[1]] = controller_action.joint_velocities[1]
            robot.apply_action(control_actions=self.curr_robot_action)
        return