import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter

class RosManager:
    _nodes = {}
    _rclpy_init = False
    _executor = None

    def __new__(cls, *args, **kwargs):
        raise TypeError("Cannot instantiate RosManager")
    
    @classmethod
    def ensure_node(cls, robot_name: str) -> Node:
        if not cls._rclpy_init:
            rclpy.init()
            cls._executor = rclpy.executors.MultiThreadedExecutor()
            cls._rclpy_init = True
        if robot_name not in cls._nodes:
            node = Node(f"{robot_name}_node")
            node.set_parameters([
                Parameter('use_sim_time', Parameter.Type.BOOL, True)
            ])
            cls._executor.add_node(node)
            cls._nodes[robot_name] = node
        return cls._nodes[robot_name]
    
    @classmethod
    def spin_once(cls) -> None:
        if cls._rclpy_init:
            cls._executor.spin_once(timeout_sec=0)