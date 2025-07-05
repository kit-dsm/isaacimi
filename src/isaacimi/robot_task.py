from isaacsim.core.api.tasks import BaseTask
from isaacsim.core.api.scenes.scene import Scene

# import rclpy

from typing import List

from .robot_plugin import ImiRobotPlugin
from .imi_robot import ImiRobot

class ImiRobotTask(BaseTask):
    def __init__(self, robot: ImiRobot, robot_plugins: List[ImiRobotPlugin] = []) -> None:
        super().__init__(name=robot.get_name()+"_task", offset=None)
        self._robot = robot
        self.plugins = robot_plugins
        return
    
    def add_plugin(self, plugin: ImiRobotPlugin) -> None:
        self.plugins.append(plugin)
        return

    def set_up_scene(self, scene: Scene):
        super().set_up_scene(scene)
        scene.add(self._robot)
        for plugin in self.plugins:
            plugin.set_up_scene(scene)
        return
    
    def post_reset(self) -> None:
        for plugin in self.plugins:
            plugin.post_reset()
        return

    def cleanup(self) -> None:
        for plugin in self.plugins:
            plugin.cleanup()
        return
    
    def pre_step(self) -> None:
        # todo: spin ros_nodes
        for plugin in self.plugins:
            plugin.pre_physics_step(self._robot)
        return

    def on_physics_step(self, step_size: float) -> None:
        for plugin in self.plugins:
            plugin.post_physics_step(self._robot, step_size)
        return

    
