import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from cv2 import aruco as ar
from geometry_msgs.msg import Point

class ArucoFinder(Node):
    def __init__(self):
        super().__init__("perception_node")
        self.pub_ = self.create_publisher(Point, "/perception/target_center" ,10)
        self.sub_=self.create_subscription(Image, "camera/image_raw", self.image_callback, 10)
        self.cvbridge_ = CvBridge()

    def image_callback(self, msg):
        # 1. Translating ROS2 Image to OpenCV readable Image
        try:
            cv_image = self.cvbridge_.imgmsg_to_cv2(msg, "bgr8")  # to generate an 8 bit per color image (blue green red) 
        except Exception as e:
            self.get_logger().error(f"Translation error: {e}")
            return None

        # 2. Setup the ArUco Dictionary and Detector
        # Using DICT_4X4_50 since the aruco tag is 4*4
        aruco_dict = ar.getPredefinedDictionary(ar.DICT_4X4_50)
        parameters = ar.DetectorParameters()
        # we need to pass the ArucoDetector with the aruco dict and the parameters for detection
        detector = ar.ArucoDetector(aruco_dict, parameters)

        # 3. Detect the markers in the image
        corners, ids, rejected = detector.detectMarkers(cv_image)

        # 4. If a marker is found, process it
        if ids is not None:
            # Drawing a green box around the detected marker
            ar.drawDetectedMarkers(cv_image, corners, ids)

            # Extracting the 4 corners of the detected marker using corners[0][0] gives us [Top-Left, Top-Right, Bottom-Right, Bottom-Left]
            marker_corners = corners[0][0]
            # Calculating the Center X and Center Y point using basic geometry
            center_x = int((marker_corners[0][0] + marker_corners[2][0]) / 2)
            center_y = int((marker_corners[0][1] + marker_corners[2][1]) / 2)

            # Drawing a solid red circle at the calculated center
            cv2.circle(cv_image, (center_x, center_y), 5, (0, 0, 255), -1)

            # Publish the cordinates to the perception/target_center topic
            point = Point()
            point.x = float(center_x)
            point.y = float(center_y)
            point.z = 0.0
            self.pub_.publish(point)
        else:
            self.get_logger().info("Searching for Aruco Code...", throttle_duration_sec=2.0) # while only printing searching for pad every 2 sec

        # 5. Display the live video feed
        cv2.imshow("Drone Downward Camera", cv_image)
        cv2.waitKey(1) # This forces OpenCV to refresh the window       
    
def main(args=None):
    rclpy.init(args=args)
    node = ArucoFinder()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()