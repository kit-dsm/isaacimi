# Welcome to Isaac IMI

Isaac IMI is a framework that enables researchers at the IMI to run custom, multi-robot simulations in Isaac Sim.

## Motivation

Isaac Sim, although a powerful tool, is confusing to use due to the sheer amount of features it has. For example, Isaac Sim supports three development [workflows](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/introduction/workflows.html): GUI, extension, and standalone. As a result, there are many ways to accomplish the same task. To spawn a single robot into the scene and have it listen to a ROS topic, you can add the robot through the GUI and create an [omnigraph](https://docs.omniverse.nvidia.com/extensions/latest/ext_omnigraph/interface.html), do it programmatically using the extension or standalone workflow, or any combination of the three. If you do anything programatically, you may find that many approaches achieve the same result. e.g. What is the difference between a "Simulation Context" and a "World"? What is a "Task"?

Even if all that seems simple, what if you now want to see how five robots interact with eachother instead of just one? You may also want to see how they interact in different environements, such as a factory or a hospital. It is a lot of manual work to create these different scenarios, and with the many ways you can accomplish the same task, the work can get inconsistent and error-prone very fast.

Finally, these problems are amplified when the project involves multiple researchers. It can be difficult for multiple people to work on the same simulation project, or for one person to continue the work of another, as the inconsistencies may lead to confusion or duplication of effort.

With the ongoing research at the IMI into multi-robot systems in logistics, a framework for many researchers to quickly create and run simulations was needed. Isaac IMI was built to accomplish two goals:

#### 1. Development consistency
Define a structured workflow for creating and running simulations in Isaac Sim. In doing so, simulations projects become more maintainable, reproducible, and multiple researchers can work together now, and future researchers can extend their work easily.

#### 2. Development speed
Enable researchers to spend less time configuring their simulation, and more time focusing on developing autonomy algorithms, fleet managers, or anything they want to test in simulation.
