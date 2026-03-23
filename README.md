# ROS 2 Jazzy + PX4: Integrated Vision-Based Perception & Offboard Teleoperation for Quadcopter Drone

## 1. Project Overview
This repository demonstrates a high-performance integration of PX4 Autopilot and ROS 2 Jazzy for autonomous and manual UAV operations. This setup was developed to bridge the gap between high-level ROS 2 vision processing and low-level PX4 flight control, proving that a modern Gazebo-Jazzy stack can handle real-time autonomous target tracking. It features a low-latency Micro XRCE-DDS communication pipeline, a custom Joy-to-Offboard teleoperation bridge, and an OpenCV-based ArUco perception system for real-time target acquisition in Gazebo simulation. Designed for modularity, it provides a robust foundation for precision landing and autonomous mission execution.

https://github.com/user-attachments/assets/7c1ae57b-f8a3-4a06-9692-ba177e3a7254

### System Interfacing and data flow 

The project utilizes a modular ROS 2 architecture, leveraging standard bridges to interface the simulation, perception pipeline, and flight controller:

* **Flight Control & Telemetry (Micro XRCE-DDS)**:
  - **Command Link**: Streams VehicleCommand and TrajectorySetpoint messages to PX4 at 10Hz to maintain Offboard mode.
  - **State Feedback** : Subscribes to VehicleOdometry and VehicleStatus uORB topics.
  - **Telemetry Processing** : Extracts and transforms raw data to display real-time Position ($P$), Orientation ($Q$), Velocity ($V$), and Angular Velocity ($\omega$).
* **Simulation Bridge (ros_gz_bridge)**:Facilitates the high-bandwidth transfer of simulated camera sensor data from Gazebo to the ROS 2 environment.
* **Perception Pipeline (cv_bridge)**:Acts as the interface between ROS 2 sensor messages and OpenCV.Converts raw streams into BGR format for real-time ArUco marker detection and coordinate extraction.

## 2. Environment & Dependencies
* **OS:** Ubuntu 24.04 
* **ROS 2:** Jazzy Jalisco
* **Gazebo sim:** version 8.10 
* **PX4 Autopilot:** version 1.17.0
* **Middleware:** MicroXRCE-D Agent
* **Python Dependencies:** `numpy - 1.26.4`, `opencv-contrib-python - 4.11.0.86`
* **ROS2 Package:** `ros-jazzy-cv-bridge` , `ros-jazzy-ros-gz` , `ros-jazzy-joy`

## 3. System Prerequisites. Ignore if already installed 

### Install MicroXRCE-D Agent (Middleware)
Install this in your home directory.
```bash
cd ~
git clone https://github.com/eProsima/Micro-XRCE-DDS-Agent.git
cd Micro-XRCE-DDS-Agent
mkdir build && cd build
cmake ..
make
sudo make install
sudo ldconfig /usr/local/lib/
```

### Install PX4_Autopilot (Flight Controller)
Install this in your home directory.
```bash
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot
bash ./Tools/setup/ubuntu.sh
```
*Note: You must restart your computer after running the ubuntu.sh script.*

### Install Python Packages and Ros2 pkg 
```bash
sudo apt update
sudo apt install ros-jazzy-cv-bridge ros-jazzy-ros-gz ros-jazzy-joy
pip3 install opencv-contrib-python==4.11.0.86 numpy==1.26.4 --break-system-packages
```

## 4. Setup & Build Instructions
Follow the steps below to build the workspace.

```bash
# 1. Clone this repository
git clone https://github.com/MurtazaChulawala/Drone_sim_ws.git
cd Drone_sim_ws

# 2. Clone the required PX4 messages dependency into the src folder
cd src
git clone https://github.com/PX4/px4_msgs.git
cd ..

# 3. Build the workspace the px4_msgs would take longer at first dont worry later it will build much faster from next time onwards
colcon build

# 4. Source the installation
source ./install/setup.bash

# 5. In order to allow PX4 to accept joystick commands we need to change certain parameters
cd ~/PX4-Autopilot
make px4_sitl gz_x500_mono_cam_down_aruco

# Let it load once done we can change the params inside in the following order

# The below param will force px4 to ignore the absense of ground control system
param set NAV_DLL_ACT 0

# The below param will force px4 to ignore the absense of GPS
param set COM_ARM_WO_GPS 1

# The above param will force px4 to only focus on the heartbeat signals from ros2 and not to look for rc signals
param set COM_RC_IN_MODE 4

# The above param will force px4 to stay in offboard control mode
param set COM_RCL_EXCEPT 4

# Note : Remember for the project to work you need to change the param to above values as provided

# The above parameters are to be ran only once in the setup, later px4 will remember those parameter changes and you wont need to perform the same steps in execution

# Once done you can safely terminate with ctrl + c.

# In case you want to return back to default setting for px4 later use the following commands to reset them. 

param set COM_RC_IN_MODE 0
param set COM_RCL_EXCEPT 0
param set NAV_DLL_ACT 1
param set COM_ARM_WO_GPS 0

```
*Note: You must run `source ./install/setup.bash` in every new terminal before executing ROS 2 commands.*

## 5. Execution Sequence
To run the full pipeline, open two separate terminals. 

**Terminal 1: Launch PX4 SITL**
```bash
# Navigate to your PX4-Autopilot directory
cd ~/PX4-Autopilot 
make px4_sitl gz_x500_mono_cam_down_aruco
```

**Terminal 2: Launch MicroXRCE Agent, ROS-GZ Bridge, Telemetry Node, Perception Node, Joy node, Drone Commander Node using ros2 Launch**
```bash
cd Drone_sim_ws
source ./install/setup.bash
ros2 launch drone_bringup drone_sim.launch.py
```

**Connect your joystick and follow the Direction given Below to acheive the control and actuation of the drone inside the Gazebo Sim**
* Press LB button to start rotating the rotors.
* Next press RB button to enter the Offboard control mode.
* Use Right joystick Up and Down motion for forward movement along X (North).
* Use Right joystick left and right motion for Sideways movement along Y (East).
* Use Left joystick Up and Down motion for vertical movement along Z axis.
* Use Left joystick left and right motion for angular Yaw motion along Z axis.
* To land the drone Use Left Joystick and move it downwards till you see the rotors stop spinning.

* Ctrl C both the terminals to end the execution.

## 6. Data Recording
A `rosbag2` was recorded during the simulation, capturing the telemetry and perception data.
* **File Location:** The compressed bag file is located in the root of this repository (`.zip` format) unzip or extrtact the file.
* **Inspected Topics:** `/camera/image_raw`, `/perception/target_center`, `/fmu/out/vehicle_odometry` , `/fmu/in/trajectory_setpoint` , `/fmu/out/vehicle_status_v3` , `/joy`
* To run it follow this command after extraction within the Drone_sim_ws folder below
```bash
ros2 bag play drone_sim_data_bag
```
## 7. Video Demonstration

[![Watch the Demo Video]()](https://LINK_TO_YOUR_DRIVE_VIDEO)

*Click the image above to watch the full system walkthrough and execution video on Google Drive.*

## 8. Future work

*Now that the communication bridge and basic perception are working well, I’m looking to expand on what this drone can do:*

* **Precision Landing**: While I’m happy to have the drone "find" the target, the next step is to close the loop and use the coordinates to run a PID controller to land on the target.
* **GPS denied Navigation**: Real-world missions involve "GPS-denied" environments (indoor environments, under bridges, etc.). I’m looking to use this vision data in conjunction with the IMU and Barometer sensors to run an EKF2 filter so that the drone can know where it is based on what it’s seen.
* **Hardware Deployment**: The end game is to get this code off the laptop and onto a companion computer (Jetson, Pi 5, etc.). Going from SITL to a physical flight controller via a serial cable is where things get serious.
* **Dynamic Obstacle Avoidance**: I’m looking to incorporate Depth or LiDAR data via the bridge. While it’s one thing to locate a target, it’s another thing to navigate to it without hitting anything.

*This repository is the first step toward a fully autonomous, vision-navigated UAV platform. The modularity of the ROS 2 Jazzy / PX4 bridge ensures that as the sensors get better, the logic stays robust.*
