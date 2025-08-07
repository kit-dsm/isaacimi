import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter

class RosManager:
    """A static utility container for managing ROS nodes in the simulation.

    Note: One multi-threaded executor is used to execute all ROS nodes in the simulation.

    Warning: the RosManager is not instantiable
    """
    _nodes = {}
    _rclpy_init = False
    _executor = None

    def __new__(cls, *args, **kwargs):
        raise TypeError("Cannot instantiate RosManager")
    
    @classmethod
    def ensure_node(cls, robot_name: str) -> Node:
        """Return the ROS node corresponding to the specefied robot name in the simulation.

        If a ROS node does not exist for the specified robot, instantiate one and add it to the registry. Otherwise, return the existing node from the registry.

        Args:
            robot_name (str): the name of the robot the ROS node belongs to

        Returns:
            Node: the ROS node instance
        """
        if not cls._rclpy_init:
            rclpy.init()
            cls._executor = rclpy.executors.MultiThreadedExecutor()
            cls._rclpy_init = True
        if robot_name not in cls._nodes:
            node = Node(
                node_name = "isaacsim_node",
                namespace=f"/{robot_name}",
                cli_args=["--remap", "/tf:=tf", "--remap", "/tf_static:=tf_static"]
            )
            node.set_parameters([
                Parameter('use_sim_time', Parameter.Type.BOOL, True)
            ])
            cls._executor.add_node(node)
            cls._nodes[robot_name] = node
        return cls._nodes[robot_name]
    
    @classmethod
    def spin_once(cls) -> None:
        """Calls the `spin_once()` method on the multi-threaded executor.
        """
        if cls._rclpy_init:
            cls._executor.spin_once(timeout_sec=0)