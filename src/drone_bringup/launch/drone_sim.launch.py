import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        
        # Running the XRCE agent
        ExecuteProcess(
            cmd=['./MicroXRCEAgent', 'udp4', '-p', '8888'],
            cwd=os.path.expanduser('~/Micro-XRCE-DDS-Agent/build/'), #os.path.expanduser('~') ensures that it points to the running system home directory
            output='screen'
        ),
        # Starting the ros gz Bridge
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/world/aruco/model/x500_mono_cam_down_0/link/camera_link/sensor/camera/image@sensor_msgs/msg/Image[gz.msgs.Image'
            ],
            remappings=[
                ('/world/aruco/model/x500_mono_cam_down_0/link/camera_link/sensor/camera/image', '/camera/image_raw'),
            ],
            output='screen'
        ),
        # Starting Perception Node
        Node(
            package='perception_node', 
            executable='perception_node', 
            output='screen'
        ),

        # Starting Telemetry Logger
        Node(
            package='telemetry_node',
            executable='telemetry_node',
            output='screen'
        ),

        # Starting joy_node
        Node(
            package='joy',
            executable='joy_node',
            output='screen'
        ),
        # Starting Telemetry Logger
        Node(
            package='drone_commander',
            executable='drone_commander',
            output='screen'
        )
    ])