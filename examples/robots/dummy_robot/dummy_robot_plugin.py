from isaacimi.robot_plugin import ImiRobotPlugin

from geometry_msgs.msg import Twist
from std_msgs.msg import Int8

import numpy as np

class DummyRobotControllerPlugin(ImiRobotPlugin):   
    def on_plugin_load(self):
        self.ros_node.create_subscription(Twist, "cmd_vel", self.velocity_callback, 1)
        self.lin_vel = np.zeros(3)
        self.ang_vel = np.zeros(3)

        self.ros_node.create_subscription(Int8, "cmd_lift", self.lift_callback, 1)
        self.lift_direction = 0 # either -1, 0, or +1

        self.max_lift_moving_speed = 0.25
        self.lift_active = False
        return

    def velocity_callback(self, data: Twist) -> None:
        self.lin_vel[0] = data.linear.x
        self.lin_vel[1] = data.linear.y
        self.lin_vel[2] = data.linear.z
        self.ang_vel[0] = data.angular.x
        self.ang_vel[1] = data.angular.y
        self.ang_vel[2] = data.angular.z
        return

    def lift_callback(self, data: Int8) -> None:
        self.lift_direction = data.data
    
    def on_physics_step(self, robot, step_size) -> None:
        if self.lift_direction == 0:
            self.lift_active = False
            robot.set_linear_velocity(self.lin_vel)
            robot.set_angular_velocity(self.ang_vel)
        else:
            self.lift_active = True
            if self.lift_direction > 0:
                robot.set_joint_velocities(np.array([+self.max_lift_moving_speed]))
            else:
                robot.set_joint_velocities(np.array([-self.max_lift_moving_speed]))
        return
    

import omni
from pxr import Gf
import omni.replicator.core as rep
class DummyRobotLidarPlugin(ImiRobotPlugin):
    def on_plugin_load(self):
        # Create the lidar sensor that generates data into "RtxSensorCpu"
        # Sensor needs to be rotated 90 degrees about X so that its Z up

        # Possible options are Example_Rotary and Example_Solid_State
        # drive sim applies 0.5,-0.5,-0.5,w(-0.5), we have to apply the reverse
        _, sensor = omni.kit.commands.execute(
            "IsaacSensorCreateRtxLidar",
            path="/microscan",
            parent="/World/dummy1/base_footprint/base_link/fr_lidar",
            config="SICK_microscan3_ABAZ90ZA1P01", # you need to modify the app.sensors.nv.lidar.profileBaseFolder setting
                                                   # in the isaacsim/exts/isaacsim.sensors.rtx/config/extension.toml file to 
                                                   # add your own lidar config, as explained here: https://forums.developer.nvidia.com/t/add-search-path-for-lidar-configs/255352/2
            translation=(0.05, 0, 0),
            orientation=Gf.Quatd(1, 0, 0, 0),  # Gf.Quatd is w,i,j,k
        )

        # RTX sensors are cameras and must be assigned to their own render product
        hydra_texture = rep.create.render_product(sensor.GetPath(), [1, 1], name="Isaac")

        # # Create Point cloud publisher pipeline in the post process graph
        writer = rep.writers.get("RtxLidar" + "ROS2PublishPointCloud")
        writer.initialize(topicName="point_cloud", frameId="base_scan")
        writer.attach([hydra_texture])

        # Create the debug draw pipeline in the post process graph
        writer = rep.writers.get("RtxLidar" + "DebugDrawPointCloud")
        writer.attach([hydra_texture])

        # Create LaserScan publisher pipeline in the post process graph
        writer = rep.writers.get("RtxLidar" + "ROS2PublishLaserScan")
        writer.initialize(topicName="scan", frameId="base_scan")
        writer.attach([hydra_texture])

        return