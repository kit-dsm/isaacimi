Isaac IMI was designed to make it easy to run many different simulation scenarios. The goal of this page is to show how to Isaac IMI can be used to quickly get a simulation up and running, and is not intended to be a tutorial or a reference. The [Getting Started](getting-started/installation.md) tutorial covers how to run a simulation in more detail.

## Create a simulation blueprint
Create a yaml file that describes the simulation you want to run.
```yaml title="my_simulation_project/blueprints/evorobot_unitree_warehouse.yaml"
app:
  headless: false
  renderer: RayTracedLighting

world:
  stage_units_in_meters: 1.0
  physics_dt: 0.0166
  rendering_dt: 0.0166

scene:
  environment:
    usd_path: ../environments/warehouse.usd
    prim_path: /World/environment
  robots:
    - name: Evorobot_1
      usd_path: ../robots/evorobot.usd
      prim_path: /World/Evorobot_1
      position: [0, 0, 0]
      orientation: [1, 0, 0, 0]
    - name: Evorobot_2
      usd_path: ../robots/evorobot.usd
      prim_path: /World/Evorobot_2
      position: [-1.5, -1.5, 0]
      orientation: [1, 0, 0, 0]
    - name: Unitree_Go2_1
      usd_path: ../robots/unitree_go2.usd
      prim_path: /World/Unitree_Go2_1
      position: [1.5, 1.5, 0]
      orientation: [1, 0, 0, 0]
```
## Run the simulation
Isaac IMI provides a simple command line interface.
```bash
isaacimi sim run my_simulation_project/blueprints/evorobot_unitree_warehouse.yaml
```

## Add your own custom plugins
To add functionality to the robots you spawn in the simulation, you can create "robot plugins" - reusable pieces of logic run that can be run on any robot spawned in the simulation. Let's create a simple ROS subscriber plugin for the evorobots:

``` py title="my_simulation_project/plugins/simple_subscriber_plugin.py"

from isaacimi.robot_plugin import ImiRobotPlugin

from std_msgs.msg import String

class SimpleSubscriber(ImiRobotPlugin):   
    def on_plugin_load(self):
        self.ros_node.create_subscription(String, f"{self.robot_name}/topic", self.callback, 1)
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

Now, to use the plugin in your simulation, you can add it to your blueprint file:
```yaml title="my_simulation_project/blueprints/evorobot_unitree_warehouse.yaml" hl_lines="20 21 27 28 37 38 39 40"
app:
  headless: false
  renderer: RayTracedLighting

world:
  stage_units_in_meters: 1.0
  physics_dt: 0.0166
  rendering_dt: 0.0166

scene:
  environment:
    usd_path: ../environments/warehouse.usd
    prim_path: /World/environment
  robots:
    - name: Evorobot_1
      usd_path: ../robots/evorobot.usd
      prim_path: /World/Evorobot_1
      position: [0, 0, 0]
      orientation: [1, 0, 0, 0]
      plugins:
        - SimpleSubscriber
    - name: Evorobot_2
      usd_path: ../robots/evorobot.usd
      prim_path: /World/Evorobot_2
      position: [-1.5, -1.5, 0]
      orientation: [1, 0, 0, 0]
      plugins:
        - SimpleSubscriber
    - name: Unitree_Go2_1
      usd_path: ../robots/unitree_go2.usd
      prim_path: /World/Unitree_Go2_1
      position: [1.5, 1.5, 0]
      orientation: [1, 0, 0, 0]

robot_plugins:
  - filepath: ../plugins/simple_subscriber_plugin.py
    classes:
      - SimpleSubscriber
```