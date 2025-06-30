from typing import Optional
import numpy as np
from isaacsim.core.api.robots import Robot
from isaacsim.core.utils.stage import add_reference_to_stage

# test
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

# todo: look into using tasks instead of this custom RosRobot class

class RosRobot(Robot):
    def __init__(
        self,
        prim_path: str,
        name: str,
        usd_path: str,
        position: Optional[np.ndarray] = None,
        orientation: Optional[np.ndarray] = None
    ) -> None:
        add_reference_to_stage(usd_path=usd_path, prim_path=prim_path)
        super().__init__(
            prim_path=prim_path, name=name, position=position, orientation=orientation, articulation_controller=None
        )

        # test
        self.mynode = rclpy.create_node("my_node")
        self.vel_sub = self.mynode.create_subscription(Twist, "/cmd_vel", self.my_vel_callback, 1)
        self.lin_vel = np.zeros(3)
        self.ang_vel = np.zeros(3)

        return
    
    def __del__(self) -> None:
        print("DESTRUCTOR CALLED")
        return

    def initialize(self, physics_sim_view=None) -> None:
        super().initialize(physics_sim_view=physics_sim_view)
        print("INITIALIZE CALLED!!!") #todo
        return

    def post_reset(self) -> None:
        super().post_reset()
        print("POST RESET CALLED!!!") #todo
        return
    
    # test
    def post_step(self) -> None:
        rclpy.spin_once(self.mynode, timeout_sec=0.0)
        self.set_linear_velocity(self.lin_vel)
        self.set_angular_velocity(self.ang_vel)
        return

    def my_vel_callback(self, data):
        self.lin_vel[0] = data.linear.x
        self.lin_vel[1] = data.linear.y
        self.lin_vel[2] = data.linear.z
        self.ang_vel[0] = data.angular.x
        self.ang_vel[1] = data.angular.y
        self.ang_vel[2] = data.angular.z

class MyCustomNode(Node):
    def __init__(self):
        self.sub_velocity = self.create_subscription(Twist, "cmd_vel2", self.vel_callback, 10)

    def vel_callback(self, data):
        print("from other node: " + data)