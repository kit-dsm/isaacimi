from isaacimi.robot_plugin import ImiRobotPlugin
import omni
from pxr import Gf
import omni.replicator.core as rep

class RTXLidarPlugin(ImiRobotPlugin):
    def on_plugin_load(self, parent_prim, lidar_name, config, translation, rotation, topic_name, frame_id, data_type):
        # The Isaac Sim documentation explains how to add an RTX LiDAR:
        # https://docs.isaacsim.omniverse.nvidia.com/4.5.0/ros_tutorials/tutorial_ros_sensors.html#adding-an-rtx-lidar-in-standalone
        _, sensor = omni.kit.commands.execute(
            "IsaacSensorCreateRtxLidar",
            path=lidar_name,
            parent=parent_prim,
            config=config, # you need to modify the app.sensors.nv.lidar.profileBaseFolder setting
                           # in the isaacsim/exts/isaacsim.sensors.rtx/config/extension.toml file to 
                           # add your own lidar config, as explained here: https://forums.developer.nvidia.com/t/add-search-path-for-lidar-configs/255352/2
            translation= tuple(translation),
            orientation=Gf.Quatd(*rotation),  # Gf.Quatd is w,i,j,k
        )

        # RTX sensors are cameras and must be assigned to their own render product
        self.hydra_texture = rep.create.render_product(sensor.GetPath(), [1, 1], name="Isaac")
        self.topic_name = topic_name
        self.data_type = data_type
        self.frame_id = frame_id
        return
    
    def set_up_scene(self, robot, scene):
        if self.data_type == "LaserScan":
            # If you would like to publish a LaserScan message, you need to make a change to the lidar config, as described here:
            # https://forums.developer.nvidia.com/t/sick-tim781-lidar-sensor-does-not-publish-lasescan/325798/7
            # Otherwise, your LaserScan data won't get published!
            # Create LaserScan publisher pipeline in the post process graph
            writer = rep.writers.get("RtxLidar" + "ROS2PublishLaserScan")
            writer.initialize(topicName=f"/{robot.name}/{self.topic_name}", frameId=self.frame_id)
            writer.attach([self.hydra_texture])
        elif self.data_type == "PointCloud2":
            # Create Point cloud publisher pipeline in the post process graph
            writer = rep.writers.get("RtxLidar" + "ROS2PublishPointCloud")
            writer.initialize(topicName=f"/{robot.name}/{self.topic_name}", frameId=self.frame_id)
            writer.attach([self.hydra_texture])
        else:
            raise ValueError(f"The provided data type '{self.data_type}' for the RTXLidarPlugin is invalid. Must be 'LaserScan' or 'PointCloud2'.")

        # # Create the debug draw pipeline in the post process graph
        # writer = rep.writers.get("RtxLidar" + "DebugDrawPointCloud")
        # writer.attach([self.hydra_texture])
        return