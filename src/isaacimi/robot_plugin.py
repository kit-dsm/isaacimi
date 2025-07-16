from isaacsim.core.api.scenes.scene import Scene

from rclpy.node import Node

from .imi_robot import ImiRobot
from .ros_manager import RosManager

from abc import ABC, abstractmethod

class ImiRobotPlugin(ABC):
    def __init__(self, robot_name: str) -> None:
        """Constructs a robot plugin instance.

        Args:
            robot_name (str): the name of the robot that this plugin instance is loaded onto
        """
        self._robot_name = robot_name

    @property
    def ros_node(self) -> Node:
        """Return the ROS node associated with the robot that this plugin is loaded onto.

        Returns:
            Node: the ROS node instance
        """
        return RosManager.ensure_node(self._robot_name)

    @abstractmethod
    def on_plugin_load(self, *args, **kwargs) -> None:
        """Hook called when the plugin is loaded onto the robot.

        Any initialization required for the plugin should be done here.
        """
        return
    
    def set_up_scene(self, scene: Scene) -> None:
        """Called at the beginning of the simulation.

        Any custom modifications to the scene, such as adding assets, should be done here.

        Args:
            scene (Scene): the scene instance
        """
        return

    def cleanup(self) -> None:
        """Called before calling a `reset()` on the world to remove temporary objects that were added during
        simulation.

        Note: Any objects that were added during `set_up_scene()` should be removed here.
        """
        return
    
    def post_reset(self) -> None:
        """Called whenever `reset()` is called on the world.
        """
        return

    def pre_physics_step(self, robot: ImiRobot, time_step_index: int, simulation_time: float) -> None:
        """Called before every physics step.

        Args:
            robot (ImiRobot): the robot instance
            time_step_index (int): the current timestep the simulation is at
            simulation_time (float): the current time (in seconds) in the simulation
        """
        return

    def on_physics_step(self, robot: ImiRobot, step_size: float) -> None:
        """Called after every physics step.

        Args:
            robot (ImiRobot): the robot instance
            step_size (float): the size of the physics timestep in seconds
        """
        return
