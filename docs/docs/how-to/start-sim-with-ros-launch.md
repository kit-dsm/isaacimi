# Starting a simulation with ROS launch files

You can use ROS launch files to start your simulation. Assuming the simulation and your ROS nodes are being run on the same machine, this method ensures that your entire simulation bringup is consolidated in one launch file.

```python
from launch.actions import ExecuteProcess
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    cmd = ExecuteProcess(
        cmd=["isaacimi", "sim", "run", "isaacimi/my_blueprint.yaml"],
        cwd=FindPackageShare("my_robot_bringup"),
        output="screen"
    )
    ld = LaunchDescription()
    ld.add_action(cmd)
```

The `ExecuteProcess` action runs the command specified in the `cmd` argument. It is similar to how you would normally use the `isaacimi` CLI to start a simulation. Note that the blueprint path can be relative or absolute. Relative paths are relative to the directory that the launch file is ran, or relative to the `cwd` argument, if it is specified.