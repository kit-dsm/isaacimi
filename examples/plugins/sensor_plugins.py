from isaacimi.robot_plugin import ImiRobotPlugin
import omni
from pxr import Gf
import omni.replicator.core as rep

class RTXLidarPlugin(ImiRobotPlugin):
    def on_plugin_load(self, parent_prim, lidar_name, config, translation, rotation, namespace, topic_name, frame_id):
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
        hydra_texture = rep.create.render_product(sensor.GetPath(), [1, 1], name="Isaac")

        # # Create Point cloud publisher pipeline in the post process graph
        writer = rep.writers.get("RtxLidar" + "ROS2PublishPointCloud")
        writer.initialize(topicName=f"/{namespace}/{topic_name}", frameId=frame_id)
        writer.attach([hydra_texture])

        # Create the debug draw pipeline in the post process graph
        writer = rep.writers.get("RtxLidar" + "DebugDrawPointCloud")
        writer.attach([hydra_texture])

        # # Note: LaserScan publisher is not working properly at the moment
        # # Create LaserScan publisher pipeline in the post process graph
        # writer = rep.writers.get("RtxLidar" + "ROS2PublishLaserScan")
        # writer.initialize(topicName="scan", frameId="base_scan")
        # writer.attach([hydra_texture])
        return