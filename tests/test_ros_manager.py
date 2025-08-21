from isaacimi.ros_manager import RosManager
import pytest
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

@pytest.fixture(autouse=True)
def reset_ros_manager():
    # Reset the RosManager at every test to present states from persisting between tests
    RosManager.shutdown()

def test_ros_manager_not_instantiable():
    with pytest.raises(TypeError):
        ros_manager = RosManager()

def test_ensure_node_returns_node():
    node = RosManager.ensure_node("robot")
    assert isinstance(node, Node)
    assert node.get_namespace() == "/robot"

def test_ensure_node_initializes_rclpy():
    assert RosManager._init is False
    assert RosManager._context is None
    assert RosManager._executor is None
    robot1_node = RosManager.ensure_node("robot1")
    assert isinstance(RosManager._executor, MultiThreadedExecutor)
    assert RosManager._context.ok()
    assert RosManager._init is True

def test_ensure_node_creates_no_duplicates():
    robot1_node = RosManager.ensure_node("robot1")
    robot2_node = RosManager.ensure_node("robot2")
    robot1_node_dup = RosManager.ensure_node("robot1")
    assert len(RosManager._nodes) == 2
    assert robot1_node is robot1_node_dup
    assert robot1_node is not robot2_node

def test_ros_manager_shutdown():
    robot1_node = RosManager.ensure_node("robot1")
    robot2_node = RosManager.ensure_node("robot2")
    robot1_node_dup = RosManager.ensure_node("robot1")
    assert len(RosManager._nodes) == 2
    RosManager.shutdown()
    assert len(RosManager._nodes) == 0
    assert RosManager._context is None
    assert RosManager._executor is None
    assert RosManager._init is False

def test_ros_manager_uses_different_context():
    rclpy.init()
    robot1_node = RosManager.ensure_node("robot1")
    robot2_node = rclpy.create_node("robot2")
    assert robot1_node.context is RosManager._context
    assert robot2_node.context is rclpy.get_default_context()
    assert robot1_node.context is not robot2_node.context