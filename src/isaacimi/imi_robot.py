from isaacsim.core.api.robots import Robot
from isaacsim.core.utils.stage import add_reference_to_stage

import numpy as np

class ImiRobot(Robot):
    def __init__(
        self,
        prim_path: str,
        name: str,
        usd_path: str,
        translation: np.ndarray,
        orientation: np.ndarray
    ) -> None:
        self._prim_path = prim_path
        self._name = name
        self._usd_path = usd_path
        self._initial_translation = translation
        self._initial_orientation = orientation
        add_reference_to_stage(usd_path=self._usd_path, prim_path=self._prim_path)
        super().__init__(prim_path=self._prim_path, name=self._name, position=self._initial_translation, orientation=self._initial_orientation, articulation_controller=None)
        return

    @property
    def name(self) -> str:
        return self._name