from typing import Dict, Type
import os
from pathlib import Path
import yaml

from .blueprint_schema import blueprint_schema, BlueprintValidator
from .utils import resolve_path_in_blueprint
from isaacimi.robot_plugin import ImiRobotPlugin
from isaacimi.utils import load_subclasses_from_file

def run_sim(blueprint_path: str):
    # Load the blueprint file
    blueprint_path_obj = Path(blueprint_path)

    if not blueprint_path_obj.is_file():
        raise FileNotFoundError(f"Blueprint file {blueprint_path_obj} does not exist.")
    
    if blueprint_path_obj.suffix.lower() != ".yaml":
        raise ValueError(f"Blueprint file {blueprint_path_obj} must be a .yaml file.")
    
    with open(blueprint_path, "r") as blueprint_file:
        blueprint = yaml.safe_load(blueprint_file)


    # Normalize and validate the blueprint file
    v = BlueprintValidator(blueprint_schema)
    blueprint = v.normalized(blueprint)
    if not v.validate(blueprint):
        raise ValueError(f"The provided blueprint file is invalid: {v.errors}")
    

    # The SimulationApp needs to start before importing any packages from isaac.core, otherwise a ModuleNotFoundError is raised
    from isaacsim import SimulationApp
    import carb
    in_docker = os.getenv("IN_DOCKER") == "1"
    headless = blueprint["app"]["headless"]
    if in_docker and headless == False:
        carb.log_warn("Docker container detected. Simulation running in headless mode.")
        headless = True
    app_config = {
        "headless": headless,
        "renderer": blueprint["app"]["renderer"],
    }
    simulation_app = SimulationApp(app_config)


    # Add user-defined robot_plugins to the plugin registry
    plugin_registry: Dict[str, Type[ImiRobotPlugin]] = dict()
    plugin_file_extensions = {".py"}
    for entry in blueprint.get("robot_plugins", []):
        plugins = load_subclasses_from_file(resolve_path_in_blueprint(entry["filepath"], blueprint_path, allowed_extensions=plugin_file_extensions), ImiRobotPlugin, allowed_names=entry["classes"])
        plugin_registry.update(plugins)
    carb.log_info(f"User defined robot_plugins: {plugin_registry}")


    from isaacsim.core.api import World
    world = World(blueprint["world"]["stage_units_in_meters"])
    world.set_simulation_dt(physics_dt=blueprint["world"]["physics_dt"], rendering_dt=blueprint["world"]["rendering_dt"])


    # Enable Isaac Sim extensions
    from isaacsim.core.utils.extensions import enable_extension
    enable_extension("isaacsim.ros2.bridge")
    if blueprint["app"]["livestream"]:
        enable_extension("omni.kit.livestream.webrtc")


    # Create an action graph that publishes the simulation time to the /clock topic
    import omni.graph.core as og
    try:
        og.Controller.edit(
            {"graph_path": "/ActionGraph", "evaluator_name": "execution"},
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("ReadSimTime", "isaacsim.core.nodes.IsaacReadSimulationTime"),
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    ("PublishClock", "isaacsim.ros2.bridge.ROS2PublishClock"),
                ],
                og.Controller.Keys.CONNECT: [
                    ("OnPlaybackTick.outputs:tick", "PublishClock.inputs:execIn"), # Connecting execution of OnPlaybackTick node to PublishClock to automatically publish each frame
                    ("ReadSimTime.outputs:simulationTime", "PublishClock.inputs:timeStamp"), # Connecting simulationTime data of ReadSimTime to PublishClock node
                ],
                og.Controller.Keys.SET_VALUES: [
                    ("PublishClock.inputs:topicName", "/clock"), # Assigning topic name to PublishClock node
                ],
            },
        )
    except Exception as e:
        print(e)


    usd_file_extensions = {".usd", ".usda"}
    # Add the environment to the scene
    from isaacsim.core.utils.stage import add_reference_to_stage
    add_reference_to_stage(usd_path=resolve_path_in_blueprint(blueprint["scene"]["environment"]["usd_path"], blueprint_path, allowed_extensions=usd_file_extensions), prim_path=blueprint["scene"]["environment"]["prim_path"])

    # Add the robots to the scene
    import numpy as np
    from isaacimi.imi_robot import ImiRobot
    from isaacimi.robot_task import ImiRobotTask
    for robot_config in blueprint["scene"]["robots"]:
        robot = ImiRobot(
            robot_config["prim_path"],
            robot_config["name"],
            resolve_path_in_blueprint(robot_config["usd_path"], blueprint_path, allowed_extensions=usd_file_extensions),
            np.array(robot_config["position"]),
            np.array(robot_config["orientation"])
        )
        plugins = [(plugin_registry[plugin["class"]](robot.name), plugin.get("params", {})) for plugin in robot_config.get("plugins", [])]

        robot_task = ImiRobotTask(robot, plugins)
        world.add_task(robot_task)


    # physics get initialized when world.reset() is called
    # internally performs one physics step
    world.reset()


    # register the physics_callback for each robot task
    # should be done after the first world.reset() is called to prevent the on_physics_step callback (in plugins) from being called before physics are initialized
    for task_name, task_obj in world.get_current_tasks().items():
        world.add_physics_callback(f"{task_name}_physics_callback", task_obj.on_physics_step)


    from isaacimi.ros_manager import RosManager
    i = 0
    reset_needed = False
    while simulation_app.is_running():
        RosManager.spin_once()
        world.step(render=True)
        if world.is_stopped() and not reset_needed:
            reset_needed = True
        if world.is_playing():
            if reset_needed:
                world.reset()
                reset_needed = False
            i += 1

    simulation_app.close()
