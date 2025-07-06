# from typing import Optional, Callable, Union, TypeVar, Any, TYPE_CHECKING
# import numpy as np

# from isaacsim.core.api.tasks import BaseTask
from isaacsim.core.api.scenes.scene import Scene
# from isaacsim.core.api.robots import Robot
# from isaacsim.core.utils.stage import add_reference_to_stage

# import rclpy
from rclpy.node import Node

from .imi_robot import ImiRobot
from .ros_manager import RosManager

# if TYPE_CHECKING:
#     from rclpy.callback_groups import CallbackGroup
#     from rclpy.qos import QoSProfile
#     from rclpy.subscription import Subscription
#     from rclpy.publisher import Publisher

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

# class ImiRobotPlugin(BaseTask):
#     def __init__(
#         self,
#         prim_path: str,
#         name: str,
#         usd_path: str,
#         position: np.ndarray,
#         orientation: np.ndarray
#     ) -> None:
#         BaseTask.__init__(self, name=name+"_task", offset=None)
#         self._robot = None
#         self._robot_name = name
#         self._robot_prim_path = prim_path
#         self._robot_usd_path = usd_path
#         self._robot_initial_position = position
#         self._robot_initial_orientation = orientation
#         self._ros_node = None
#         return
    
#     def set_up_scene(self, scene: Scene) -> None:
#         super().set_up_scene(scene)
#         add_reference_to_stage(usd_path=self._robot_usd_path, prim_path=self._robot_prim_path)
#         self.set_robot()
#         scene.add(self._robot) # needs to be called to create a Physics Simulation View and initialize Articulation
#         return
    
#     def set_robot(self) -> Robot:
#         if self._robot is None:
#             self._robot = Robot(prim_path=self._robot_prim_path, name=self._robot_name, position=self._robot_initial_position, orientation=self._robot_initial_orientation, articulation_controller=None)
#         return self._robot
    
#     def post_reset(self) -> None:
#         self._robot.post_reset()
#         return
    
#     def pre_step(self, time_step_index: int, simulation_time: float) -> None:
#         if self._ros_node is not None:
#             rclpy.spin_once(self._ros_node, timeout_sec=0)
#         self.custom_pre_step()
#         return
    
#     def _get_ros_node(self) -> Node:
#         if self._ros_node is None:
#             self._ros_node = rclpy.create_node(self._robot_name + "_node")
#         return self._ros_node
            
#     def add_ros_subscriber(
#         self,
#         msg_type,
#         topic: str,
#         callback: Callable[[Any], None],
#         qos_profile: Union['QoSProfile', int],
#         *,
#         callback_group: Optional['CallbackGroup'] = None,
#     ) -> 'Subscription':
#         return self._get_ros_node().create_subscription(msg_type, f"/{self._robot_name}/{topic}", callback, qos_profile, callback_group=callback_group)

#     def add_ros_publisher(
#         self,
#         msg_type,
#         topic: str,
#         qos_profile: Union['QoSProfile', int],
#     ) -> 'Publisher':
#         return self._get_ros_node().create_publisher(msg_type, f"/{self._robot_name}/{topic}", qos_profile)
    
#     def custom_pre_step(self) -> None:
#         return