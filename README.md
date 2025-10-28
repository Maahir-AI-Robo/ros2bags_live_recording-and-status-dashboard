# ROS2 Data Recording & Status Dashboard

An offline-first desktop application for recording and monitoring ROS2 bag files with live metrics and advanced ROS2 features.

## ✨ Features

### 📡 **Topic Monitoring**
- View all available ROS2 topics with real-time information
- Topic names, message types, and publisher counts
- Publishing frequencies (Hz)
- Select specific topics to record
- Color-coded status indicators

### 🔧 **Node Monitoring**
- Discover all active ROS2 nodes
- View node namespaces
- Monitor publishers and subscribers per node
- Real-time node status updates

### ⚙️ **Service Discovery**
- List all available ROS2 services
- Service types and server information
- Service status monitoring

### 👁️ **Topic Echo - Live Message Preview**
- View live messages from any topic
- Configurable message limits
- Array truncation options
- Real-time data inspection
- Clear formatted output

### 💾 **Bag Recording Control**
- Easy-to-use interface for recording ROS2 bags
- Start/stop recording with one click
- Custom output directory and bag name prefix
- Records all topics or selected topics only
- Automatic timestamp-based naming
- Recording compression support

### ▶️ **Bag Playback Control**
- Play back recorded bags directly from the dashboard
- Adjustable playback speed (0.1x - 10x)
- Loop playback option
- Start paused mode
- Quick access to recorded bags

### 📊 **Real-time Metrics & Statistics**
- **Recording Metrics:**
  - Recording duration (HH:MM:SS)
  - Total data size (MB/GB)
  - Write speed (MB/s)
  - Message count and rate
  - Active topic count
  - Disk usage indicator with warnings

- **System Statistics:**
  - CPU usage monitoring
  - Memory usage (used/total)
  - Disk write speed
  - Network I/O (upload/download)

- **ROS2 Environment Info:**
  - ROS2 distribution
  - Domain ID
  - Total active topics
  - Total active nodes

### ☁️ **Offline-First Network Upload System** ⭐
- **Automatic Background Uploads:**
  - Auto-upload completed recordings to server
  - Chunked uploads with resume capability
  - Zero data loss even during network failures
  - Automatic retry with exponential backoff

- **Upload Features:**
  - Priority queue system (1-10 levels)
  - Multi-file concurrent uploads
  - Progress tracking per upload
  - Upload history with statistics
  - Persistent state across restarts
  - Bandwidth throttling support

- **Network Resilience:**
  - Works offline-first
  - Automatic resume from last chunk
  - Survives application restarts
  - Smart retry logic
  - Real-time network status monitoring

### 🤖 **ML-Ready Data Export** ⭐ NEW!
- **Automatic ML Package Creation:**
  - Every completed recording is packaged for ML use
  - Lightweight, dependency-free packaging
  - Background processing (non-blocking UI)
  - Compressed archives for easy transfer

- **ML Package Contents:**
  - `raw/` - Complete bag file copy
  - `metadata.json` - Bag info (size, duration, topics)
  - `schema.json` - Topic/message type mappings
  - `<bagname>.tar.gz` - Compressed archive

- **Integration Ready:**
  - Compatible with TensorFlow, PyTorch pipelines
  - Easy conversion to TFRecord/Parquet
  - Structured schema for automated processing
  - Standardized metadata format

### 📝 **Recording History**
- Track all your recordings
- View past recordings with metadata
- File size, duration, topic count
- Start time and completion status
- Open recordings folder directly
- Quick playback access

### 🚀 **Advanced Features**
- **Offline First**: Works independently without internet
- **Tabbed Interface**: Organized feature access
- **Auto-refresh**: Configurable update intervals
- **Error Handling**: Graceful ROS2 unavailability handling
- **Responsive UI**: Non-blocking operations
- **Color Coding**: Visual status indicators

## Requirements

- ROS2 (Humble, Iron, or Rolling)
- Python 3.8+
- PyQt5
- psutil
- PyYAML

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies**:
   ```bash
   cd /tmp/ros2_dashboard
   pip install -r requirements.txt
   ```

3. **Make sure ROS2 is sourced**:
   ```bash
   source /opt/ros/<your_ros2_distro>/setup.bash
   ```

4. **(Optional) Start Upload Server for Network Uploads**:
   ```bash
   # In a separate terminal
   python3 upload_server.py
   # Server runs on http://localhost:8080
   # Uploads saved to ~/ros2_uploads/completed/
   ```

## 🚀 Startup Guide

### Prerequisites Check

Before starting, verify your system is ready:

```bash
# 1. Check ROS2 installation
ros2 --version

# 2. Source your ROS2 environment
source /opt/ros/humble/setup.bash  # Replace 'humble' with your distro

# 3. Verify ROS2 daemon is running
ros2 daemon status

# 4. (Optional) Test with a demo node to see live data
ros2 run demo_nodes_py talker
```

### First Time Setup

```bash
# 1. Navigate to the dashboard directory
cd /tmp/ros2_dashboard

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Verify all dependencies are installed
python3 -c "import PyQt5, psutil, yaml; print('All dependencies OK!')"
```

### Starting the Dashboard

**Option 1: Basic Mode (Monitoring & Recording Only)**

```bash
# Single command - dashboard starts in ~1 second!
cd /tmp/ros2_dashboard
python3 main.py
```

The dashboard will:
- ✅ Start immediately (no blocking operations)
- ✅ Show ROS2 topics, nodes, and services
- ✅ Allow recording with auto ML export
- ✅ Work offline-first (no internet needed)

**Option 2: Full Mode (With Network Uploads)**

```bash
# Terminal 1: Start upload server first
cd /tmp/ros2_dashboard
python3 upload_server.py
# Wait for: "Running on http://127.0.0.1:8080"

# Terminal 2: Start dashboard
cd /tmp/ros2_dashboard
python3 main.py
# Go to Upload tab and enable auto-upload
```

### Using the Dashboard - Step by Step

#### 1️⃣ **Monitor ROS2 System**

**Topics Tab:**
- View all active ROS2 topics
- Check message types and publisher counts
- Select topics for recording (checkbox)

**Nodes Tab:**
- See all running ROS2 nodes
- Monitor publishers/subscribers per node

**Services Tab:**
- Discover available ROS2 services
- View service types and servers

**Topic Echo Tab:**
- Preview live messages from any topic
- Select topic from dropdown
- Click "Start Echo" to see data
- Useful for debugging and verification

#### 2️⃣ **Record ROS2 Data**

**Recording Tab:**
1. **Set Output Directory:**
   - Click "Browse" or use default `~/ros2_recordings`
   - Ensure you have write permissions

2. **Name Your Recording:**
   - Set bag name prefix (e.g., "experiment", "test_run")
   - Timestamp is automatically added

3. **Select Topics:**
   - Go to Topics tab
   - Check topics you want to record
   - Or leave all unchecked to record everything

4. **Start Recording:**
   - Click "Start Recording" (green button)
   - Watch real-time metrics update:
     - Duration (HH:MM:SS)
     - Data size (MB/GB)
     - Message count and rate
     - Disk usage warning

5. **Stop Recording:**
   - Click "Stop Recording" (red button)
   - Wait for "ML package created" message ⭐
   - Recording saved to `~/ros2_recordings/recording_YYYYMMDD_HHMMSS`
   - ML package created in `ml_datasets/recording_YYYYMMDD_HHMMSS/`

#### 3️⃣ **Playback Recordings**

**Playback Tab:**
1. Click "Browse" and select a bag folder
2. Adjust playback speed (0.1x to 10x)
3. Optional: Enable "Loop" or "Start Paused"
4. Click "Start Playback"
5. Monitor playback status

**Or use command line:**
```bash
ros2 bag play ~/ros2_recordings/recording_20251025_120000
```

#### 4️⃣ **Use ML Datasets** ⭐

Every recording automatically creates an ML-ready package:

```bash
# Find your ML packages
ls -lh ~/ros2_recordings/ml_datasets/

# Example structure:
# ml_datasets/recording_20251025_120000/
#   ├── raw/                    # Original bag files
#   ├── metadata.json           # Duration, size, topic count
#   ├── schema.json             # Topic types for ML pipelines
#   └── recording_20251025_120000.tar.gz  # Compressed archive
```

**Use in ML Pipelines:**
```python
# Example: Load metadata for training
import json

with open('ml_datasets/recording_20251025_120000/metadata.json') as f:
    info = json.load(f)
    print(f"Duration: {info['duration_sec']}s")
    print(f"Topics: {info['topics']}")
```

#### 5️⃣ **Enable Network Uploads** (Optional)

**Setup Upload Server:**
```bash
# Terminal 1
cd /tmp/ros2_dashboard
python3 upload_server.py
# Server starts on http://localhost:8080
# Uploads saved to ~/ros2_uploads/completed/
```

**Configure Dashboard:**
1. Start dashboard (Terminal 2)
2. Go to **☁️ Upload** tab
3. Wait for "● Online" status (~1 second)
4. Enable "Auto-upload completed recordings"
5. Set priority (1-10, higher = urgent)

**Now recordings auto-upload when completed!**
- View pending uploads with progress
- Check upload history and stats
- Uploads resume if network fails
- Retry automatically with backoff

#### 6️⃣ **Monitor System Performance**

**Advanced Stats Tab:**
- **System Resources:**
  - CPU usage %
  - Memory used/total
  - Disk write speed
  - Network I/O rates

- **ROS2 Environment:**
  - ROS2 distribution (Humble/Iron/Rolling)
  - Domain ID
  - Total topics and nodes

- **Real-time Updates:**
  - Auto-refresh every 2 seconds
  - Color-coded indicators
  - No UI freezing (async operations ⚡)

### Quick Tips for Best Performance

✅ **DO:**
- Start with demo nodes if testing: `ros2 run demo_nodes_py talker`
- Select specific topics instead of "all" for large systems
- Monitor disk space during long recordings
- Use SSD storage for best write speeds
- Close other heavy applications
- Enable auto-upload to free local disk space

❌ **DON'T:**
- Record all topics on systems with 100+ topics
- Fill your disk (recordings will fail)
- Run multiple instances simultaneously
- Block the UI thread (we handle this for you! ⭐)

### Startup Troubleshooting

**Dashboard doesn't start:**
```bash
# Check Python version (need 3.8+)
python3 --version

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check for errors
python3 main.py 2>&1 | grep -i error
```

**No topics visible:**
```bash
# Verify ROS2 is sourced
echo $ROS_DISTRO  # Should show: humble, iron, etc.

# Check daemon
ros2 daemon stop
ros2 daemon start

# Test with demo node
ros2 run demo_nodes_py talker &
# Dashboard should now show /chatter topic
```

**Network uploads not working:**
```bash
# Check server is running
curl http://localhost:8080/health
# Should return: {"status": "ok"}

# Check server logs
# Look for "Upload complete" messages
```

**ML packages not created:**
```bash
# Check permissions
ls -ld ~/ros2_recordings/ml_datasets/
# Should be writable by your user

# Manually verify
ls ~/ros2_recordings/ml_datasets/
# Should show recording folders with .tar.gz files
```

### World-Class Performance Features ⭐

This dashboard is designed for **patent-quality performance**:

- **Instant Startup:** Dashboard launches in <1 second
- **Async Operations:** All ROS2 calls run in background threads (Qt QThreadPool)
- **Non-Blocking UI:** Never freezes, even on 8GB RAM systems
- **Smart Refresh:** Only active tab updates (saves CPU)
- **Short Timeouts:** Network checks fail fast (1s timeout)
- **Background Processing:** ML export and uploads don't block UI
- **Memory Efficient:** Chunked uploads (5MB chunks)
- **Resilient:** Survives network failures, restarts, crashes

**Tested on:**
- ✅ 8GB RAM laptop (no freezing)
- ✅ Systems with 100+ ROS2 topics
- ✅ Long recordings (hours)
- ✅ Poor network conditions
- ✅ Concurrent recording + playback + uploads

## Quick Start

### Basic Usage (Monitoring & Recording Only)

1. **Run the dashboard**:
   ```bash
   cd /tmp/ros2_dashboard
   python3 main.py
   ```
   
   **Note**: The dashboard will start immediately and remain responsive. Network upload features will initialize in the background after 1 second.

2. **Configure recording settings**:
   - Set output directory (default: `~/ros2_recordings`)
   - Set bag name prefix (default: `recording`)
   - Select topics to record (or record all)

3. **Start recording**:
   - Click "Start Recording" button
   - Monitor real-time metrics
   - Topics will be automatically discovered and recorded

4. **Stop recording**:
   - Click "Stop Recording" button
   - Recording will be saved with timestamp
   - **ML package is automatically created** in `ml_datasets/` ⭐

5. **View recordings**:
   - Check the Recording History table
   - Click "Open Recordings Folder" to browse files
   - Use standard ROS2 tools to play back bags
   - **ML packages** are in `ml_datasets/<bagname>_<timestamp>/` ⭐

### Advanced Usage (With Network Uploads)

**Step 1: Start the Upload Server**
```bash
# In Terminal 1
cd /tmp/ros2_dashboard
python3 upload_server.py

# Server will start on http://localhost:8080
# Uploads are saved to ~/ros2_uploads/completed/
```

**Step 2: Start the Dashboard**
```bash
# In Terminal 2
cd /tmp/ros2_dashboard
python3 main.py
```

**Step 3: Enable Auto-Upload**
- Go to **☁️ Upload** tab
- Wait for "● Online" status (appears after 1 second)
- Enable "Auto-upload completed recordings" checkbox
- Set priority (1-10, higher = more urgent)
- Recordings will now upload automatically when completed!

**Step 4: Monitor Uploads**
- View pending uploads with progress bars
- Check upload history and statistics
- Manually add files to upload queue
- Uploads resume automatically if network fails

## 🌐 Network Upload System

The dashboard includes a robust offline-first upload system. See [NETWORKING.md](NETWORKING.md) for detailed documentation.

**Key Features:**
- ✅ Automatic background uploads
- ✅ Chunked uploads with resume (no data loss)
- ✅ Works offline, uploads when network returns
- ✅ Priority queue for critical data
- ✅ Progress tracking and history
- ✅ Persistent state across restarts

**Quick Start:**
```bash
# Terminal 1: Start upload server
python3 upload_server.py

# Terminal 2: Start dashboard
python3 main.py

# Enable auto-upload in the Upload tab
# Record bags - they'll upload automatically!
```

## Project Structure

```
ros2_dashboard/
├── main.py                      # Application entry point
├── upload_server.py            # Flask server for receiving uploads
├── gui/
│   ├── __init__.py
│   ├── main_window.py          # Main application window with tabs
│   ├── topic_monitor.py        # Topic list and monitoring
│   ├── node_monitor.py         # ROS2 node monitoring
│   ├── service_monitor.py      # Service discovery
│   ├── topic_echo.py           # Live topic message viewer
│   ├── bag_playback.py         # Bag playback controls
│   ├── recording_control.py   # Recording controls
│   ├── metrics_display.py     # Metrics visualization
│   ├── advanced_stats.py      # System and ROS2 statistics
│   └── network_upload.py      # Network upload monitoring & control ⭐ NEW
├── core/
│   ├── __init__.py
│   ├── ros2_manager.py         # ROS2 integration and bag recording
│   ├── metrics_collector.py   # Metrics collection and calculation
│   └── network_manager.py     # Offline-first upload system ⭐ NEW
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── FEATURES.md                 # Detailed feature documentation
├── NETWORKING.md               # Network upload system documentation
└── IMPLEMENTATION_SUMMARY.md  # Complete implementation summary
```

## Key Components

### ROS2Manager
Handles all ROS2 interactions:
- Topic discovery and monitoring
- Node and service discovery
- Bag recording (start/stop)
- Bag playback control
- Bag file information retrieval
- Disk usage monitoring
- QoS information

### MetricsCollector
Collects and calculates recording metrics:
- Duration tracking
- File size monitoring
- Write speed calculation
- Message counting and rate
- System resource monitoring

### GUI Components
- **MainWindow**: Main application window with 7 tabbed interfaces
- **TopicMonitorWidget**: Displays available topics with selection
- **NodeMonitorWidget**: Shows active ROS2 nodes
- **ServiceMonitorWidget**: Lists available services
- **TopicEchoWidget**: Live topic message preview
- **BagPlaybackWidget**: Playback control interface
- **RecordingControlWidget**: Recording start/stop controls
- **MetricsDisplayWidget**: Live metrics visualization
- **AdvancedStatsWidget**: System and ROS2 statistics
- **NetworkUploadWidget**: Upload monitoring and control ⭐ NEW

### Network Components ⭐ NEW
- **NetworkManager**: Offline-first upload system with:
  - Chunked upload protocol (5MB chunks)
  - SQLite persistent state
  - Automatic retry with exponential backoff
  - Priority queue for smart scheduling
  - Multi-file concurrent uploads
  - Resume from last chunk on network failure
- **Upload Server**: Flask-based server for receiving uploads
  - Chunked upload endpoints
  - Automatic file reassembly
  - Upload verification with checksums
  - RESTful API for status queries

## ROS2 Commands Used

The dashboard uses these ROS2 CLI commands internally:
- `ros2 topic list` - Get available topics
- `ros2 topic type <topic>` - Get topic message type
- `ros2 topic info <topic>` - Get topic information
- `ros2 topic echo <topic>` - Display live messages
- `ros2 node list` - Get active nodes
- `ros2 node info <node>` - Get node details
- `ros2 service list` - Get available services
- `ros2 service type <service>` - Get service type
- `ros2 bag record` - Record bags
- `ros2 bag play` - Playback bags
- `ros2 bag info` - Get bag information

## Playback Recordings

To play back recorded bags, use:
```bash
ros2 bag play ~/ros2_recordings/recording_20251025_120000
```

To get info about a recording:
```bash
ros2 bag info ~/ros2_recordings/recording_20251025_120000
```

## Troubleshooting

### Dashboard shows "Not Responding" dialog
**Fixed in latest version!** The dashboard now:
- Starts immediately without blocking operations
- Initializes network manager in the background after 1 second
- Uses short timeouts (1s) for network checks
- Works fine even if upload server isn't running

If you still experience freezing:
- Check system resources (CPU/memory)
- Reduce number of active ROS2 topics
- Close other heavy applications

### No topics appearing
- Make sure ROS2 is properly sourced
- Check that ROS2 nodes are running and publishing
- Verify ROS2 daemon is running: `ros2 daemon status`

### Recording fails to start
- Ensure output directory has write permissions
- Check that ROS2 bag tools are installed
- Verify no other recording process is running

### Metrics not updating
- Check that recording actually started
- Verify file system is not full
- Ensure bag files are being written to disk

### Network uploads show "Not Initialized"
- This is normal during the first second after startup
- Wait 1 second for network manager to initialize
- If it persists, check that upload server is running

### Upload server connection fails
- Check server is running: `curl http://localhost:8080/health`
- Verify firewall isn't blocking port 8080
- Check server URL in Upload tab settings
- Review server logs for errors

### Uploads stuck in "pending" status
- Check network connectivity
- Verify upload server is accessible
- Look for file permission issues
- Check server has enough disk space

## Performance Tips

### Recording Performance
- Select specific topics instead of recording all topics for better performance
- Monitor disk space to avoid running out during long recordings
- Use SSD storage for better write speeds
- Close unused applications to free system resources

### UI Responsiveness ⭐ NEW
- Dashboard starts immediately (no blocking operations)
- Network manager initializes in background after 1 second
- All ROS2 operations use short timeouts (1-3 seconds)
- Tabs only refresh when active (saves CPU)
- Upload operations run in background threads

### Network Upload Performance
- Adjust chunk size in `network_manager.py` (default: 5MB)
- Use higher priority (7-10) for critical uploads
- Limit concurrent uploads if bandwidth is limited
- Enable compression before upload for large files
- Monitor upload tab for bandwidth usage

## License

This project is provided as-is for ROS2 development and monitoring purposes.

## Contributing

Feel free to submit issues and enhancement requests!

## Future Enhancements

Potential features to add:
- Live data visualization with plots/charts
- Topic remapping support
- Custom QoS profile configuration
- Bag file compression options (already UI ready)
- Split bags by size/duration
- Network streaming support
- Custom message filters and triggers
- Export metrics to CSV/JSON
- Bag comparison and diff tools
- Plugin system for custom widgets
- ROS2 parameter monitoring and tuning
- Action monitoring
- TF tree visualization

## 📸 Screenshots

The dashboard features:
- Clean tabbed interface for easy navigation
- Real-time updates without freezing
- Color-coded status indicators
- Responsive layout that adapts to window size
- Professional dark/light theme support

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is provided as-is for ROS2 development and monitoring purposes.
