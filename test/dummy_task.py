from isaacimi import ImiRobot

from geometry_msgs.msg import Twist

class DummyTask(ImiRobot):
    def __init__(
        self,
        prim_path,
        name,
        usd_path,
        position,
        orientation
    ):
        super().__init__(prim_path, name, usd_path, position, orientation)
        self.add_ros_subscriber(Twist, "cmd_vel", self.velocity_callback, 1)
        return
    
    def velocity_callback(self, data: Twist) -> None:
        print("Velocity callback!")
        return