import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand, VehicleStatus
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Point

class Commander(Node):
    def __init__(self):
        super().__init__('commander_node')

        # Best Effort QoS profile setting for PX4
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=5
        )

        # Publishers
        self.offboard_mode_pub = self.create_publisher(OffboardControlMode, '/fmu/in/offboard_control_mode', qos_profile)
        self.trajectory_pub = self.create_publisher(TrajectorySetpoint, '/fmu/in/trajectory_setpoint', qos_profile)
        self.vehicle_command_pub = self.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', qos_profile)

        # Subscribers
        self.joy_sub = self.create_subscription(Joy, '/joy', self.joy_callback, 10)
        self.cg_sub = self.create_subscription(Point, 'perception/target_center', self.cgval_callback, 10)

        # Timer for Heartbeat (10Hz is mandatory for Offboard)
        self.timer = self.create_timer(0.1, self.timer_callback)

        # Internal State setting to 0.0 for the start and giving a flag for aruco centered
        self.joy_v_x, self.joy_v_y, self.joy_v_z, self.joy_yaw = 0.0, 0.0, 0.0, 0.0

    def joy_callback(self, msg):
        # mapping the joystick axis for NED control along xyz and yaw
        self.joy_v_x = msg.axes[4] * 2.0   # right stick ud x forward 
        self.joy_v_y = -msg.axes[3] * 2.0  # Right stick lr (Y is negative in NED)
        self.joy_v_z = -msg.axes[1] * 2.0  # left stick ud (Z is negative in NED)
        self.joy_yaw = -msg.axes[0] * 1.5  # yaw left stick lr

        # Button (rb) to Switch to Offboard
        if msg.buttons[5] == 1:
            # VEHICLE CMD DO SET MODE PARAM 1 VALUE 1.0 DENOTES CUSTOM MODE ENABLED AND PARAM 2 VALUE 6.0 DENOTES OFFBOARD CONTROL MODE ENABLED 
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE,param1 = 1.0, param2 = 6.0)

        # Button (lb) to Arm
        if msg.buttons[4] == 1:
            # VEHICLE CMD COMPONENT ARM DISARM VALUE 1.0 FOR ARM AND VALUE 0.0 FOR DISARM 
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, param1=1.0)

    def cgval_callback(self, msg):
        if ((msg.x >= 630 and msg.x <= 650) and (msg.y >= 460 and msg.y <= 490) and (msg.z >= 1.0)):
            # Below command would shut the offboard control and give the control to autopilot for loitering 
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE,param1 = 1.0, param2 = 4.0)
            # cmd nav land will trigger landing on the spot
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_NAV_LAND)

    def timer_callback(self):
        # 1. Publish Heartbeat
        offboard_msg = OffboardControlMode()
        offboard_msg.position, offboard_msg.velocity = False, True
        offboard_msg.acceleration, offboard_msg.attitude, offboard_msg.body_rate = False, False, False
        offboard_msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)  # this is done to publish time in microseconds
        self.offboard_mode_pub.publish(offboard_msg)

        # 2. Publish Velocity Setpoints (NED Frame)
        setpoint_msg = TrajectorySetpoint()
        setpoint_msg.velocity = [self.joy_v_x, self.joy_v_y, self.joy_v_z]
        setpoint_msg.yaw = self.joy_yaw
        setpoint_msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.trajectory_pub.publish(setpoint_msg)

    def publish_vehicle_command(self, command, param1=0.0, param2=0.0):
        msg = VehicleCommand()
        msg.param1, msg.param2 = param1, param2
        msg.command = command
        msg.target_system, msg.target_component = 1, 1
        msg.source_system, msg.source_component = 1, 1
        msg.from_external = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.vehicle_command_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = Commander()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()