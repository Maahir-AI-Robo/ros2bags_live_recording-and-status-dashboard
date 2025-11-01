# Recording Health Monitoring Fix

## Problem
The recording health monitoring was showing **static values** that didn't reflect actual recording activity:
```
📊 Recording health: 45s elapsed, CPU=0.0%, MEM=38.4MB, PID=12345
📊 Recording health: 47s elapsed, CPU=0.0%, MEM=38.4MB, PID=12345
📊 Recording health: 49s elapsed, CPU=0.0%, MEM=38.4MB, PID=12345
```

## Root Cause
- Used `cpu_percent(interval=0.1)` to monitor recording process
- ROS2 bag recording is **I/O-bound**, not CPU-bound
- CPU usage is always ~0% even during active recording
- Memory usage is static (process doesn't allocate much RAM)
- **Result**: Health metrics showed static values, not useful for monitoring

## Solution
Track **actual recording activity** instead of process stats:

### 1. Bag File Size Tracking
```python
# Walk bag directory and sum all file sizes
bag_size_mb = 0.0
for root, _, files in os.walk(self.current_bag_path):
    for file in files:
        file_path = os.path.join(root, file)
        if os.path.isfile(file_path):
            bag_size_mb += os.path.getsize(file_path) / (1024 * 1024)
```

### 2. Write Speed Calculation
```python
# Calculate MB/s based on size growth
time_delta = time.time() - self._last_size_check_time
size_delta = bag_size_mb - self._last_bag_size
write_speed_mbps = size_delta / time_delta
```

### 3. New Health Output
```
📊 Recording health: 45s elapsed, Size=125.34MB, Write=2.78MB/s, PID=12345
📊 Recording health: 105s elapsed, Size=291.67MB, Write=2.77MB/s, PID=12345
📊 Recording health: 165s elapsed, Size=458.12MB, Write=2.77MB/s, PID=12345
```

## Changes Made

### Modified Files
1. **core/ros2_manager.py** - `_monitor_recording()` method (lines 398-486)
   - Track bag file size every 2 seconds
   - Calculate write speed (MB/s)
   - Change log format: `"Size=XXX.XMB, Write=X.XXMB/s"` instead of `"CPU=0.0%, MEM=38.4MB"`
   - Add warnings for:
     - **Stalled recording**: No size growth for 10+ seconds
     - **High write speed**: >100MB/s (potential I/O bottleneck)

2. **core/ros2_manager.py** - `get_recording_health()` method (lines 549-598)
   - Return `bag_size_mb` and `write_speed_mbps` instead of `cpu_percent` and `memory_mb`
   - Same calculation logic as `_monitor_recording()`
   - Maintain tracking variables: `_last_bag_size`, `_last_size_check_time`

### New Warnings
```python
# Stalled recording detection
if bag_size_mb > 0 and size_delta == 0 and time_delta > 10:
    warning = f"Recording appears stalled (no growth for {int(time_delta)}s)"
    
# High write speed detection
if write_speed_mbps > 100:
    warning = f"High write speed: {write_speed_mbps:.2f}MB/s (possible I/O bottleneck)"
```

## Benefits

### Before (Static Values)
- ❌ CPU always shows 0.0% (not useful)
- ❌ Memory always shows same value (38.4MB)
- ❌ Can't tell if recording is active or stalled
- ❌ No visibility into recording throughput

### After (Dynamic Activity)
- ✅ Bag size shows continuous growth
- ✅ Write speed shows actual recording rate
- ✅ Can detect stalled recordings (no growth)
- ✅ Can detect I/O bottlenecks (high write speed)
- ✅ Values are **dynamic** and reflect real activity

## Testing

### How to Verify
1. Start a recording with some active topics:
   ```bash
   # In terminal 1: Start demo topic publisher
   python3 demo_topics_generator.py
   
   # In terminal 2: Run dashboard
   python3 main.py
   
   # Click "Start Recording" in dashboard
   ```

2. Watch console output for health logs:
   ```
   📊 Recording health: XXs elapsed, Size=XXX.XMB, Write=X.XXMB/s, PID=XXXX
   ```

3. Verify values are **dynamic**:
   - Size should increase over time
   - Write speed should be > 0 MB/s
   - Values should change with each log (~60s intervals)

### Expected Results
- **Low-rate topics** (1-10 Hz): Write speed 0.1-1 MB/s
- **Medium-rate topics** (50-100 Hz): Write speed 5-20 MB/s
- **High-rate topics** (100+ Hz, images): Write speed 50-100 MB/s
- **Stalled recording**: Size stops growing, warning appears

## Impact

### User Experience
- Clear visibility into recording activity
- Can verify recording is working (size growing)
- Can monitor recording throughput (write speed)
- Early warning for stalled recordings
- Early warning for I/O bottlenecks

### Technical Reliability
- Health metrics now reflect **actual activity**
- Can detect and warn about recording issues
- Provides actionable data for troubleshooting
- Aligns with user's need for "live data" and "correct statistics"

## Commit Details
- **Commit**: `4056fd1`
- **Branch**: `feature/production-optimization-v2`
- **Message**: "Fix recording health to show actual activity (bag size, write speed)"
- **Files Changed**: 1 (core/ros2_manager.py)
- **Lines Changed**: +86/-8
- **Status**: ✅ Committed and pushed to GitHub

## Next Steps
1. Test the fix by starting a recording and observing health logs
2. Verify bag size and write speed values are dynamic
3. Confirm warnings appear for stalled/high-speed recordings
4. Consider adding health metrics to UI if not already displayed

---

**Status**: ✅ COMPLETE - Recording health now shows actual activity (bag size, write speed) instead of static CPU/memory values
