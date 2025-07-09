from isaacsim.core.api.scenes.scene import Scene

from rclpy.node import Node

from .imi_robot import ImiRobot
from .ros_manager import RosManager


class ImiRobotPlugin:
    def __init__(self, robot_name: str) -> None:
        self._robot_name = robot_name

    @property
    def ros_node(self) -> Node:
        return RosManager.ensure_node(self._robot_name)

    def on_plugin_load(self) -> None:
        return
    
    def set_up_scene(self, scene: Scene) -> None:
        return

    def post_reset(self) -> None:
        return

    def cleanup(self) -> None:
        return

    def pre_physics_step(self, robot: ImiRobot, time_step_index: int, simulation_time: float) -> None:
        return

    def on_physics_step(self, robot: ImiRobot, step_size: float) -> None:
        return
