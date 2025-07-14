# Preparing USD assets

## Prerequisite
* Completed [Isaac Sim and Isaac IMI installation](installation.md)

## Prepare the two required asset types
Isaac Sim uses the Universal Scene Description (USD) file format to describe assets in the simulation. To run a simulation using Isaac IMI, there are two assets you need:

1. A `.usd` file for each custom robot you want to use in simulation
2. A `.usd` for the environment you want to use in simulation

Suppose we want to simulate two autonomous mobile robots (AMRs) of the same model in an open space with obstacles. Let's create the assets needed for that.

#### Prepare a USD file for each custom robot you want to use in simulation
Each custom robot in the simulation requires its own USD file. For example, if you want to simulate three Evorobots and two Unitree Go2 robots, you'll need two `.usd` files: one that describes the Evorobot and one htat describes the Unitree Go2.

To create a USD for a custom robot, you can:

* Design the robot using the Isaac Sim GUI using [this tutorial](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/gui/tutorial_build_robot_in_gui.html)
* If your robot is in a file format such as URDF, MJCF, or CAD, you can use these [import tools](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/robot_setup/index.html) to convert it to a USD file

This USD file should contain only the robot you want to spawn in the simulation. The `.usd` file for the robot used in this tutorial is located in `examples/robots/dummy_robot.usd`. It contains a simpple AMR with a platform that can lift up and down.

#### 2. Prepare a USD for the environment you want to use in simulation 
Similarly, you need a `.usd` file to represent the static environment that your robots will be spawned in. Here you can define different obstacles such as shelves and walls. Below are some helpful links from the Isaac Sim documentation to get started:

* [Environment Setup](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/gui/tutorial_intro_environment_setup.html) - walks through how to create an environment in Isaac Sim
* [Add Simply Objects](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/gui/tutorial_intro_simple_objects.html) - wakls through how to add objects to the scene

This USD file should contain only the static evironment you want to span you robots in. The `.usd` file for the robot used in this tutorial is located in `examples/environments/cone_cylinder_cube.usd`. It contains an empty environment with a cone, and sylinder, and a cube as obstacles.

## Summary
After this step, you should now have a `.usd` file describing each robot and a `.usd` file describing the static environment that each robot will be spawned in.
