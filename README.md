# Isaac IMI: Simulations in Isaac Sim made easy 

[![IsaacSim](https://img.shields.io/badge/IsaacSim-4.5.0-silver.svg)](https://docs.isaacsim.omniverse.nvidia.com/latest/index.html)
[![Python](https://img.shields.io/badge/python-3.10-blue.svg)](https://docs.python.org/3/whatsnew/3.10.html)

Isaac IMI, originally developed for the Institute for Information Management in Engineering (IMI) at the Karlsruhe Institute of Technology (KIT), is a framework for running custom robotic simulations in Isaac Sim. Each simulation scenario is configured with a single "blueprint" YAML file, and customized with modular user-developed plugins. Isaac IMI is easy to use with a simple command line interface.

## Documentation
The [documentation](https://kit-dsm.github.io/isaacimi/) page provides everything you need to use isaacimi, including tutorials, examples, and developer guides.

## Example workflow
### 1. Prepare the `.usd` files
Since Isaac Sim uses Universal Scene Description (USD) for all assets, you need to create a `.usd` file to describe each robot you want to simulate, and the environment you want to simulate them in. 

### 2. Create a simulation blueprint
Once you have the `.usd` assets, create a yaml file that describes the simulation you want to run.
```yaml
# my_custom_sim.yaml
app:
  headless: false
  renderer: RayTracedLighting

world:
  stage_units_in_meters: 1.0
  physics_dt: 0.0166
  rendering_dt: 0.0166

scene:
  environment:
    usd_path: path/to/environment.usd
    prim_path: /World/environment
  robots:
    - name: robot1
      usd_path: path/to/robot.usd
      prim_path: /World/robot1
      position: [0, 0, 0]
      orientation: [1, 0, 0, 0]
```

### 4. Run your simulation
```bash
isaacimi sim run path/to/my_custom_sim.yaml
```

### 5. Customize your simulation with plugins
In separate Python files, create a custom plugins by extending the `ImiRobotPlugin` class:
```python
# my_custom_plugins.py

from isaacimi.robot_plugin import ImiRobotPlugin
from std_msgs.msg import String

class SimpleSubscriber(ImiRobotPlugin):   
    def on_plugin_load(self):
        self.ros_node.create_subscription(String, "topic", self.callback, 1)
        self.topic_data = None
        return

    def callback(self, msg: String) -> None:
        print("I heard: {msg.data}")
        self.topic_data = msg
        return

    def on_physics_step(self, robot, step_size) -> None:
        print(f"My most recent data is {self.topic_data}")
        return
```
Add your plugins to the simulation blueprint and use it across many robots:
```yaml
# my_custom_sim.yaml
...

scene:
  environment:
    usd_path: path/to/environment.usd
    prim_path: /World/environment
  robots:
    - name: robot1
      usd_path: path/to/robot.usd
      prim_path: /World/robot1
      position: [0, 0, 0]
      orientation: [1, 0, 0, 0]
      plugins:
        class: SimpleSubscriber # add custom plugin

robot_plugins: # define custom plugin
  - filepath: path/to/my_custom_plugins.py
    classes:
      - SimpleSubscriber
```

## Citing the project
```bibtex
@misc{isaacimi2025,
author = {Chung, David and Disselnmeyer, Max and Meyer, Anne},
title = {IsaacIMI},
year = {2025},
publisher = {GitHub},
journal = {GitHub Repository},
howpublished = {\url{https://github.com/kit-dsm/isaacimi}},
}
```