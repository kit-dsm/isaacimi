# Adding robot plugins

## Prerequisite
* Completed the [running a simulation](running-a-simulation.md) section and successfully spawned three AMRs into a warehouse.

## Using robot plugins
The three robots are spawned in the simulation, but they currently aren't doing anything. We can give them extra functionality through "robot plugins". A robot plugin is simply a reusable piece of logic that can be used across different robots in simulations. Plugins are really useful when you are working with ROS2, as we provide a very simple way to have publishers, subscribers, actions, etc. running on your simulated robot.

!!! note
    You could technically add functionality to your robot wihout using a robot plugin by creating an [action graph](https://docs.isaacsim.omniverse.nvidia.com/latest/omnigraph/omnigraph_tutorial.html). However, plugins are recommended because it offers greater visibility and control over what happens on the robot. For more details on why plugins are preferred, see the [architecture](../architecture.md) page.

In the real world, your robot might run a ROS node to perform path planning, and a ROS node to compute the `Twist` (linear and angular velocity) message required for your robot to follow that path. Then, a controller might translate this `Twist` message into some lower level control input for the motors (can be velocity, torque, PWM, depending on the motor). However, in a simulated world, we are no longer working with motors but rather joints. Thus, whatever controller was used to control the motors of the robot in real life needs to be replaced with with a controller that controls the joints of the robot in simulation.

### Creating a controller plugin
Since the Clearpath Dingo is a differential drive robot, let's create a differential controller robot plugin to use across all three robots in the warehouse. Each plugin instance will listen to `Twist` messages published to the `cmd_vel` topic for that robot, and apply the necessary joint commands to move the robot. The example plugin created in this section can be found in `isaacimi/examples/plugins/differential_controller_plugin.py`.

Create a new `differential_controller_plugin.py` file, and create a robot plugin class called `DifferentialControllerPlugin` that extends the `ImiRobotPlugin` class. The base class provides several hooks for you to override, such as `on_plugin_load`, which is called when the plugin is attached to the robot. More information on the different hooks that are provided can be found in the [API Reference page](../reference/api/isaacimi/robot_plugin.md).
```python title="differential_controller_plugin.py"
from isaacimi.robot_plugin import ImiRobotPlugin

class DifferentialControllerPlugin(ImiRobotPlugin):
    def on_plugin_load(self):
        pass
```

To add the plugin to our robot, we need to modify the simulation blueprint:
```yaml title="dingo_3x_warehouse_two_shelves.yaml" hl_lines="20 21 27 28 34 35 37-40"
app:
  headless: false
  renderer: RayTracedLighting

world:
  stage_units_in_meters: 1.0
  physics_dt: 0.0166
  rendering_dt: 0.0166

scene:
  environment:
    usd_path: path/to/warehouse_two_shelves.usd # replace this path with the path to your environment .usd file
    prim_path: /World/environment
  robots:
    - name: dingo1
      usd_path: path/to/clearpath_dingo.usd # replace this path with the path to your robot .usd file
      prim_path: /World/dingo1
      position: [2, 0, 0]
      orientation: [1, 0, 0, 0]
      plugins:
        - class: DifferentialControllerPlugin
    - name: dingo2
      usd_path: path/to/clearpath_dingo.usd # replace this path with the path to your robot .usd file
      prim_path: /World/dingo2
      position: [2, 3, 0]
      orientation: [1, 0, 0, 0]
      plugins:
        - class: DifferentialControllerPlugin
    - name: dingo3
      usd_path: path/to/clearpath_dingo.usd # replace this path with the path to your robot .usd file
      prim_path: /World/dingo3
      position: [-2, -3, 0]
      orientation: [1, 0, 0, 0]
      plugins:
        - class: DifferentialControllerPlugin

robot_plugins:
  - filepath: path/to/differential_controller_plugin.py # replace this path with the path to the .py file containing your controller plugin
    classes:
      - DifferentialControllerPlugin
```

### Adding a ROS subscriber
When the plugin is loaded, we want to create a subscriber to the `cmd_vel` topic. The callback function will be `twist_cmd_callback`. By default, every robot in the simulation does not have a ROS node. Accessing `self.ros_node` will internally create a ROS node for that robot, and each robot can have at most one ROS node.

Remember that physics steps may occur many times in a second, and your ROS callback will not execute every physics step. Thus, we need to save the published twist commands to `self.lin_vel_cmd` and `self.ang_vel_cmd` variables so we can use them in the `pre_physics_step` method.

```python title="differential_controller_plugin.py"
from isaacimi.robot_plugin import ImiRobotPlugin

from geometry_msgs.msg import Twist

class DummyRobotPlugin(ImiRobotPlugin):
    def on_plugin_load(self):
        # create ROS subscriber
        self.ros_node.create_subscription(Twist, "cmd_vel", self.twist_cmd_callback, 1)
        
        # variables to store the Twist command
        self.lin_vel_cmd = np.zeros(3)
        self.ang_vel_cmd = np.zeros(3)
        return

    def twist_cmd_callback(self, data: Twist) -> None:
        # save twist command to variables
        self.lin_vel_cmd[0] = data.linear.x
        self.lin_vel_cmd[1] = data.linear.y
        self.lin_vel_cmd[2] = data.linear.z
        self.ang_vel_cmd[0] = data.angular.x
        self.ang_vel_cmd[1] = data.angular.y
        self.ang_vel_cmd[2] = data.angular.z
        return

    def pre_physics_step(self, robot, time_step_index, simulation_time):
        pass
```

### Implementing the controller
We can use the `DifferentialController` class provided by Isaac Sim to compute the joint commands required to make our robot follow the twist command. You can most definitely do your own calculations, but we are using this built-in class for simplicity. The `DifferentialController`, requires the `wheel_radius` and `wheel_base` of the robot in meters to calculate the joint velocities, which are `0.0492` and `0.45232` respectively.

All joint commands (velocity, position, or effort) need to be packaged in an `ArticulationAction` object. So, we create a member variable to store the most current `ArticulationAction`. More information on this class can be found on the [Isaac Sim docs](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/robot_simulation/articulation_controller.html#articulation-action).

In the `pre_physics_step` method, we can compute the joint velocities using the `DifferentialController.forward()` method, which accepts a two element `np.ndarray` consisting of the desired linear and angular speed for our robot (i.e. the `Twist`), and outputs an `ArticulationAction` object containing joint velocities for the left and right wheel joints. As described in the Isaac Sim documentation for `ArticulationAction`, there are a few ways to populate the object. In this scenario, we will populate the object with commands for all joints on the robot. Therefore, our `ArticulationAction` object should match the number of joints on our robot.

To get the number of joints on our Dingo robot, we can use the `num_dof` property on the `robot` instance, which returns the number of joints it has. We need to do this in the `initialize` method of our plugin, because that is when the robot's physics are initialized and joint information becomes available.

Additionally, when we populate the `ArticulationAction` object with our wheel velocity commands, we need to place the commands at the correct index, as each index corresponds to a specific joint. We know that name of the left and right wheel joints on the Dingo are `left_wheel_joint` and `right_wheel_joint` respectively, so we can get the index of each joint using the `robot.get_dof_index()` method.

Finally, now that we have the total number of joints on our robot, and know which index in the `ArticulationAction` object corresponds to the left and right wheel joints, we can construct our `ArticulationAction` object and apply it to the robot using the `robot.apply_action()` method.

```python title="differential_controller_plugin.py" hl_lines="17-26 29-42 54-66"
from isaacimi.robot_plugin import ImiRobotPlugin

from geometry_msgs.msg import Twist

from isaacsim.robot.wheeled_robots.controllers.differential_controller import DifferentialController
from isaacsim.core.utils.types import ArticulationAction

class DummyRobotPlugin(ImiRobotPlugin):
    def on_plugin_load(self):
        # create ROS subscriber
        self.ros_node.create_subscription(Twist, "cmd_vel", self.twist_cmd_callback, 1)
        
        # variables to store the Twist command
        self.lin_vel_cmd = np.zeros(3)
        self.ang_vel_cmd = np.zeros(3)

        # use differential controller class provided by Isaac Sim
        self.diff_controller = DifferentialController(name="differential_controller", wheel_radius=0.0492, wheel_base=0.45232)

        # variable to store the current ArticulationAction
        self.curr_robot_action = None

        # to be inititialized in self.initialize() after physics has been initialized
        self.left_wheel_joint_index = None
        self.right_wheel_joint_index = None
        self.num_joints = None
        return

    def initialize(self, robot):
        # get the joint index corresponding to the left and right wheel joints
        self.left_wheel_joint_index = robot.get_dof_index("left_wheel_joint")
        self.right_wheel_joint_index = robot.get_dof_index("right_wheel_joint")

        # get the number of joints on our robot
        self.num_joints = robot.num_dof

        # initialize the ArticulationAction object, ensuring it has the same length as the number of joints on our robot
        self.curr_robot_action = ArticulationAction()
        self.curr_robot_action.joint_positions = np.zeros(self.num_joints)
        self.curr_robot_action.joint_velocities = np.zeros(self.num_joints)
        self.curr_robot_action.joint_efforts = np.zeros(self.num_joints)
        return

    def twist_cmd_callback(self, data: Twist) -> None:
        # save twist command to variables
        self.lin_vel_cmd[0] = data.linear.x
        self.lin_vel_cmd[1] = data.linear.y
        self.lin_vel_cmd[2] = data.linear.z
        self.ang_vel_cmd[0] = data.angular.x
        self.ang_vel_cmd[1] = data.angular.y
        self.ang_vel_cmd[2] = data.angular.z
        return

    def pre_physics_step(self, robot, time_step_index, simulation_time):
        # use the DifferentialController class to calculate the joint velocity based on the Twist message
        # input: [signed linear speed, signed angular speed], output: [Left Drive, Right Drive] 
        controller_action = self.diff_controller.forward(command=[self.lin_vel_cmd[0], self.ang_vel_cmd[2]])

        if controller_action is not None:
            # populate the correct indices with the joint commands
            self.curr_robot_action.joint_velocities[self.left_wheel_joint_index] = controller_action.joint_velocities[0]
            self.curr_robot_action.joint_velocities[self.right_wheel_joint_index] = controller_action.joint_velocities[1]

            # apply the joint commands to the robot
            robot.apply_action(control_actions=self.curr_robot_action)
        return
```


### Adding parameters
You may have noticed that we hardcoded some values that were specific to the Dingo robot, such as the ROS topic name, the wheel radius, wheel base, the left wheel joint name, and the right wheel joint name. To make this plugin as modular as possible, we can set these values with parameters.

We can add as many parameters as we want to the `on_plugin_load` method:
```python title="differential_controller_plugin.py" hl_lines="2 4 11 14 15 28 29"
class DummyRobotPlugin(ImiRobotPlugin):
    def on_plugin_load(self, topic_name, wheel_radius, wheel_base, left_wheel_joint_name, right_wheel_joint_name):
        # create ROS subscriber
        self.ros_node.create_subscription(Twist, f"{topic_name}", self.twist_cmd_callback, 1)
        
        # variables to store the Twist command
        self.lin_vel_cmd = np.zeros(3)
        self.ang_vel_cmd = np.zeros(3)

        # use differential controller class provided by Isaac Sim
        self.diff_controller = DifferentialController(name="differential_controller", wheel_radius=wheel_radius, wheel_base=wheel_base)

        # save the names of the left and right wheel joint to be used in the initialize method
        self.left_wheel_joint_name = left_wheel_joint_name
        self.right_wheel_joint_name = right_wheel_joint_name

        # variable to store the current ArticulationAction
        self.curr_robot_action = None

        # to be inititialized in self.initialize() after physics has been initialized
        self.left_wheel_joint_index = None
        self.right_wheel_joint_index = None
        self.num_joints = None
        return

    def initialize(self, robot):
        # get the joint index corresponding to the left and right wheel joints
        self.left_wheel_joint_index = robot.get_dof_index(self.left_wheel_joint_name)
        self.right_wheel_joint_index = robot.get_dof_index(self.right_wheel_joint_name)

        # get the number of joints on our robot
        self.num_joints = robot.num_dof

        # initialize the ArticulationAction object, ensuring it has the same length as the number of joints on our robot
        self.curr_robot_action = ArticulationAction()
        self.curr_robot_action.joint_positions = np.zeros(self.num_joints)
        self.curr_robot_action.joint_velocities = np.zeros(self.num_joints)
        self.curr_robot_action.joint_efforts = np.zeros(self.num_joints)
        return
```

Then, we can set the values of these paramters in the simulation blueprint:
```yaml title="dingo_3x_warehouse_two_shelves.yaml" hl_lines="21-28 35-42 49-56"
app:
  headless: false
  renderer: RayTracedLighting

world:
  stage_units_in_meters: 1.0
  physics_dt: 0.0166
  rendering_dt: 0.0166

scene:
  environment:
    usd_path: path/to/warehouse_two_shelves.usd # replace this path with the path to your environment .usd file
    prim_path: /World/environment
  robots:
    - name: dingo1
      usd_path: path/to/clearpath_dingo.usd # replace this path with the path to your robot .usd file
      prim_path: /World/dingo1
      position: [2, 0, 0]
      orientation: [1, 0, 0, 0]
      plugins:
        - class: DifferentialControllerPlugin
          params:
            topic_name: cmd_vel
            wheel_radius: 0.0492
            wheel_base: 0.45232
            left_wheel_joint_name: left_wheel_joint
            right_wheel_joint_name: right_wheel_joint
    - name: dingo2
      usd_path: path/to/clearpath_dingo.usd # replace this path with the path to your robot .usd file
      prim_path: /World/dingo2
      position: [2, 3, 0]
      orientation: [1, 0, 0, 0]
      plugins:
        - class: DifferentialControllerPlugin
          params:
            topic_name: cmd_vel
            wheel_radius: 0.0492
            wheel_base: 0.45232
            left_wheel_joint_name: left_wheel_joint
            right_wheel_joint_name: right_wheel_joint
    - name: dingo3
      usd_path: path/to/clearpath_dingo.usd # replace this path with the path to your robot .usd file
      prim_path: /World/dingo3
      position: [-2, -3, 0]
      orientation: [1, 0, 0, 0]
      plugins:
        - class: DifferentialControllerPlugin
          params:
            topic_name: cmd_vel
            wheel_radius: 0.0492
            wheel_base: 0.45232
            left_wheel_joint_name: left_wheel_joint
            right_wheel_joint_name: right_wheel_joint

robot_plugins:
  - filepath: path/to/differential_controller_plugin.py # replace this path with the path to the .py file containing your controller plugin
    classes:
      - DifferentialControllerPlugin
```

Great! Now this `DifferentialControllerPlugin` that we created can be used across any differential two-wheel robot in our simulation, we just need to tweak the params a bit in the simulation blueprint.

## Summary
You have successfully created a robot plugin that can be used on each Dingo robot in the simulation! You can now run your simulation and control each Dingo robot by publishing to ROS topics.