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

import carb
import sys
from isaacsim.storage.native import get_assets_root_path
assets_root_path = get_assets_root_path()
if assets_root_path is None:
    carb.log_error("Could not find Isaac Sim assets folder")
    simulation_app.close()
    sys.exit()

from isaacsim.core.utils.stage import add_reference_to_stage
add_reference_to_stage(usd_path=assets_root_path+scene_config["scene"]["environment_usd_path"], prim_path="/World/Environment")

for robot in scene_config["scene"]["robots"]:
    print("spawning robot")

simulation_app.close()
