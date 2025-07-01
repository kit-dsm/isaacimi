from isaacimi import ImiRobot

from geometry_msgs.msg import Twist

import numpy as np

class DummyTask(ImiRobot):
    def __init__(
        self,
        prim_path,
        name,
        usd_path,
        position,
        orientation
    ):
        super().__init__(prim_path, name, usd_path, position, orientation)
        self.add_ros_subscriber(Twist, "cmd_vel", self.velocity_callback, 1)
        self.lin_vel = np.zeros(3)
        self.ang_vel = np.zeros(3)
        return
    
    def velocity_callback(self, data: Twist) -> None:
        self.lin_vel[0] = data.linear.x
        self.lin_vel[1] = data.linear.y
        self.lin_vel[2] = data.linear.z
        self.ang_vel[0] = data.angular.x
        self.ang_vel[1] = data.angular.y
        self.ang_vel[2] = data.angular.z
        return
    
    def custom_pre_step(self) -> None:
        self._robot.set_linear_velocity(self.lin_vel)
        self._robot.set_angular_velocity(self.ang_vel)
        return