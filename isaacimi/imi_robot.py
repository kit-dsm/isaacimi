from typing import Optional
import numpy as np
from abc import ABC, abstractmethod

from isaacsim.core.api.tasks import BaseTask
from isaacsim.core.api.scenes.scene import Scene
from isaacsim.core.api.robots import Robot
from isaacsim.core.utils.stage import add_reference_to_stage

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
    
    def set_up_scene(self, scene: Scene) -> None:
        super().set_up_scene(scene)
        add_reference_to_stage(usd_path=self._robot_usd_path, prim_path=self._robot_prim_path)
        self.set_robot()
        return
    
    def set_robot(self) -> Robot:
        if self._robot is None:
            self._robot = Robot(prim_path=self._robot_prim_path, name=self._robot_name, position=self._robot_initial_position, orientation=self._robot_initial_orientation, articulation_controller=None)
        return self._robot
    
    def post_reset(self) -> None:
        # maybe: get the user to optionally implement Robot class
        # self._robot.post_reset()
        self._robot.set_angular_velocity(np.array([0, 0, 0]))
        self._robot.set_linear_velocity(np.array([0, 0, 0]))
        self._robot.set_local_pose(self._robot_initial_position, self._robot_initial_orientation)
        return