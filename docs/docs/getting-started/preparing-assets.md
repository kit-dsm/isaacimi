# Preparing USD assets

## Prerequisite
* Successfully installed Isaac Sim and Isaac IMI [locally](local-installation.md) or with [Docker](docker-deployment.md).

## Introduction
Suppose we want to simulate three autonomous mobile robots (AMRs) driving through a warehouse. To create this simulation with Isaac IMI, we first need to prepare our assets.

Isaac Sim uses the Universal Scene Description (USD) file format to describe assets in the simulation. Thus, the two assets you need are:

1. A `.usd` file describing each robot you want to add to the simulation (in this tutorial, the AMR)
2. A `.usd` file describing the static environment that your robots will be spawned in (in this tutorial, the warehouse)

!!! note
    Each custom robot in the simulation requires its own USD file. For example, if you want to simulate three AMRs and two Unitree Go2 robots, you'll need two `.usd` files: one that describes the AMR and one that describes the Unitree Go2.

## Prepare a USD for each custom robot you want to use in simulation
There are many ways to obtain a `.usd` file for your robot:

1. Design your robot using the Isaac Sim GUI and export it as a `.usd` file
2. Design your robot in a software of your choice and export it to a `.usd` file. Many [softwares](https://openusd.org/release/usd_products.html#maya) support OpenUSD.
3. If you have a URDF, MJCF XML, or CAD file for your robot, you can use the [Isaac Sim import tools](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/robot_setup/importers_exporters.html)

The [Isaac Sim documentation](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/robot_setup/index.html) provides a create guide for how to set up your assets for simulation, including how to use the import tools and rigging the robot. As this process is already documented, we won't cover it here.

This tutorial will use the NVIDIA Carter robot. The `.usd` file for the robot is located in `isaacimi/examples/robots/carter_v1.usd`.

!!! warning
    This `.usd` file should only contain the robot you want to spawn in the simulation. As a best practice, do not add additional prims or logic such as action graphs to your `.usd` file.

## Prepare a USD for the environment you want to use in simulation 
You can obtain a `.usd` file for the environment the same way you would for your robot.

If using the Isaac Sim GUI, the Isaac Sim documentation provides some helpful guides:

* [Environment Setup](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/gui/tutorial_intro_environment_setup.html) - walks through how to create an environment in Isaac Sim
* [Add Simply Objects](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/gui/tutorial_intro_simple_objects.html) - wakls through how to add objects to the scene

This tutorial will use a simple warehouse environment. The `.usd` file for the warehouse is located in `isaacimi/examples/environments/warehouse_with_shelf.usd`.

!!! warning
    This `.usd` file should contain only the static evironment you want to spawn your robots in. As a best practice, do not add robots or logic such as action graphs to your `.usd` file.

## Summary
After this step, you should now have a `.usd` file describing the AMR you want to simulate and a `.usd` file describing the warehouse that the AMRs will be spawned in.
