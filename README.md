# Drone Simulation in Gazebo via PX4 SITL with Vision-Based Target Tracking using ROS 2, OpenCV, and ArUco Markers

## 1. Project Overview
This repository contains a ROS 2 Jazzy workspace with a PX4 Software-In-The-Loop (SITL) simulation. It shows a complete process that connects PX4 telemetry and simulated camera data to ROS 2. Additionally, it runs an event based perception node to identify and mark the ArUco Marker.

## 2. Environment & Dependencies
* **OS:** Ubuntu 24.04 
* **ROS 2:** Jazzy Jalisco
* **Gazebo sim:** version 8.10 
* **PX4 Autopilot:** version 1.17.0
* **Middleware:** MicroXRCE-D Agent
* **Python Dependencies:** `numpy - 1.26.4`, `opencv-contrib-python - 4.11.0.86`
* **ROS2 Package:** `ros-jazzy-cv-bridge` , `ros-jazzy-ros-gz`

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
sudo apt install ros-jazzy-cv-bridge ros-jazzy-ros-gz
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
source install/setup.bash
```
*Note: You must run `source install/setup.bash` in every new terminal before executing ROS 2 commands.*

## 5. Execution Sequence
To run the full pipeline, open two separate terminals. 

**Terminal 1: Launch PX4 SITL**
```bash
# Navigate to your PX4-Autopilot directory
cd ~/PX4-Autopilot 
make px4_sitl gz_x500_mono_cam_down_aruco
```

**Terminal 2: Launch MicroXRCE Agent, ROS-GZ Bridge, Telemetry Node, Perception Node using ros2 Launch**
```bash
source install/setup.bash
ros2 launch drone_bringup drone_sim.launch.py
```

**Go back to Terminal 1 where your PX4 is running and enter the commands for takeoff and landing**
```bash
commander arm -f    #This will force the propeller motors to spin
commander takeoff   #Once the motor spins the drone will use this command for takeoff
commander land      #You can use commander land command to land the drone on the spot
```

## 6. Data Recording
A `rosbag2` was recorded during the simulation, capturing the telemetry and perception data.
* **File Location:** The compressed bag file is located in the root of this repository (`.zip` format).
* **Extraction Note:** Please unzip the file to access the full `.mcap` data (expands to ~6.6GB).
* **Inspected Topics:** `/camera/image_raw`, `/perception/target_center`, `/fmu/out/vehicle_odometry`, `/fmu/out/vehicle_status`
* To run it follow this command after extraction within the Drone_sim_ws folder below
```bash
ros2 bag play drone_sim_data_ros2_bag
```

## 7. Screen Recording with Explanation
**Google Drive link of the screen recording :** [Screen Recording](https://github.com/MurtazaChulawala/Drone_sim_ws.git)
