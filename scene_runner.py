import argparse
parser = argparse.ArgumentParser()
parser.add_argument(
    '--config',
    type=str,
    required=True,
    help='Path to the scene configuration file' # for now, path is relative to where the script is called
)
args = parser.parse_args()

import yaml
with open(args.config, 'r') as scene_config_file:
    scene_config = yaml.safe_load(scene_config_file)

from isaacsim import SimulationApp
app_config = {
    "headless": scene_config["app"]["headless"],
    "renderer": scene_config["app"]["renderer"],
}
simulation_app = SimulationApp(app_config)

from isaacsim.core.api import World
world = World(scene_config["world"]["stage_units_in_meters"])
world.set_simulation_dt(physics_dt=scene_config["world"]["physics_dt"], rendering_dt=scene_config["world"]["rendering_dt"])

from isaacsim.core.utils.extensions import enable_extension
enable_extension("isaacsim.ros2.bridge")

import rclpy
import omni.graph.core as og
rclpy.init()
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

import carb
import sys
from isaacsim.storage.native import get_assets_root_path
assets_root_path = get_assets_root_path()
if assets_root_path is None:
    carb.log_error("Could not find Isaac Sim assets folder")
    simulation_app.close()
    sys.exit()

from isaacsim.core.utils.stage import add_reference_to_stage
add_reference_to_stage(usd_path=assets_root_path+scene_config["scene"]["environment"]["usd_path"], prim_path=scene_config["scene"]["environment"]["prim_path"])

import numpy as np
# from custom_utils import RosRobot
from isaacimi import ImiRobot
# robots = []
for robot_config in scene_config["scene"]["robots"]:
    # robots.append(world.scene.add(RosRobot(
    #     robot_config["prim_path"],
    #     robot_config["name"],
    #     robot_config["usd_path"],
    #     np.array(robot_config["position"]),
    #     np.array(robot_config["orientation"])
    #     # to-do: articulation controller
    # )))

    world.add_task(ImiRobot(
        robot_config["prim_path"],
        robot_config["name"],
        robot_config["usd_path"],
        np.array(robot_config["position"]),
        np.array(robot_config["orientation"])
    ))

world.reset()

while simulation_app.is_running():
    # for robot in robots:
    #     robot.post_step()
    world.step(render=True)

simulation_app.close()
