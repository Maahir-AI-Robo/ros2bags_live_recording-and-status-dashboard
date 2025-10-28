#!/bin/bash
# Setup script for ROS2 Dashboard

echo "Setting up ROS2 Dashboard..."

# Check if ROS2 is sourced
if [ -z "$ROS_DISTRO" ]; then
    echo "ERROR: ROS2 is not sourced!"
    echo "Please source your ROS2 installation first:"
    echo "  source /opt/ros/<distro>/setup.bash"
    exit 1
fi

echo "ROS2 Distribution: $ROS_DISTRO"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Create default recordings directory
recordings_dir="$HOME/ros2_recordings"
if [ ! -d "$recordings_dir" ]; then
    mkdir -p "$recordings_dir"
    echo "Created recordings directory: $recordings_dir"
fi

# Make main.py executable
chmod +x main.py

echo ""
echo "Setup complete!"
echo ""
echo "To run the dashboard:"
echo "  python3 main.py"
echo ""
echo "Or make it executable and run directly:"
echo "  ./main.py"
echo ""
