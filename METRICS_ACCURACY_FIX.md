# Metrics Accuracy Fix - Stats Tab

## Problem Identified
User reported discrepancy between Recording Metrics and Stats tab:

### Recording Metrics Panel (Top Right)
- Duration: 00:03:43 ✅
- Total Size: 1.86 MB ✅
- **Write Speed: 0.50 MB/s** ✅
- Messages: 22,361 ✅
- Active Topics: 5 ✅
- Avg Rate: 100.0 msg/s ✅

### Stats Tab (Bottom)
- CPU Usage: 4.9% ✅
- Memory Usage: 4455 MB / 7719 MB (68.3%) ✅
- **Disk Write Speed: 0.00 MB/s** ❌ **WRONG!**
- Network I/O: ↑ 6.9 KB/s ↓ 9.4 KB/s ✅

## Root Cause

The Stats tab was showing **system-wide disk I/O** from `psutil.disk_io_counters()`, which measures ALL disk activity on the system, not just the ROS2 bag recording.

```python
# OLD CODE - showing system-wide disk writes
disk_io = psutil.disk_io_counters()
write_bytes = disk_io.write_bytes - self.last_disk_io.write_bytes
write_mb_s = write_bytes / (1024 * 1024 * 2)  # Often shows 0 due to OS buffering
```

### Why it showed 0.00 MB/s:
1. **OS Buffering**: Linux buffers disk writes in RAM before flushing to disk
2. **System-wide metric**: Measures all processes, not just our recording
3. **Timing mismatch**: 2-second polling interval may miss small writes
4. **Different metric**: Recording write speed ≠ system disk I/O

The Recording Metrics panel correctly showed **0.50 MB/s** from `metrics_collector.get_metrics()['write_speed_mb_s']`, which tracks the actual bag file size growth.

## Solution

Modified `gui/advanced_stats.py` to show **actual recording write speed** during recording:

```python
# NEW CODE - show recording write speed when recording
if self.metrics_collector and self.ros2_manager.is_recording:
    # During recording: show actual bag write speed from metrics
    metrics = self.metrics_collector.get_metrics()
    write_speed = metrics.get('write_speed_mb_s', 0)
    self.disk_io_value.setText(f"{write_speed:.2f} MB/s")
    self.disk_io_value.setStyleSheet("color: #4CAF50; font-weight: bold;")  # Green when recording
else:
    # When not recording: show system-wide disk writes
    disk_io = psutil.disk_io_counters()
    write_bytes = disk_io.write_bytes - self.last_disk_io.write_bytes
    write_mb_s = write_bytes / (1024 * 1024 * 2)
    self.disk_io_value.setText(f"{write_mb_s:.2f} MB/s")
```

## Changes Made

### File: `gui/advanced_stats.py`

1. **Constructor**: Added `metrics_collector` parameter
   ```python
   def __init__(self, ros2_manager, metrics_collector=None):
       self.metrics_collector = metrics_collector
   ```

2. **refresh_stats()**: Show recording write speed when recording
   - During recording: Display bag write speed from `metrics_collector`
   - When not recording: Display system-wide disk I/O (original behavior)
   - Highlight in green when recording for visibility

### File: `gui/main_window.py`

1. **Pass metrics_collector** to AdvancedStatsWidget
   ```python
   self.advanced_stats = AdvancedStatsWidget(self.ros2_manager, self.metrics_collector)
   ```

## Benefits

### Before (Inaccurate)
- ❌ Stats tab showed 0.00 MB/s during recording
- ❌ Didn't match Recording Metrics panel (0.50 MB/s)
- ❌ Confused users about recording activity
- ❌ System-wide metric not useful during recording

### After (Accurate)
- ✅ Stats tab shows **actual bag write speed** (0.50 MB/s)
- ✅ Matches Recording Metrics panel exactly
- ✅ Green highlight during recording for visibility
- ✅ Clearly indicates recording is active and writing data
- ✅ Falls back to system disk I/O when not recording

## Testing

### How to Verify
1. Start a recording with active topics
2. Wait 3-5 seconds for metrics to accumulate
3. Check both panels:
   - **Recording Metrics panel**: Write Speed: 0.XX MB/s
   - **Stats tab**: Disk Write Speed: 0.XX MB/s (green, same value)
4. Stop recording
5. Stats tab reverts to system-wide disk I/O (non-green)

### Expected Results
- During recording: Both panels show **identical write speed**
- Stats tab value is **green** during recording
- After recording stops: Stats tab shows system disk I/O (may be 0)

## Related Issues Fixed

1. ✅ **Recording health monitoring** - Shows actual activity (bag size, write speed)
2. ✅ **Stats tab accuracy** - Shows recording write speed during recording
3. 🔄 **Live Charts** - Next to debug (empty/zeros issue)

## Commit Details
- **Commit**: `0721c9e`
- **Branch**: `feature/production-optimization-v2`
- **Message**: "Fix Stats tab to show accurate recording write speed"
- **Files Changed**: 2 (gui/advanced_stats.py, gui/main_window.py)
- **Status**: ✅ Committed and pushed to GitHub

---

**Status**: ✅ COMPLETE - Stats tab now shows accurate recording write speed that matches Recording Metrics panel
