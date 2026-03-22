import rclpy
from rclpy.node import Node
from px4_msgs.msg import VehicleOdometry
from rclpy.qos import qos_profile_sensor_data

class logger(Node):
    def __init__(self):
        super().__init__("telemetry_node")
        self.sub_ = self.create_subscription(VehicleOdometry, "fmu/out/vehicle_odometry", self.telemetry_callback, qos_profile_sensor_data)

    def telemetry_callback(self, msg):
        log = (f"Listening to Vehicle Odometry\n\nPrinting the Position \n{msg.position}\n ------------\nPrinting the Q \n{msg.q}\n ------------\nPrinting the Velocity \n{msg.velocity}\n ------------\nPrinting the Angular Velocity \n{msg.angular_velocity}\n ------------\n")
        self.get_logger().info(log, throttle_duration_sec = 1.0)
def main(args=None):
    rclpy.init(args=args)
    node = logger()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()