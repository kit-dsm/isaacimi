from typing import Optional
import numpy as np
from abc import ABC, abstractmethod

from isaacsim.core.api.tasks import BaseTask
from isaacsim.core.api.scenes.scene import Scene
from isaacsim.core.api.robots import Robot

class ImiRobot(BaseTask):
    def __init__(
        self,
        prim_path: str,
        name: str,
        usd_path: str,
        position: np.ndarray,
        orientation: np.ndarray
    ) -> None:
        BaseTask.__init__(self, name=name+"_task", offset=None)
        self._robot = None
        self._robot_name = name
        self._robot_prim_path = prim_path
        self._robot_usd_path = usd_path
        self._robot_initial_position = position
        self._robot_initial_orientation = orientation
        return
    
    def setup_scene(self, scene: Scene):
        super().set_up_scene(scene)
        self.set_robot()
        scene.add(self._robot)
        return
    
    def set_robot(self) -> Robot:
        self._robot = Robot(prim_path=self._robot_prim_path, name=self._robot_name, position=self._robot_initial_position, orientation=self._robot_initial_orientation, articulation_controller=None)
        return self._robot
