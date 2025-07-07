from isaacimi.robot_plugin import ImiRobotPlugin

from geometry_msgs.msg import Twist
from std_msgs.msg import Int8
from nav_msgs.msg import Odometry
from rclpy.time import Time

import numpy as np
import math

class DummyRobotControllerPlugin(ImiRobotPlugin):   
    def on_plugin_load(self):
        self.ros_node.create_subscription(Twist, "cmd_vel", self.velocity_callback, 1)
        self.lin_vel_cmd = np.zeros(3)
        self.ang_vel_cmd = np.zeros(3)

        self.ros_node.create_subscription(Int8, "cmd_lift", self.lift_callback, 1)
        self.lift_direction = 0 # either -1, 0, or +1
        self.max_lift_moving_speed = 0.25
        self.lift_active = False

        # TODO: lift position publisher
        # the evorobot publishes lift position by publishing the positions (in mm) of the four lift motors to four different publishers
        # i.e. lift/1/position, lift/2/position, ..., lift/4/position

        self.odom_pub = self.ros_node.create_publisher(Odometry, "odom", 1)
        self.odom_pose = np.zeros(3) # only keep track of x, y, yaw

        self.pre_step_time = 0 # used to calculate step size in pre_physics_step
        return

    def velocity_callback(self, data: Twist) -> None:
        self.lin_vel_cmd[0] = data.linear.x
        self.lin_vel_cmd[1] = data.linear.y
        self.lin_vel_cmd[2] = data.linear.z
        self.ang_vel_cmd[0] = data.angular.x
        self.ang_vel_cmd[1] = data.angular.y
        self.ang_vel_cmd[2] = data.angular.z
        return

    def lift_callback(self, data: Int8) -> None:
        self.lift_direction = data.data

    def pre_physics_step(self, robot, time_step_index, simulation_time):
        dt = simulation_time - self.pre_step_time
        self.pre_step_time = simulation_time

        # typically, you would use wheel data (+ other sensor data) to determine odometry
        # however, as a shortcut, we know that the velocity of the robot in the child frame
        # is the same as the most recent cmd_vel that we gave it. We can determine odom pose
        # by integrating the velocity
        odom_msg = Odometry()
        seconds = int(simulation_time)
        nanoseconds = int((simulation_time - seconds) * 1e9)
        odom_msg.header.stamp = Time(seconds=seconds, nanoseconds=nanoseconds).to_msg() # you can also do self.ros_node.get_clock().now().to_msg() which will
                                                                                        # return the world time. If you set the node parameter use_sim_time 
                                                                                        # to true it will return the simulated time. By default, use_sim_time is true.
        odom_msg.header.frame_id = "odom"
        odom_msg.child_frame_id  = "base_footprint"

        # this section is incorrect
        position_increment = self.lin_vel_cmd * dt
        orientation_increment = self.ang_vel_cmd * dt

        curr_odom_yaw = self.odom_pose[2]
        self.odom_pose[0] += math.cos(curr_odom_yaw) * position_increment[0] - math.sin(curr_odom_yaw) - position_increment[1] # x
        self.odom_pose[1] += math.sin(curr_odom_yaw) * position_increment[0] + math.cos(curr_odom_yaw) - position_increment[1] # y
        self.odom_pose[2] += orientation_increment[2] # yaw
        # --------

        odom_msg.pose.pose.position.x = float(self.odom_pose[0])
        odom_msg.pose.pose.position.y = float(self.odom_pose[1])
        odom_msg.pose.pose.orientation = yaw_to_ros_quaternion(self.odom_pose[2])

        print(f"dt: {dt}, odom_pose(rpy): {self.odom_pose}, position increment: {position_increment}, orientation_increment{orientation_increment}, yaw {self.odom_pose[2]}")

        odom_msg.twist.twist.linear.x = float(self.lin_vel_cmd[0])
        odom_msg.twist.twist.linear.y = float(self.lin_vel_cmd[1])
        odom_msg.twist.twist.linear.z = float(self.lin_vel_cmd[2])
        odom_msg.twist.twist.angular.x = float(self.ang_vel_cmd[0])
        odom_msg.twist.twist.angular.y = float(self.ang_vel_cmd[1])
        odom_msg.twist.twist.angular.z = float(self.ang_vel_cmd[2])

        # todo
        odom_msg.twist.covariance = np.array([0.1, 0.0, 0.0, 0.0, 0.0, 0.0,   
                                              0.0, 0.1, 0.0, 0.0, 0.0, 0.0, 
                                              0.0, 0.0, 0.1, 0.0, 0.0, 0.0,
                                              0.0, 0.0, 0.0, 0.1, 0.0, 0.0,   
                                              0.0, 0.0, 0.0, 0.0, 0.1, 0.0, 
                                              0.0, 0.0, 0.0, 0.0, 0.0, 0.1])
        odom_msg.pose.covariance = odom_msg.twist.covariance
        
        self.odom_pub.publish(odom_msg)
        return
    
    def on_physics_step(self, robot, step_size) -> None:
        # todo publish odom tf
        # todo publish joint states

        if self.lift_direction == 0:
            self.lift_active = False
            # set_linear_velocity and set_angular_velocity methods assume the input is in the parent frame
            # incoming messages in /cmd_vel are in the child (robot) frame, so we need to convert it to the parent frame
            _, orientation = robot.get_world_pose()
            rotation_matrix = quaternion_rotation_matrix(orientation)
            lin_vel_cmd_rotated = rotation_matrix.dot(self.lin_vel_cmd)
            ang_vel_cmd_rotated = rotation_matrix.dot(self.ang_vel_cmd)

            robot.set_linear_velocity(lin_vel_cmd_rotated)
            robot.set_angular_velocity(ang_vel_cmd_rotated)
        else:
            self.lift_active = True
            if self.lift_direction > 0:
                robot.set_joint_velocities(np.array([+self.max_lift_moving_speed]))
            else:
                robot.set_joint_velocities(np.array([-self.max_lift_moving_speed]))
        return
    
def quaternion_rotation_matrix(Q):
    # Extract the values from Q
    q0 = Q[0]
    q1 = Q[1]
    q2 = Q[2]
    q3 = Q[3]
    # First row of the rotation matrix
    r00 = 2 * (q0 * q0 + q1 * q1) - 1
    r01 = 2 * (q1 * q2 - q0 * q3)
    r02 = 2 * (q1 * q3 + q0 * q2)
    # Second row of the rotation matrix
    r10 = 2 * (q1 * q2 + q0 * q3)
    r11 = 2 * (q0 * q0 + q2 * q2) - 1
    r12 = 2 * (q2 * q3 - q0 * q1)
    # Third row of the rotation matrix
    r20 = 2 * (q1 * q3 - q0 * q2)
    r21 = 2 * (q2 * q3 + q0 * q1)
    r22 = 2 * (q0 * q0 + q3 * q3) - 1
    # 3x3 rotation matrix
    rot_matrix = np.array([[r00, r01, r02],
                           [r10, r11, r12],
                           [r20, r21, r22]])            
    return rot_matrix

from geometry_msgs.msg import Quaternion
def yaw_to_ros_quaternion(yaw):
    q = Quaternion()
    q.z = math.sin(yaw / 2.0)
    q.w = math.cos(yaw / 2.0)
    return q


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