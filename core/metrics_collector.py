"""
Metrics Collector - collects and calculates recording metrics
OPTIMIZED: Adaptive caching with threading safety
"""

import os
import time
import psutil
from typing import Dict, Union, Optional
import threading


class MetricsCollector:
    """Collects metrics during bag recording with OPTIMIZED adaptive performance"""
    
    def __init__(self):
        self.start_time: Optional[float] = None
        self.last_update_time: Optional[float] = None
        self.last_size: float = 0.0
        self.last_disk_io = None
        
        # Adaptive caching for performance
        self.system_metrics_cache_timeout = 1.0  # Will be updated by performance mode
        self._system_metrics_cache = None
        self._system_metrics_cache_time = 0
        
        # Thread safety
        self._lock = threading.Lock()
        
        self.metrics: Dict[str, Union[int, float]] = {
            'duration': 0.0,
            'size_mb': 0.0,
            'write_speed_mb_s': 0.0,
            'message_count': 0,
            'topic_count': 0,
            'message_rate': 0.0,
            'disk_usage_percent': 0.0,
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'disk_write_speed': 0.0
        }
        
    def reset(self):
        """Reset metrics for new recording"""
        with self._lock:
            self.start_time = time.time()
            self.last_update_time = self.start_time
            self.last_size = 0.0
            self.last_disk_io = None
            self.metrics = {
                'duration': 0.0,
                'size_mb': 0.0,
                'write_speed_mb_s': 0.0,
                'message_count': 0,
                'topic_count': 0,
                'message_rate': 0.0,
                'disk_usage_percent': 0.0,
                'cpu_percent': 0.0,
                'memory_percent': 0.0,
                'disk_write_speed': 0.0
            }
        
    def update(self, ros2_manager):
        """Update metrics based on current recording - OPTIMIZED with thread safety"""
        current_time = time.time()
        
        with self._lock:
            # Update duration
            if self.start_time:
                self.metrics['duration'] = current_time - self.start_time
                
            # Get current bag path
            bag_path = ros2_manager.get_current_bag_path()
            
            if bag_path and os.path.exists(bag_path):
                # Calculate current size
                current_size = 0
                try:
                    for dirpath, dirnames, filenames in os.walk(bag_path):
                        for filename in filenames:
                            filepath = os.path.join(dirpath, filename)
                            try:
                                current_size += os.path.getsize(filepath)
                            except:
                                pass
                except:
                    pass
                        
                current_size_mb = current_size / (1024 * 1024)
                self.metrics['size_mb'] = current_size_mb
                
                # Calculate write speed
                if self.last_update_time and self.last_update_time != self.start_time:
                    time_delta = current_time - self.last_update_time
                    if time_delta > 0:
                        size_delta_mb = current_size_mb - self.last_size
                        self.metrics['write_speed_mb_s'] = size_delta_mb / time_delta
                        
                self.last_size = current_size_mb
                self.last_update_time = current_time
                
                # Get topic count from currently active topics
                try:
                    topics = ros2_manager.get_topics_info()
                    self.metrics['topic_count'] = len(topics)
                except:
                    # Fallback to bag info (will be 0 during recording)
                    try:
                        bag_info = ros2_manager.get_bag_info(bag_path)
                        self.metrics['topic_count'] = bag_info.get('topic_count', 0)
                    except:
                        pass
                
                # Estimate message count (simplified - could be improved)
                avg_msg_size_kb = 1  # Assume 1KB per message on average
                self.metrics['message_count'] = int(current_size_mb * 1024 / avg_msg_size_kb)
                
                # Calculate message rate
                if self.metrics['duration'] > 0:
                    self.metrics['message_rate'] = self.metrics['message_count'] / self.metrics['duration']
                    
            # Get disk usage
            try:
                self.metrics['disk_usage_percent'] = ros2_manager.get_disk_usage()
            except:
                pass
        
        # Get system metrics (CPU, Memory, Disk I/O) - can run outside lock
        self.update_system_metrics()
        
    def update_system_metrics(self):
        """Update system performance metrics (ADAPTIVE caching based on performance mode)"""
        current_time = time.time()
        
        # Use cached values if still fresh
        if (self._system_metrics_cache is not None and 
            current_time - self._system_metrics_cache_time < self.system_metrics_cache_timeout):
            # Use cached values (no lock needed for read)
            with self._lock:
                self.metrics.update(self._system_metrics_cache)
            return
        
        # CPU usage (non-blocking with interval=0)
        try:
            cpu_percent = psutil.cpu_percent(interval=0)
        except:
            cpu_percent = 0.0
        
        # Memory usage
        try:
            mem = psutil.virtual_memory()
            memory_percent = mem.percent
        except:
            memory_percent = 0.0
        
        # Disk I/O speed - adaptive check based on cache timeout
        disk_write_speed = 0.0
        if not hasattr(self, '_last_disk_check'):
            self._last_disk_check = 0
            
        # Check disk I/O at 2x the system metrics cache timeout
        if current_time - self._last_disk_check > (self.system_metrics_cache_timeout * 2):
            try:
                disk_io = psutil.disk_io_counters()
                if disk_io and self.last_disk_io and self.last_update_time:
                    write_bytes_delta = disk_io.write_bytes - self.last_disk_io.write_bytes
                    time_delta = current_time - self.last_update_time
                    if time_delta > 0:
                        disk_write_speed = (write_bytes_delta / time_delta) / (1024 * 1024)  # MB/s
                
                self.last_disk_io = disk_io
                self._last_disk_check = current_time
            except:
                disk_write_speed = 0.0
        else:
            # Use last known value
            with self._lock:
                disk_write_speed = self.metrics.get('disk_write_speed', 0.0)
        
        # Update metrics with lock
        with self._lock:
            self.metrics['cpu_percent'] = cpu_percent
            self.metrics['memory_percent'] = memory_percent
            self.metrics['disk_write_speed'] = disk_write_speed
        
        # Cache the system metrics
        self._system_metrics_cache = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'disk_write_speed': disk_write_speed
        }
        self._system_metrics_cache_time = current_time
    
    def get_metrics(self) -> Dict[str, Union[int, float]]:
        """Get current metrics - thread-safe"""
        # Always update system metrics when requested
        self.update_system_metrics()
        
        with self._lock:
            return self.metrics.copy()
    
    def get_live_metrics(self, ros2_manager=None):
        """Get live metrics including system stats (lightweight topic checks)"""
        # Update system metrics (cached)
        self.update_system_metrics()
        
        # Check topic count occasionally (every 3 seconds) for Live Charts
        if ros2_manager:
            if not hasattr(self, '_last_topic_check'):
                self._last_topic_check = 0
            
            time_since_check = time.time() - self._last_topic_check
            if time_since_check > 3.0:  # Every 3 seconds
                try:
                    topics = ros2_manager.get_topics_info()
                    with self._lock:
                        self.metrics['topic_count'] = len(topics)
                    self._last_topic_check = time.time()
                except:
                    pass
        elif ros2_manager and not hasattr(self, '_last_topic_check'):
            self._last_topic_check = 0  # Initialize
        
        with self._lock:
            return self.metrics.copy()
