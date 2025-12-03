from isaacsim.core.api.robots import Robot
from isaacsim.core.utils.stage import add_reference_to_stage

import numpy as np

class ImiRobot(Robot):
    """A class that extends from Isaac Sim's Robot class.

    An instance of the ImiRobot class represents an individual robot in simulation.

    Note: When a simulation is run, each robot listed in the yaml blueprint is spawned by creating an instance of the ImiRobot class.
    """
    def __init__(
        self,
        prim_path: str,
        name: str,
        usd_path: str,
        translation: np.ndarray,
        orientation: np.ndarray
    ) -> None:
        """Calls the base Robot constructor and adds the provided usd_path as a reference to the stage.

        Args:
            prim_path (str): prim path of the Prim to encapsulate or create
            name (str): shortname to be used as a key by the Scene class and as an identifier by plugins and the RosManager
                        Note: must be unique
            usd_path (str): the path to the usd file to load into the stage as a reference
            translation (np.ndarray): translation in the local frame of the prim
            orientation (np.ndarray): quaternion orientation in the local frame of the prim
        """
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
        """Return the name of the robot, as specified as an argument in the __init__ method.

        Returns:
            str: the name of the robot
        """
        return self._name