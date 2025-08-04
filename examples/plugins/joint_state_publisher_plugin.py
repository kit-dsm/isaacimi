from isaacimi.robot_plugin import ImiRobotPlugin
import omni.graph.core as og

class JointStatePublisherPlugin(ImiRobotPlugin):
    def on_plugin_load(self, namespace, topic_name):
        self.namespace = namespace
        self.topic_name = topic_name
        return
    
    def set_up_scene(self, robot, scene):
        # In the real world, you would have a set of sensors that can measure the joint states, and publish
        # those states to a joint_states topic. However, as this is a simulation, we can get the joint states
        # directly from the simulation and publish them.
        # 
        # This plugin just creates an omnigraph node called ROS2PublishJointState that is already provided
        # by Isaac Sim. Another way to implement this joint state publisher plugin is to create a publisher
        # with self.ros_node.create_publisher(JointState, ...) and use it to publish joint information that
        # can be accessed from the robot instance. Here, we just use the provided omnigraph node for simplicity.
        try:
            og.Controller.edit(
                {"graph_path": f"{robot.prim_path}/JointStatePublisherGraph", "evaluator_name": "execution"},
                {
                    og.Controller.Keys.CREATE_NODES: [
                        ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                        ("PublishJointState", "isaacsim.ros2.bridge.ROS2PublishJointState"),
                        ("ReadSimTime", "isaacsim.core.nodes.IsaacReadSimulationTime"),
                    ],
                    og.Controller.Keys.CONNECT: [
                        ("OnPlaybackTick.outputs:tick", "PublishJointState.inputs:execIn"),
                        ("ReadSimTime.outputs:simulationTime", "PublishJointState.inputs:timeStamp"),
                    ],
                    og.Controller.Keys.SET_VALUES: [
                        # Note: the robot.prim_path property will return the articulation root of the robot
                        ("PublishJointState.inputs:targetPrim", robot.prim_path),
                        ("PublishJointState.inputs:topicName", self.topic_name),
                        ("PublishJointState.inputs:nodeNamespace", self.namespace)
                    ],
                },
            )
        except Exception as e:
            print(e)
        return