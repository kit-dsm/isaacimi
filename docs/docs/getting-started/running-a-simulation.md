# Running a simulation

## Prerequisite
* Prepared the [two required asset types](preparing-assets.md) to run a simulation with Isaac IMI

## Create a blueprint for the simulation
Each simulation is configured by a single YAML file. This file provides all the information that Isaac IMI needs to run a simulation with Isaac Sim. More information on this file is provided in the [simulation blueprint reference](../reference/simulation-blueprint.md).

!!! note
    The location of your YAML file does not matter, you can create it anywhere on your system without a specific folder structure.

Create a `simple_simulation.yaml` file, and add the following contents to it:

```yaml title="simple_simulation.yaml"
app:
  headless: false
  renderer: RayTracedLighting

world:
  stage_units_in_meters: 1.0
  physics_dt: 0.0166
  rendering_dt: 0.0166
```
The `app` settings configures the Isaac Sim application that will be run. Here, we are launching the GUI with our simulation, and using `RayTracedLighting` as the renderer. The `world` settings configures the world that takes place inside the simulation. Here, we we set one unit length in the world equal to one meter, and set the physics and render step size to 0.0166 seconds.

Now, to spawn the AMRs in the environment, we can add the following `scene` settings to the YAML file:

```yaml title="simple_simulation.yaml" hl_lines="10-29"
app:
  headless: false
  renderer: RayTracedLighting

world:
  stage_units_in_meters: 1.0
  physics_dt: 0.0166
  rendering_dt: 0.0166

scene:
  environment:
    usd_path: /path/to/warehouse_with_shelf.usd # replace this path with your environment .usd file
    prim_path: /World/environment
  robots:
    - name: carter1
      usd_path: /home/user/isaacimi/examples/robots/carter_v1.usd # replace this path with your robot .usd file
      prim_path: /World/carter1
      position: [0, 0, 0]
      orientation: [1, 0, 0, 0]
    - name: carter2
      usd_path: /home/user/isaacimi/examples/robots/carter_v1.usd # replace this path with your robot .usd file
      prim_path: /World/carter2
      position: [2, 2, 0]
      orientation: [1, 0, 0, 0]
    - name: carter3
      usd_path: /home/user/isaacimi/examples/robots/carter_v1.usd # replace this path with your robot .usd file
      prim_path: /World/carter3
      position: [-2, -2, 0]
      orientation: [1, 0, 0, 0]
```

!!! note
    The `usd_path` setting should contain the absolute path to the assets that you prepared in the [preparing assets](preparing-assets.md) section.

These settings will spawn three robots described our `carter_v1.usd` file in an environment described by our `warehouse_with_shelf.usd` file. A copy of the YAML file used in this tutorial is found in `isaacimi/examples/blueprints/warehouse_with_shelf.usd`.

## Run the simulation
Now that you have a YAML file that describes the simulation, a `.usd` file describing the AMR, and a `.usd` file describing the warehouse that the AMRs will be spawned in, you are now ready to run the simulation. Use the following command and replace `path/to/simple_simulation.yaml` with the path to your simulation blueprint:
```bash
isaacimi sim run path/to/simple_simulation.yaml
```

Your simulation should now be up and running, with three AMRs spawned in the warehouse environment you created!