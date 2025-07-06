from isaacimi.robot_plugin import ImiRobotPlugin

from geometry_msgs.msg import Twist
from std_msgs.msg import Int8

import numpy as np

class DummyRobotPlugin(ImiRobotPlugin):   
    def on_plugin_load(self):
        print("Dummy plugin loaded onto robot!")
        self.ros_node.create_subscription(Twist, "cmd_vel", self.velocity_callback, 1)
        self.lin_vel = np.zeros(3)
        self.ang_vel = np.zeros(3)

        self.ros_node.create_subscription(Int8, "cmd_lift", self.lift_callback, 1)
        self.cmd_lift = 0 # either -1, 0, or +1

        self.max_lift_moving_speed = 0.25
        self.lift_active = False    
        return

    def velocity_callback(self, data: Twist) -> None:
        self.lin_vel[0] = data.linear.x
        self.lin_vel[1] = data.linear.y
        self.lin_vel[2] = data.linear.z
        self.ang_vel[0] = data.angular.x
        self.ang_vel[1] = data.angular.y
        self.ang_vel[2] = data.angular.z
        return

    def lift_callback(self, data: Int8) -> None:
        self.cmd_lift = data.data
    
    def on_physics_step(self, robot, step_size) -> None:
        if self.cmd_lift == 0:
            self.lift_active = False
            robot.set_linear_velocity(self.lin_vel)
            robot.set_angular_velocity(self.ang_vel)
        else:
            self.lift_active = True
            if self.cmd_lift > 0:
                robot.set_joint_velocities(np.array([+self.max_lift_moving_speed]))
            else:
                robot.set_joint_velocities(np.array([-self.max_lift_moving_speed]))
            
        return