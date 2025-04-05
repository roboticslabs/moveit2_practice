import rclpy
from rclpy.node import Node
from control_msgs.msg import JointTrajectoryControllerState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import sys
import tty
import termios

class PandaJointController(Node):
    def __init__(self):
        super().__init__('panda_joint_controller')
        # publisher that publish to "/panda_arm_controller/joint_trajectory" topic
        self.publisher_ = self.create_publisher(JointTrajectory, '/panda_arm_controller/joint_trajectory', 10)
        # joint name list
        self.joint_names = ['panda_joint1', 'panda_joint2', 'panda_joint3', 'panda_joint4', 'panda_joint5', 'panda_joint6', 'panda_joint7']
        # initialize joint position
        self.joint_positions = [0.0] * 7
        # joint position step
        self.step = 0.1

    def get_key(self):
        # get input key
        settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        return key

    def send_trajectory(self):
        # create JointTrajectory msg
        trajectory_msg = JointTrajectory()
        trajectory_msg.joint_names = self.joint_names

        # create JointTrajectoryPoint and set target pos
        point = JointTrajectoryPoint()
        point.positions = self.joint_positions
        # set move time
        point.time_from_start = rclpy.duration.Duration(seconds=1).to_msg()

        # add point to path
        trajectory_msg.points.append(point)

        # publish path msg
        self.publisher_.publish(trajectory_msg)
        self.get_logger().info('Sent joint trajectory command')

    def run(self):
        while rclpy.ok():
            key = self.get_key()
            if key == '-':   # - and no. for reverse movement
                self.minus_pressed = True
            elif key in ['1', '2', '3', '4', '5', '6', '7']:
                index = int(key) - 1 
                if self.minus_pressed:
                    self.joint_positions[index] -= self.step
                    self.minus_pressed = False
                else:
                    self.joint_positions[index] += self.step
                self.send_trajectory()  # call send_traj to pub the control
            elif key == '\x03':  # Ctrl+C 
                break

def main(args=None):
    rclpy.init(args=args)
    panda_joint_controller = PandaJointController()
    panda_joint_controller.run()
    panda_joint_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()