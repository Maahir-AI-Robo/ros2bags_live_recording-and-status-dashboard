# ROS2 Live Recording & Status Dashboard

A powerful, real-time dashboard for ROS2 data recording and system monitoring with live charts, topic monitoring, and intelligent resource optimization.

## 🎯 Features

### 📊 Real-Time Monitoring
- **Live Charts** - Real-time visualization of system metrics (CPU, memory, network)
- **Topic Monitor** - Live Hz monitoring with status tracking (Publishing/Idle indicators)
- **Periodic Updates** - Hz values refresh every 10 seconds during recording
- **Zero Freezing** - All updates happen in background threads (100% responsive UI)

### 🎬 Recording Control
- **Easy Recording** - One-click start/stop for ROS2 bag recording
- **Selective Topics** - Choose which topics to record
- **Auto-Scaling** - Intelligent worker thread scaling based on system resources
- **Batch Processing** - Optimized Hz measurement using thread pools

### 🔐 Authentication
- **Token-Based Auth** - Secure API key management with rate limiting
- **Token Lifecycle** - Automatic expiration and refresh
- **Admin Panel** - Manage authentication settings and API tokens
- **Rate Limiting** - Prevent abuse with configurable rate limits

### 📤 Network Upload
- **Automatic Upload** - Auto-upload recordings to remote server
- **API Integration** - Built-in support for REST API endpoints
- **Authentication** - Secure uploads with API key verification
- **Status Display** - Real-time upload progress and status

### ⚡ Performance Optimization
- **Dynamic Hz Scaling** - Adaptive worker count based on CPU/memory
- **Incremental UI Updates** - Reuses widgets (no recreation overhead)
- **Thread Pooling** - Efficient background task execution
- **Memory-Safe Buffers** - Bounded deques prevent memory leaks

## 📋 Requirements

- **Python**: 3.8+
- **ROS2**: Humble or later
- **PyQt5**: 5.15+
- **System**: Linux with 4GB+ RAM recommended

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/MohammedMaheer/ROSwave.git
cd ROSwave

# Install dependencies
pip install -r requirements.txt

# Install ROS2 (if not already installed)
# Follow: https://docs.ros.org/en/humble/Installation.html
```

### Running the Dashboard

```bash
# Start the dashboard
python3 main.py

# Or use the startup script
bash start_dashboard.sh
```

### First Run

1. **Topics Tab** - Review available ROS2 topics
2. **Check Boxes** - Select topics to record
3. **Output Directory** - Choose where to save bag files
4. **Recording Control** - Click "Record" to start
5. **Live Charts** - Watch real-time metrics
6. **Stop Recording** - Click "Stop" when done

## 📁 Project Structure

```
ROSwave/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── start_dashboard.sh               # Startup script
│
├── gui/
│   ├── main_window.py              # Main application window
│   ├── topic_monitor.py            # Topic discovery and monitoring
│   ├── recording_control.py        # Recording UI and control
│   ├── live_charts.py              # Real-time charting widget
│   ├── network_upload.py           # Network upload widget
│   ├── auth_settings_dialog.py     # Authentication management
│   └── ...                         # Other UI modules
│
├── core/
│   ├── ros2_manager.py             # ROS2 communication layer
│   ├── metrics_collector.py        # System metrics collection
│   ├── async_worker.py             # Async task execution
│   ├── dynamic_hz_scaling.py       # Intelligent Hz scaling
│   ├── auth_manager.py             # Authentication system
│   ├── recording_triggers.py       # Recording conditions
│   ├── health_check.py             # System health monitoring
│   └── ...                         # Other core modules
│
├── config/
│   └── robot_config.json           # Robot configuration
│
├── docs/
│   ├── REALTIME_MONITORING_ENHANCEMENT.md
│   ├── REALTIME_MONITORING_QUICK_START.md
│   ├── ENHANCEMENT_SUMMARY_REALTIME.md
│   └── ...                         # Other documentation
│
└── tests/
    └── test_realtime_monitoring.py # Test suite
```

## 🎮 Usage

### Recording Topics

1. **Open Topic Monitor** tab
2. **Check boxes** next to topics you want to record
3. **Click "Select All"** to record all topics
4. **Set Output Directory** where recordings will be saved
5. **Click "Record"** button to start
6. **Monitor** real-time charts and status
7. **Click "Stop"** when done recording
8. Recordings are saved as `.db3` files

### Monitoring System Health

**Live Charts Tab:**
- 📊 CPU Usage - Real-time CPU percentage
- 💾 Memory Usage - RAM utilization
- 📡 Network Activity - Network I/O stats
- 🔥 System Load - 1-min, 5-min, 15-min averages

**Topic Monitor Tab:**
- ✅ Publishing - Topics actively publishing (green)
- ⏸️ Idle - Topics with no publishers (orange)
- 📈 Hz Values - Publishing rate updates every 10 seconds during recording
- 🔢 Publisher Count - Number of active publishers per topic

### Uploading Recordings

1. **Click "Network Upload"** tab
2. **Enter API Endpoint** (if needed)
3. **Enter API Key** for authentication
4. **Select Bag File** to upload
5. **Click "Upload"** to start
6. Monitor upload progress

## ⚙️ Configuration

### Recording Settings

Edit `config/robot_config.json`:

```json
{
  "robot_name": "robot_maahir",
  "output_directory": "/path/to/recordings",
  "auto_upload": false,
  "api_endpoint": "https://api.example.com/upload"
}
```

### Performance Tuning

The dashboard automatically optimizes based on system resources:

- **CPU-bound systems** - Reduces worker threads
- **Memory-constrained systems** - Smaller buffers
- **High-load systems** - Intelligent batching

Manual tuning available in `dynamic_hz_scaling.py`

## 📊 Real-Time Monitoring Details

### Hz Refresh Mechanism

During recording:
- **Every 10 seconds**: Hz values are measured from active topics
- **Background Thread**: Measurements don't block UI
- **Incremental Updates**: Only changed cells are repainted
- **Automatic Control**: Starts when recording begins, stops when recording ends

### Status Indicators

| Status | Color | Meaning |
|--------|-------|---------|
| Publishing | 🟢 Green | Topic has active publishers |
| Idle | 🟠 Orange | No active publishers |

### Performance Characteristics

- **UI Responsiveness**: 100% maintained during recording
- **CPU Overhead**: < 1% during Hz measurement
- **Memory Footprint**: < 100MB typical
- **Latency**: < 50ms for UI updates

## 🔐 Authentication & Security

### Setting Up Authentication

1. **Open Settings** → **Authentication...**
2. **Generate API Token** with admin key
3. **Copy Token** for API usage
4. **Set Expiration** (default: 7 days)
5. **Manage Tokens** in admin panel

### Token Features

- ✅ Automatic expiration after set duration
- ✅ Rate limiting (default: 100 requests/hour)
- ✅ Token revocation support
- ✅ Usage tracking and logging
- ✅ Admin-only token management

## 🧪 Testing

### Run Tests

```bash
# Run real-time monitoring tests
python3 test_realtime_monitoring.py

# Run specific test
python3 -m pytest tests/test_realtime_monitoring.py -v
```

### Test Coverage

- ✅ Topic loading and discovery
- ✅ Recording state transitions
- ✅ Hz refresh timer control
- ✅ Status column updates
- ✅ Background thread operations
- ✅ UI responsiveness

## 📚 Documentation

### Quick Start Guides

- [`REALTIME_MONITORING_QUICK_START.md`](docs/REALTIME_MONITORING_QUICK_START.md) - User guide for real-time monitoring
- [`REALTIME_MONITORING_ENHANCEMENT.md`](docs/REALTIME_MONITORING_ENHANCEMENT.md) - Technical details
- [`ENHANCEMENT_SUMMARY_REALTIME.md`](docs/ENHANCEMENT_SUMMARY_REALTIME.md) - Complete summary

### Additional Resources

- ROS2 Documentation: https://docs.ros.org/
- PyQt5 Guide: https://riverbankcomputing.com/software/pyqt/
- Bag File Format: https://github.com/ros2/rosbag2

## 🐛 Troubleshooting

### Dashboard Won't Start

```bash
# Check Python version
python3 --version

# Check dependencies
pip list | grep -E "PyQt5|rclpy"

# Check ROS2 setup
source /opt/ros/humble/setup.bash
echo $ROS_DOMAIN_ID
```

### No Topics Appearing

```bash
# Verify ROS2 is running
ros2 topic list

# Check network configuration
ros2 node list

# Verify domain ID matches
echo $ROS_DOMAIN_ID
```

### Recording Not Starting

```bash
# Check write permissions
ls -la /path/to/output/directory

# Check disk space
df -h /path/to/output/directory

# Verify ROS2 bag record is available
which ros2_bag_record
```

### Hz Values Not Updating

- Wait 10+ seconds (refresh interval)
- Ensure topics have active publishers
- Check "Status" column (should show "Publishing" for active topics)
- Verify recording is actually running

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👨‍💻 Author

**Maahir** - Robot Developer & ROS2 Enthusiast

- GitHub: [@MohammedMaheer](https://github.com/MohammedMaheer)
- Email: Contact via GitHub

## 🙏 Acknowledgments

- ROS2 Community for excellent documentation
- PyQt5 developers for the powerful GUI framework
- All contributors and testers

## 📞 Support

For issues, questions, or suggestions:

1. Check existing [Issues](https://github.com/MohammedMaheer/ROSwave/issues)
2. Search [Documentation](docs/)
3. Create a new issue with:
   - Detailed description
   - Steps to reproduce
   - System information
   - Screenshots/logs if applicable

## 🔄 Version History

### v1.0.0 (Current)
- ✅ Real-time topic monitoring with live Hz updates
- ✅ Live status tracking (Publishing/Idle)
- ✅ Automatic monitoring control
- ✅ Background thread-based updates
- ✅ Full integration with RecordingControl signals
- ✅ Zero performance degradation
- ✅ Comprehensive documentation and tests

### Features Added in Latest Release

**Real-Time Monitoring Enhancement:**
- Periodic Hz refresh (10 seconds during recording)
- Live status column with color coding
- Automatic recording state tracking
- Non-blocking background thread updates
- Full signal integration for automatic control

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Start Dashboard | `python3 main.py` |
| Run Tests | `python3 test_realtime_monitoring.py` |
| View Topics | `ros2 topic list` |
| Record Bag | Click "Record" in UI |
| Upload Recording | Use "Network Upload" tab |
| Check Status | Monitor "Live Charts" tab |
| Manage Auth | Settings → Authentication |

---

**Ready to start recording? Just run `python3 main.py` and select your topics!** 🚀
