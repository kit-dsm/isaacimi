import pytest

from isaacimi.robot_plugin import ImiRobotPlugin
from unittest.mock import Mock, call, ANY

@pytest.fixture
def dummy_robot(simulation_app):
    from isaacimi.imi_robot import ImiRobot
    from pathlib import Path
    dummy_robot = ImiRobot(
        "/World/robot",
        "robot",
        str(Path(__file__).parent / ".." / "data" / "dummy_robot.usd"),
        [0, 0, 0],
        [1, 0, 0, 0]
    )
    return dummy_robot

def test_plugins_load_successfully(dummy_robot):
    from isaacimi.robot_task import ImiRobotTask
    plugin1 = Mock()
    plugin2 = Mock()
    plugin3 = Mock()
    plugins = [
        (plugin1, {}),
        (plugin2, {"arg1": 1, "arg2": 2, "arg3": 3}),
        (plugin3, {"arg1": 1})
    ]
    robot_task = ImiRobotTask(dummy_robot, plugins)
    assert robot_task._robot is dummy_robot
    assert len(robot_task._plugins) == 3
    plugin1.on_plugin_load.assert_called_once_with()
    plugin2.on_plugin_load.assert_called_once_with(arg1=1, arg2=2, arg3=3)
    plugin3.on_plugin_load.assert_called_once_with(arg1=1)

def test_plugin_methods_called_at_correct_times(dummy_robot, world):
    from isaacimi.robot_task import ImiRobotTask
    plugin = Mock()

    robot_task = ImiRobotTask(dummy_robot, [(plugin, {})])
    plugin.on_plugin_load.assert_called_once()
    assert len(plugin.mock_calls) == 1

    world.add_task(robot_task)
    world.reset()

    assert len(plugin.mock_calls) == 4
    plugin.set_up_scene.assert_called_once()
    plugin.cleanup.assert_called_once()
    plugin.initialize.assert_called_once()

    for task_name, task_obj in world.get_current_tasks().items():
        world.add_physics_callback(f"{task_name}_physics_callback", task_obj.on_physics_step)
    world.step()

    assert len(plugin.mock_calls) == 6
    plugin.pre_physics_step.assert_called_once()
    plugin.on_physics_step.assert_called_once()

    world.reset()
    assert len(plugin.mock_calls) == 8
    assert plugin.cleanup.call_count == 2
    assert plugin.initialize.call_count == 2


def test_plugin_methods_called_in_correct_order(dummy_robot, world):
    from isaacimi.robot_task import ImiRobotTask
    plugins = [(Mock(), {}), (Mock(), {}), (Mock(), {})]
    robot_task = ImiRobotTask(dummy_robot, plugins)

    world.add_task(robot_task)
    world.reset()

    for task_name, task_obj in world.get_current_tasks().items():
        world.add_physics_callback(f"{task_name}_physics_callback", task_obj.on_physics_step)

    for i in range(3): # simulate three steps
        world.step(render=True)

    world.reset()
    
    # ensure that the correct methods are called for all plugins:
    # on_plugin_load() is called once at the beginning
    # set_up_scene(), cleanup(), and initialize() are called after a world.reset()
    # set_up_scene() is called only on the first reset
    expected_calls = [
        call.on_plugin_load(),
        call.set_up_scene(dummy_robot, world.scene),
        call.cleanup(world.scene),
        call.initialize(dummy_robot),
        call.pre_physics_step(dummy_robot, ANY, ANY),
        call.on_physics_step(dummy_robot, ANY),
        call.pre_physics_step(dummy_robot, ANY, ANY),
        call.on_physics_step(dummy_robot, ANY),
        call.pre_physics_step(dummy_robot, ANY, ANY),
        call.on_physics_step(dummy_robot, ANY),
        call.cleanup(world.scene),
        call.initialize(dummy_robot)
    ]

    for plugin, _ in plugins:
        assert len(plugin.mock_calls) == len(expected_calls)
        plugin.assert_has_calls(expected_calls, any_order=False)

def test_robot_exists_in_scene_after_first_world_reset(dummy_robot, world):
    from isaacimi.robot_task import ImiRobotTask
    robot_task = ImiRobotTask(dummy_robot, [(Mock(), {})])
    world.add_task(robot_task)
    assert not world.scene.object_exists(dummy_robot.name)
    world.reset()
    assert world.scene.object_exists(dummy_robot.name)