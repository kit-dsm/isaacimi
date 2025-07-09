from isaacimi.robot_plugin import ImiRobotPlugin

from geometry_msgs.msg import Twist, Quaternion, TransformStamped
from std_msgs.msg import Int8
from nav_msgs.msg import Odometry
from rclpy.time import Time
from tf2_ros import TransformBroadcaster
from std_srvs.srv import Empty

import numpy as np
import math

# todo: enable developers to use custom messages and services defined in other ros packages
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

        self.tf_odom_broadcaster = TransformBroadcaster(self.ros_node)

        self.srv_reset_odom = self.ros_node.create_service(Empty, "reset_odom", self.reset_odom_callback)

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
                                                                                        # to true it will return the simulated time. By default, use_sim_time is false
                                                                                        # by default, but for all plugins it has been set to true.
        odom_msg.header.frame_id = "odom"
        odom_msg.child_frame_id  = "base_footprint"

        curr_odom_yaw = self.odom_pose[2]
        self.odom_pose[0] += (math.cos(curr_odom_yaw) * self.lin_vel_cmd[0] - math.sin(curr_odom_yaw) * self.lin_vel_cmd[1]) * dt # x
        self.odom_pose[1] += (math.sin(curr_odom_yaw) * self.lin_vel_cmd[0] + math.cos(curr_odom_yaw) * self.lin_vel_cmd[1]) * dt # y
        self.odom_pose[2] = wrap_angle_rad(self.odom_pose[2] + self.ang_vel_cmd[2] * dt) # yaw
        
        odom_msg.pose.pose.position.x = float(self.odom_pose[0])
        odom_msg.pose.pose.position.y = float(self.odom_pose[1])
        odom_orientation_q = yaw_to_quaternion(self.odom_pose[2])
        odom_msg.pose.pose.orientation = Quaternion(w=odom_orientation_q[0], x=odom_orientation_q[1], y=odom_orientation_q[2], z=odom_orientation_q[3])

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
        
        transform = TransformStamped()
        transform.header.stamp = odom_msg.header.stamp
        transform.header.frame_id = "odom"

        transform.child_frame_id = "base_footprint"
        transform.transform.translation.x = odom_msg.pose.pose.position.x
        transform.transform.translation.y = odom_msg.pose.pose.position.y 
        transform.transform.translation.z = odom_msg.pose.pose.position.z

        transform.transform.rotation = odom_msg.pose.pose.orientation

        self.tf_odom_broadcaster.sendTransform(transform)
        return
    
    def on_physics_step(self, robot, step_size) -> None:
        # todo publish odom tf
        # todo publish joint states

        if self.lift_direction == 0:
            self.lift_active = False

            # I had trouble using robot.set_angular_velocity() and robot.set_linear_velocity()
            # It doesn't directly set the velocity of the robot in the world - I believe it accounts
            # for physics (friction, mass, gravity)
            # To simplify things, I just set the position of the cube in the world
            position, orientation = robot.get_world_pose()

            orientation_as_matrix = quaternion_rotation_matrix(orientation)
            lin_vel_cmd_rotated = orientation_as_matrix.dot(self.lin_vel_cmd)

            position += lin_vel_cmd_rotated * step_size
            orientation = quaternion_multiply(orientation, rpy_to_quaternion(self.ang_vel_cmd * step_size))
            robot.set_world_pose(position, orientation)
        else:
            self.lift_active = True
            if self.lift_direction > 0:
                robot.set_joint_velocities(np.array([+self.max_lift_moving_speed]))
            else:
                robot.set_joint_velocities(np.array([-self.max_lift_moving_speed]))
        return
    
    def reset_odom_callback(self, request, response):
        self.lin_vel_cmd = np.zeros(3)
        self.ang_vel_cmd = np.zeros(3)
        self.odom_pose = np.zeros(3)
        return response
    
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

def wrap_angle_rad(angle_rad):
    return ((angle_rad + math.pi) % (2 * math.pi)) - math.pi

def yaw_to_quaternion(yaw):
    return np.array([math.cos(yaw / 2.0), 0, 0, math.sin(yaw / 2.0)])

def rpy_to_quaternion(rpy):
    """
    Convert roll, pitch, yaw to quaternion using numpy arrays.

    Args:
        rpy: np.array of shape (3,) -> [roll, pitch, yaw] in radians

    Returns:
        np.array of shape (4,) -> [x, y, z, w] quaternion
    """
    roll, pitch, yaw = rpy
    cy = np.cos(yaw * 0.5)
    sy = np.sin(yaw * 0.5)
    cp = np.cos(pitch * 0.5)
    sp = np.sin(pitch * 0.5)
    cr = np.cos(roll * 0.5)
    sr = np.sin(roll * 0.5)
    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy
    return np.array([w, x, y, z])

def quaternion_multiply(q1, q2): # result is q2 * q1
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    w = w2*w1 - x2*x1 - y2*y1 - z2*z1
    x = w2*x1 + x2*w1 + y2*z1 - z2*y1
    y = w2*y1 - x2*z1 + y2*w1 + z2*x1
    z = w2*z1 + x2*y1 - y2*x1 + z2*w1
    return np.array([w, x, y, z])

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