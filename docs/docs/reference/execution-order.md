# Execution order

When a simulation is started with `isaacimi sim run path/to/blueprint.yaml`, it goes through the following phases: **Initialization** &rarr; **Simulation Loop** &rarr; **Finalization**

### Initialization
1. Insert a reference to the environment `.usd` file provided in the blueprint into the USD stage at the specified `prim_path`. An `Xform` prim points to the environment asset.
2. For every robot listed in the blueprint:
    - Insert a reference to the robot `.usd` file into the USD stage at the specified `prim_path`. An `Xform` prim points to the robot asset.
    - Wrap the robot prim into a high-level `ImiRobot` object, which is an articulation-aware object that exposes APIs for physics, joint manipulation and more,
    - Instantiate each plugin listed in the blueprint and load it onto the robot, `on_plugin_load()` hook is called for each plugin
    - At this point, the robot object has not been added to the `Scene` yet
3. For every `ImiRobot` robot object: 
    - Add the object to the `Scene` registry, enabling the object to be managed by the simulation. Now, the object will become responsive to simulation events when the simulation begins. 
    - `set_up_scene()` is called for each plugin on the robot
    - At this point, the robot's physics and joint handles have not been initialized yet, i.e. robot APIs like `num_dof` or `get_joint_positions()` return `None`
5. Initialize physics handles and articulation controllers for **all** objects in the `Scene` registry, including the `ImiRobot` objects. At this point, robot physics and joint handles are initialized, e.g. joint indicies are mapped and robot APIs like `get_joint_positions()` no longer return `None`
6. The `initialize()` method is called for each plugin on the robot. Here, plugins have access to the robot object with all physics initialized.

### Simulaton loop
1. All ROS nodes across all robots are checked for available callbacks. If a callback is available, execute it in the background by a worker thread. Note, only one callback is started each loop (if there is one available), but each simulation loop is very fast and callbacks can run concurrently.    
2.  If it is time for a physics step (configured by the `physics_dt` field in the blueprint):
    - Call `pre_physics_step()` for all plugins
    - Complete the physics step (done internally by Isaac Sim)
    - Call `on_physics_step()` for all plugins
3. If it is time for a render step (configured by the `render_dt` field in the blueprint)
    - Render the scene (done internally by Isaac Sim)

### Finalization
- to-do