from isaacimi.robot_plugin import ImiRobotPlugin

from geometry_msgs.msg import Twist

from isaacsim.robot.wheeled_robots.controllers.differential_controller import DifferentialController
from isaacsim.core.utils.types import ArticulationAction

import numpy as np

class DifferentialControllerPlugin(ImiRobotPlugin):   
    def on_plugin_load(self, namespace, topic_name, wheel_radius, wheel_base, left_wheel_joint_name, right_wheel_joint_name):
        # create ROS subscriber
        self.ros_node.create_subscription(Twist, f"/{namespace}/{topic_name}", self.twist_cmd_callback, 1)
        
        # variables to store the Twist command
        self.lin_vel_cmd = np.zeros(3)
        self.ang_vel_cmd = np.zeros(3)

        # use differential controller class provided by Isaac Sim
        self.diff_controller = DifferentialController(name="differential_controller", wheel_radius=wheel_radius, wheel_base=wheel_base)

        # save the names of the left and right wheel joint to be used in the initialize method
        self.left_wheel_joint_name = left_wheel_joint_name
        self.right_wheel_joint_name = right_wheel_joint_name

        # variable to store the current ArticulationAction
        self.curr_robot_action = None

        # to be inititialized in self.initialize() after physics has been initialized
        self.left_wheel_joint_index = None
        self.right_wheel_joint_index = None
        self.num_joints = None
        return

    def initialize(self, robot):
        # get the joint index corresponding to the left and right wheel joints
        self.left_wheel_joint_index = robot.get_dof_index("left_wheel_joint")
        self.right_wheel_joint_index = robot.get_dof_index("right_wheel_joint")

        # get the number of joints on our robot
        self.num_joints = robot.num_dof

        # initialize the ArticulationAction object, ensuring it has the same length as the number of joints on our robot
        self.curr_robot_action = ArticulationAction()
        self.curr_robot_action.joint_positions = np.zeros(self.num_joints)
        self.curr_robot_action.joint_velocities = np.zeros(self.num_joints)
        self.curr_robot_action.joint_efforts = np.zeros(self.num_joints)
        return

    def twist_cmd_callback(self, data: Twist) -> None:
        # save twist command to variables
        self.lin_vel_cmd[0] = data.linear.x
        self.lin_vel_cmd[1] = data.linear.y
        self.lin_vel_cmd[2] = data.linear.z
        self.ang_vel_cmd[0] = data.angular.x
        self.ang_vel_cmd[1] = data.angular.y
        self.ang_vel_cmd[2] = data.angular.z
        return

    def pre_physics_step(self, robot, time_step_index, simulation_time):
        # use the DifferentialController class to calculate the joint velocity based on the Twist message
        # input: [signed linear speed, signed angular speed], output: [Left Drive, Right Drive] 
        controller_action = self.diff_controller.forward(command=[self.lin_vel_cmd[0], self.ang_vel_cmd[2]])

        if controller_action is not None:
            # populate the correct indices with the joint commands
            self.curr_robot_action.joint_velocities[self.left_wheel_joint_index] = controller_action.joint_velocities[0]
            self.curr_robot_action.joint_velocities[self.right_wheel_joint_index] = controller_action.joint_velocities[1]

            # apply the joint commands to the robot
            robot.apply_action(control_actions=self.curr_robot_action)
        return