# Running a simulation

## Prerequisite
* Prepared the [two required asset types](preparing-assets.md) to run a simulation with Isaac IMI

## Create a YAML config for the simulation
Each simulation run is defined by a single YAML config file. This file provides all the information that Isaac IMI needs to run a simulation. More information on this file is provided in the [yaml config reference](../reference/yaml-config.md).

Create a `simple_simulation.yaml` file, and add the following contents to it:

```yaml title="simple_simulation.yaml"
app:
  headless: false
  renderer: RayTracedLighting

world:
  stage_units_in_meters: 1.0
  physics_dt: 0.0166
  rendering_dt: 0.0166

scene:
  environment:
    usd_path: /path/to/cone_cylinder_cube.usd.usd # replace this path with your environment .usd file
    prim_path: /World/environment
  robots:
    - name: dummy1
      usd_path: /path/to/dummy_robot.usd # replace this path with your robot .usd file
      prim_path: /World/dummy1
      position: [0, 0, 0]
      orientation: [1, 0, 0, 0]
    - name: dummy2
      usd_path: /path/to/dummy_robot.usd # replace this path with your robot .usd file
      prim_path: /World/dummy2
      position: [1.5, 1.5, 0]
      orientation: [1, 0, 0, 0]
```
This yaml file sets some generic settings for the simulation, and spawns two dummy robots defined in our `dummy_robot.usd` file in an environment defined by our `cone_cylinder_cube.usd` file. A copy of the yaml config file used in this tutorial is found in `examples/scenes/cone_cylinder_cube.usd`.

## Run the simulation