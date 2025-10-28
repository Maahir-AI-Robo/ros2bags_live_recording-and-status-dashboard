"""
Smart Recording Triggers - Event-based automated recording control
Supports pre-buffering, conditional starts/stops, and scheduling
"""

import re
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from collections import deque
import json


class RecordingTrigger(QObject):
    """Base class for recording triggers"""
    
    # Signals
    trigger_activated = pyqtSignal(str)  # reason
    trigger_deactivated = pyqtSignal(str)  # reason
    
    def __init__(self, name="Unnamed"):
        super().__init__()
        self.name = name
        self.enabled = True
        self.activated = False
        
    def check(self, ros2_manager, metrics):
        """
        Check if trigger condition is met
        
        Args:
            ros2_manager: ROS2Manager instance
            metrics: Current metrics dictionary
            
        Returns:
            bool: True if trigger should activate
        """
        raise NotImplementedError
        
    def reset(self):
        """Reset trigger state"""
        self.activated = False


class TopicAppearsTrigger(RecordingTrigger):
    """Trigger when specific topic(s) appear"""
    
    def __init__(self, topic_patterns, name="Topic Appears"):
        super().__init__(name)
        self.topic_patterns = topic_patterns if isinstance(topic_patterns, list) else [topic_patterns]
        self.compiled_patterns = [re.compile(p) for p in self.topic_patterns]
        
    def check(self, ros2_manager, metrics):
        """Check if any matching topics exist"""
        if not self.enabled:
            return False
            
        topics = ros2_manager.get_topics_info()
        
        for topic_info in topics:
            topic_name = topic_info['name']
            for pattern in self.compiled_patterns:
                if pattern.match(topic_name):
                    if not self.activated:
                        self.activated = True
                        self.trigger_activated.emit(f"Topic matched: {topic_name}")
                    return True
                    
        return False


class MessageRateTrigger(RecordingTrigger):
    """Trigger when message rate exceeds threshold"""
    
    def __init__(self, threshold_msg_per_sec, name="Message Rate"):
        super().__init__(name)
        self.threshold = threshold_msg_per_sec
        
    def check(self, ros2_manager, metrics):
        """Check if message rate exceeds threshold"""
        if not self.enabled:
            return False
            
        current_rate = metrics.get('message_rate', 0)
        
        if current_rate >= self.threshold:
            if not self.activated:
                self.activated = True
                self.trigger_activated.emit(f"Message rate {current_rate:.1f} >= {self.threshold}")
            return True
        else:
            if self.activated:
                self.activated = False
                self.trigger_deactivated.emit(f"Message rate dropped below {self.threshold}")
            return False


class DiskSpaceTrigger(RecordingTrigger):
    """Trigger stop when disk space is low"""
    
    def __init__(self, threshold_percent=90, name="Low Disk Space"):
        super().__init__(name)
        self.threshold = threshold_percent
        
    def check(self, ros2_manager, metrics):
        """Check if disk usage exceeds threshold (for STOP trigger)"""
        if not self.enabled:
            return False
            
        disk_usage = metrics.get('disk_usage_percent', 0)
        
        if disk_usage >= self.threshold:
            if not self.activated:
                self.activated = True
                self.trigger_activated.emit(f"Disk usage {disk_usage:.1f}% >= {self.threshold}%")
            return True
            
        return False


class DurationTrigger(RecordingTrigger):
    """Trigger stop after specific duration"""
    
    def __init__(self, duration_seconds, name="Duration Limit"):
        super().__init__(name)
        self.duration = duration_seconds
        
    def check(self, ros2_manager, metrics):
        """Check if recording duration exceeds limit"""
        if not self.enabled:
            return False
            
        current_duration = metrics.get('duration', 0)
        
        if current_duration >= self.duration:
            if not self.activated:
                self.activated = True
                self.trigger_activated.emit(f"Duration {current_duration:.1f}s >= {self.duration}s")
            return True
            
        return False


class SizeTrigger(RecordingTrigger):
    """Trigger stop when recording size reaches limit"""
    
    def __init__(self, size_mb, name="Size Limit"):
        super().__init__(name)
        self.size_limit = size_mb
        
    def check(self, ros2_manager, metrics):
        """Check if recording size exceeds limit"""
        if not self.enabled:
            return False
            
        current_size = metrics.get('size_mb', 0)
        
        if current_size >= self.size_limit:
            if not self.activated:
                self.activated = True
                self.trigger_activated.emit(f"Size {current_size:.1f}MB >= {self.size_limit}MB")
            return True
            
        return False


class TopicDisappearsTrigger(RecordingTrigger):
    """Trigger when specific topic disappears"""
    
    def __init__(self, topic_name, grace_period_sec=5, name="Topic Dropout"):
        super().__init__(name)
        self.topic_name = topic_name
        self.grace_period = grace_period_sec
        self.last_seen = None
        
    def check(self, ros2_manager, metrics):
        """Check if topic has disappeared for grace period"""
        if not self.enabled:
            return False
            
        topics = ros2_manager.get_topics_info()
        topic_names = [t['name'] for t in topics]
        
        if self.topic_name in topic_names:
            self.last_seen = datetime.now()
            return False
        else:
            # Topic not found
            if self.last_seen is None:
                self.last_seen = datetime.now()
                
            time_missing = (datetime.now() - self.last_seen).total_seconds()
            
            if time_missing >= self.grace_period:
                if not self.activated:
                    self.activated = True
                    self.trigger_activated.emit(f"Topic {self.topic_name} missing for {time_missing:.1f}s")
                return True
                
        return False


class ScheduledTrigger(RecordingTrigger):
    """Trigger at specific time or recurring schedule"""
    
    def __init__(self, start_time, duration_seconds=None, name="Scheduled"):
        super().__init__(name)
        self.start_time = start_time  # datetime object
        self.duration = duration_seconds
        self.recording_started = None
        
    def check(self, ros2_manager, metrics):
        """Check if current time matches schedule"""
        if not self.enabled:
            return False
            
        now = datetime.now()
        
        # Check if it's time to start
        if now >= self.start_time and self.recording_started is None:
            self.recording_started = now
            if not self.activated:
                self.activated = True
                self.trigger_activated.emit(f"Scheduled time reached: {self.start_time}")
            return True
            
        # Check if it's time to stop (if duration specified)
        if self.duration and self.recording_started:
            elapsed = (now - self.recording_started).total_seconds()
            if elapsed >= self.duration:
                self.trigger_deactivated.emit(f"Scheduled duration {self.duration}s completed")
                return False
                
        return self.recording_started is not None


class SmartRecordingManager(QObject):
    """
    Manages smart recording triggers with pre-buffering
    """
    
    # Signals
    auto_start_requested = pyqtSignal(str)  # reason
    auto_stop_requested = pyqtSignal(str)  # reason
    
    def __init__(self, ros2_manager, metrics_collector):
        super().__init__()
        self.ros2_manager = ros2_manager
        self.metrics_collector = metrics_collector
        
        # Trigger lists
        self.start_triggers = []
        self.stop_triggers = []
        
        # Pre-buffering (stores last N seconds of topic info)
        self.pre_buffer_enabled = False
        self.pre_buffer_duration = 10  # seconds
        self.pre_buffer_data = deque(maxlen=100)  # 100 snapshots
        
        # State
        self.monitoring_enabled = False
        self.recording_active = False
        
        # Setup monitoring timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.check_triggers)
        self.monitor_timer.setInterval(1000)  # Check every second
        
    def add_start_trigger(self, trigger):
        """Add a trigger that starts recording"""
        self.start_triggers.append(trigger)
        trigger.trigger_activated.connect(self.on_start_trigger_activated)
        
    def add_stop_trigger(self, trigger):
        """Add a trigger that stops recording"""
        self.stop_triggers.append(trigger)
        trigger.trigger_activated.connect(self.on_stop_trigger_activated)
        
    def remove_trigger(self, trigger):
        """Remove a trigger"""
        if trigger in self.start_triggers:
            self.start_triggers.remove(trigger)
        if trigger in self.stop_triggers:
            self.stop_triggers.remove(trigger)
            
    def enable_pre_buffering(self, duration_seconds=10):
        """Enable pre-buffering to capture data before trigger"""
        self.pre_buffer_enabled = True
        self.pre_buffer_duration = duration_seconds
        
    def disable_pre_buffering(self):
        """Disable pre-buffering"""
        self.pre_buffer_enabled = False
        self.pre_buffer_data.clear()
        
    def start_monitoring(self):
        """Start monitoring triggers"""
        self.monitoring_enabled = True
        self.monitor_timer.start()
        
    def stop_monitoring(self):
        """Stop monitoring triggers"""
        self.monitoring_enabled = False
        self.monitor_timer.stop()
        
    def check_triggers(self):
        """Check all triggers (called by timer)"""
        if not self.monitoring_enabled:
            return
            
        metrics = self.metrics_collector.get_metrics()
        
        # Update pre-buffer if enabled
        if self.pre_buffer_enabled:
            self.pre_buffer_data.append({
                'timestamp': datetime.now(),
                'topics': self.ros2_manager.get_topics_info(),
                'metrics': metrics.copy()
            })
        
        # Check start triggers if not recording
        if not self.recording_active:
            for trigger in self.start_triggers:
                if trigger.check(self.ros2_manager, metrics):
                    break  # Only activate first matching trigger
                    
        # Check stop triggers if recording
        else:
            for trigger in self.stop_triggers:
                if trigger.check(self.ros2_manager, metrics):
                    break  # Only activate first matching trigger
                    
    def on_start_trigger_activated(self, reason):
        """Handle start trigger activation"""
        if not self.recording_active:
            self.recording_active = True
            self.auto_start_requested.emit(reason)
            
    def on_stop_trigger_activated(self, reason):
        """Handle stop trigger activation"""
        if self.recording_active:
            self.recording_active = False
            self.auto_stop_requested.emit(reason)
            
    def get_pre_buffer_data(self):
        """Get pre-buffered data for playback/saving"""
        return list(self.pre_buffer_data)
        
    def reset_all_triggers(self):
        """Reset all triggers"""
        for trigger in self.start_triggers + self.stop_triggers:
            trigger.reset()
            
    def save_configuration(self, filepath):
        """Save trigger configuration to JSON file"""
        config = {
            'pre_buffer_enabled': self.pre_buffer_enabled,
            'pre_buffer_duration': self.pre_buffer_duration,
            'start_triggers': [self._serialize_trigger(t) for t in self.start_triggers],
            'stop_triggers': [self._serialize_trigger(t) for t in self.stop_triggers]
        }
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
            
    def _serialize_trigger(self, trigger):
        """Serialize trigger to dictionary"""
        return {
            'type': trigger.__class__.__name__,
            'name': trigger.name,
            'enabled': trigger.enabled,
            # Add trigger-specific parameters here
        }
