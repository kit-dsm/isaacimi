from isaacsim.core.api.tasks import BaseTask
from isaacsim.core.api.scenes.scene import Scene

# import rclpy

from typing import List

from .robot_plugin import ImiRobotPlugin
from .imi_robot import ImiRobot

class ImiRobotTask(BaseTask):
    """A class that extends from Isaac Sim's BaseTask.
    
    Tasks in Isaac Sim are a way to modularize the scene creation, information retrieval, calculating metrics and creating more complex scenes with more involved logic.
    The ImiRobotTask class is meant to encapsulate all programming logic related to a single robot in the simulation.

    Note: Each robot spawned into the simulation by Isaac IMI, along with it's plugins, ros node, resources, etc. become part of a single task instance that is added to the world via world.add_task() 
    """
    def __init__(self, robot: ImiRobot, robot_plugins: List[ImiRobotPlugin] = []) -> None:
        """Create an instance of ImiRobotTask.

        Calls the __init__ for the BaseTask and loads all plugins that were passed in as arguments.

        Args:
            robot (ImiRobot): the robot instance contained in this task
            robot_plugins (List[ImiRobotPlugin], optional): the plugin instances to be loaded onto the robot. Defaults to [].
        """
        super().__init__(name=f"{robot.name}_task", offset=None)
        self._robot = robot
        self._plugins = robot_plugins
        for plugin in self._plugins:
            plugin.on_plugin_load()
        return
    
    def add_plugin(self, plugin: ImiRobotPlugin) -> None:
        """Loads a plugin onto the robot.

        Args:
            plugin (ImiRobotPlugin): the plugin to be loaded
        """
        self._plugins.append(plugin)
        plugin.on_plugin_load()
        return

    def set_up_scene(self, scene: Scene):
        """Adds the ImiRobot instance to the scene and calls `set_up_scene()` for all plugins loaded onto the robot

        Args:
            scene (Scene): the scene instance
        """
        super().set_up_scene(scene)
        scene.add(self._robot)
        for plugin in self._plugins:
            plugin.set_up_scene(scene)
        return
    
    def post_reset(self) -> None:
        """Calls `post_reset()` for all plugins loaded on the robot.
        """
        for plugin in self._plugins:
            plugin.post_reset()
        return

    def cleanup(self) -> None:
        """Calls `cleanup()` for all plugins loaded on the robot.
        """
        for plugin in self._plugins:
            plugin.cleanup()
        return
    
    def pre_step(self, time_step_index: int, simulation_time: float) -> None:
        """Calls `pre_physics_step()` for all plugins loaded on the robot.

        Args:
            time_step_index (int): the current timestep the simulation is at
            simulation_time (float): the current time (in seconds) in the simulation
        """
        for plugin in self._plugins:
            plugin.pre_physics_step(self._robot, time_step_index, simulation_time)
        return

    def on_physics_step(self, step_size: float) -> None:
        """Calls `on_physics_step()` for all plugins loaded on the robot.

        Args:
            step_size (float): the size of the physics timestep in seconds
        """
        for plugin in self._plugins:
            plugin.on_physics_step(self._robot, step_size)
        return

    
