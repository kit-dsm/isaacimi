from rclpy.node import Node

class RosManager:
    _nodes = {}

    def __new__(cls, *args, **kwargs):
        raise TypeError("Cannot instantiate RosManager")
    
    @classmethod
    def ensure_node(cls, robot_name: str) -> Node:
        return cls._nodes.set_default(robot_name, Node(f"{robot_name}_node"))