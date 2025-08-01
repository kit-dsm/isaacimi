from typing import Dict, Type
from pathlib import Path


def resolve_path_in_blueprint(path: str, blueprint_path: str, allowed_extensions: set = None) -> str:
    """Resolves a file path provided in the simulation blueprint to an absolute, normalized path.

    If the file path provided in the simulation blueprint is already a valid absolute path, return it.
    Otherwise, it is treated as relative to the simulation blueprint file.

    Args:
        path (str): The file path provided in the simulation blueprint
        blueprint_path (str): The path to the simulation blueprint
        allowed_extensions (set, optional): A set of allowed file extensions. Defaults to None.

    Raises:
        FileNotFoundError: If the provided file path does not exist
        IsADirectoryError: If the provided path is a directory instead of a file 
        ValueError: If the provided file path has an invalid extension

    Returns:
        str: Resolved absolute path to the file
    """
    # TODO: paths to cloud assets
    blueprint_dir = Path(blueprint_path).resolve().parent
    path_obj = Path(path)
    resolved_path = path_obj if path_obj.is_absolute() else (blueprint_dir / path_obj).resolve()
    if not resolved_path.exists():
        raise FileNotFoundError(f"The provided path does not exist: {resolved_path}")
    if not resolved_path.is_file():
        raise IsADirectoryError(f"The provided path is not a file: {resolved_path}")
    if allowed_extensions and resolved_path.suffix.lower() not in allowed_extensions:
        raise ValueError(f"The provided path {resolved_path} has an invalid file extension. Allowed: {allowed_extensions}")
    return str(resolved_path)
    

def run_sim(blueprint_path: str):
    import yaml
    with open(blueprint_path, 'r') as scene_config_file:
        scene_config = yaml.safe_load(scene_config_file)


    import sys
    import carb
    from .blueprint_schema import blueprint_schema, BlueprintValidator
    v = BlueprintValidator(blueprint_schema)
    scene_config = v.normalized(scene_config)
    if not v.validate(scene_config):
        carb.log_error(f"The provided config file is invalid: {v.errors}")
        sys.exit(1)


    # The SimulationApp needs to start before importing any packages from isaac.core, otherwise a ModuleNotFoundError is raised
    from isaacsim import SimulationApp
    app_config = {
        "headless": scene_config["app"]["headless"],
        "renderer": scene_config["app"]["renderer"],
    }
    simulation_app = SimulationApp(app_config)


    from isaacsim.storage.native import get_assets_root_path
    assets_root_path = get_assets_root_path()
    if assets_root_path is None:
        carb.log_error("Could not find Isaac Sim assets folder")
        simulation_app.close()
        sys.exit(1)


    from isaacimi.robot_plugin import ImiRobotPlugin
    from isaacimi.utils import load_subclasses_from_file
    plugin_registry: Dict[str, Type[ImiRobotPlugin]] = dict()
    plugin_file_extensions = {".py"}
    for entry in scene_config.get("robot_plugins", []):
        plugins = load_subclasses_from_file(resolve_path_in_blueprint(entry["filepath"], blueprint_path, allowed_extensions=plugin_file_extensions), ImiRobotPlugin, allowed_names=entry["classes"])
        plugin_registry.update(plugins)
    carb.log_info(f"User defined robot_plugins: {plugin_registry}")


    from isaacsim.core.api import World
    world = World(scene_config["world"]["stage_units_in_meters"])
    world.set_simulation_dt(physics_dt=scene_config["world"]["physics_dt"], rendering_dt=scene_config["world"]["rendering_dt"])


    from isaacsim.core.utils.extensions import enable_extension
    enable_extension("isaacsim.ros2.bridge")
    if scene_config["app"]["livestream"]:
        enable_extension("omni.kit.livestream.webrtc")


    import rclpy
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

    from isaacsim.core.utils.stage import add_reference_to_stage
    add_reference_to_stage(usd_path=resolve_path_in_blueprint(scene_config["scene"]["environment"]["usd_path"], blueprint_path, allowed_extensions=usd_file_extensions), prim_path=scene_config["scene"]["environment"]["prim_path"])


    import numpy as np
    from isaacimi.imi_robot import ImiRobot
    from isaacimi.robot_task import ImiRobotTask
    for robot_config in scene_config["scene"]["robots"]:
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
