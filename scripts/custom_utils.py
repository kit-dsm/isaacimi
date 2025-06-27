from typing import Optional
import numpy as np
from isaacsim.core.api.robots import Robot
from isaacsim.core.utils.stage import add_reference_to_stage

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
        print(f"initializing ros robot {name}!")
        return
