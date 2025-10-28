"""
Adaptive Performance Modes for ROS2 Dashboard
Automatically adjusts settings based on system specifications
"""

import psutil
import platform
from enum import Enum
from typing import Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal  # type: ignore


class PerformanceMode(Enum):
    """Performance mode levels"""
    HIGH = "high"           # High-end systems (16GB+ RAM, 8+ cores)
    BALANCED = "balanced"   # Mid-range systems (8-16GB RAM, 4-8 cores)
    LOW = "low"            # Low-end systems (<8GB RAM, <4 cores)
    CUSTOM = "custom"      # User-defined settings


class PerformanceModeManager(QObject):
    """Manages adaptive performance modes based on system specs"""
    
    mode_changed = pyqtSignal(str)  # Emits new mode name
    
    def __init__(self):
        super().__init__()
        self._current_mode = None
        self._custom_settings = None
        
        # Detect system specs
        self.system_info = self._detect_system_specs()
        
        # Auto-detect optimal mode
        self._current_mode = self._auto_detect_mode()
        
    def _detect_system_specs(self) -> Dict[str, Any]:
        """Detect system hardware specifications"""
        try:
            memory_gb = psutil.virtual_memory().total / (1024 ** 3)
            cpu_count = psutil.cpu_count(logical=False) or psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            cpu_freq_mhz = cpu_freq.max if cpu_freq else 0
            
            # Get disk info
            disk = psutil.disk_usage('/')
            disk_total_gb = disk.total / (1024 ** 3)
            
            # Check if SSD (heuristic: very fast disk)
            try:
                disk_io_start = psutil.disk_io_counters()
                import time
                time.sleep(0.1)
                disk_io_end = psutil.disk_io_counters()
                read_speed = (disk_io_end.read_bytes - disk_io_start.read_bytes) / 0.1
                is_ssd = read_speed > 100 * 1024 * 1024  # >100MB/s suggests SSD
            except:
                is_ssd = False
            
            return {
                'memory_gb': round(memory_gb, 1),
                'cpu_count': cpu_count,
                'cpu_freq_mhz': round(cpu_freq_mhz, 0),
                'disk_gb': round(disk_total_gb, 1),
                'is_ssd': is_ssd,
                'platform': platform.system(),
                'architecture': platform.machine()
            }
        except Exception as e:
            print(f"Error detecting system specs: {e}")
            return {
                'memory_gb': 8.0,
                'cpu_count': 4,
                'cpu_freq_mhz': 2000,
                'disk_gb': 256,
                'is_ssd': False,
                'platform': 'Unknown',
                'architecture': 'Unknown'
            }
    
    def _auto_detect_mode(self) -> PerformanceMode:
        """Auto-detect optimal performance mode based on specs"""
        memory_gb = self.system_info['memory_gb']
        cpu_count = self.system_info['cpu_count']
        
        # High-end: 16GB+ RAM AND 8+ cores
        if memory_gb >= 16 and cpu_count >= 8:
            return PerformanceMode.HIGH
        
        # Low-end: <8GB RAM OR <4 cores
        elif memory_gb < 8 or cpu_count < 4:
            return PerformanceMode.LOW
        
        # Balanced: Everything else (8-16GB RAM, 4-8 cores)
        else:
            return PerformanceMode.BALANCED
    
    def get_mode_settings(self, mode: PerformanceMode = None) -> Dict[str, Any]:
        """Get settings for specified mode (or current mode)"""
        if mode is None:
            mode = self._current_mode
        
        if mode == PerformanceMode.CUSTOM and self._custom_settings:
            return self._custom_settings
        
        # HIGH PERFORMANCE MODE (16GB+ RAM, 8+ cores)
        if mode == PerformanceMode.HIGH:
            return {
                # Timer intervals (ms)
                'ros2_update_interval': 1000,      # 1 second - very responsive
                'metrics_update_interval': 250,    # 250ms - ultra responsive during recording
                'history_update_interval': 5000,   # 5 seconds - frequent history updates
                'chart_update_interval': 500,      # 500ms - smooth real-time charts
                
                # Thread pool settings
                'max_threads': 6,                  # More parallel operations
                'max_concurrent_threads': 4,       # Allow 4 concurrent operations
                
                # Cache settings (seconds)
                'cache_timeout': 1,                # 1 second - fresh data
                'system_metrics_cache': 0.5,       # 500ms - very fresh system metrics
                'topic_check_interval': 1,         # 1 second - frequent topic checks
                
                # Chart settings
                'chart_buffer_size': 120,          # 2 minutes of data at 1s intervals
                'chart_auto_pause': False,         # Don't auto-pause (plenty of resources)
                
                # Memory settings
                'history_max_entries': 1000,       # Large history
                'enable_profiler': True,           # Enable performance profiler
                'enable_advanced_features': True,  # All features enabled
                
                # UI settings
                'lazy_load_widgets': False,        # Load everything upfront
                'process_priority': 'normal',      # Normal priority
            }
        
        # BALANCED MODE (8-16GB RAM, 4-8 cores) - Current optimized settings
        elif mode == PerformanceMode.BALANCED:
            return {
                # Timer intervals (ms)
                'ros2_update_interval': 3000,      # 3 seconds - moderate
                'metrics_update_interval': 500,    # 500ms - still responsive during recording
                'history_update_interval': 15000,  # 15 seconds - moderate history updates
                'chart_update_interval': 1000,     # 1 second - good real-time feel
                
                # Thread pool settings
                'max_threads': 3,                  # Moderate parallelism
                'max_concurrent_threads': 2,       # Allow 2 concurrent operations
                
                # Cache settings (seconds)
                'cache_timeout': 3,                # 3 seconds - balanced freshness
                'system_metrics_cache': 1,         # 1 second - balanced system metrics
                'topic_check_interval': 3,         # 3 seconds - moderate topic checks
                
                # Chart settings
                'chart_buffer_size': 60,           # 1 minute of data
                'chart_auto_pause': True,          # Auto-pause when hidden (save resources)
                
                # Memory settings
                'history_max_entries': 500,        # Moderate history
                'enable_profiler': True,           # Enable performance profiler
                'enable_advanced_features': True,  # All features enabled
                
                # UI settings
                'lazy_load_widgets': True,         # Lazy load heavy widgets
                'process_priority': 'normal',      # Normal priority
            }
        
        # LOW PERFORMANCE MODE (<8GB RAM, <4 cores)
        else:  # PerformanceMode.LOW
            return {
                # Timer intervals (ms)
                'ros2_update_interval': 5000,      # 5 seconds - reduce load
                'metrics_update_interval': 1000,   # 1 second - still usable during recording
                'history_update_interval': 30000,  # 30 seconds - minimal history updates
                'chart_update_interval': 2000,     # 2 seconds - acceptable real-time
                
                # Thread pool settings
                'max_threads': 2,                  # Minimal threads
                'max_concurrent_threads': 1,       # Only 1 operation at a time
                
                # Cache settings (seconds)
                'cache_timeout': 5,                # 5 seconds - aggressive caching
                'system_metrics_cache': 2,         # 2 seconds - reduce system calls
                'topic_check_interval': 5,         # 5 seconds - minimal topic checks
                
                # Chart settings
                'chart_buffer_size': 30,           # 30 seconds of data
                'chart_auto_pause': True,          # Auto-pause when hidden (critical for low-end)
                
                # Memory settings
                'history_max_entries': 200,        # Minimal history
                'enable_profiler': False,          # Disable profiler (saves resources)
                'enable_advanced_features': True,  # Keep features but optimize
                
                # UI settings
                'lazy_load_widgets': True,         # Lazy load everything possible
                'process_priority': 'below_normal', # Lower priority to not interfere with ROS2
            }
    
    def set_mode(self, mode: PerformanceMode):
        """Set performance mode"""
        if mode != self._current_mode:
            self._current_mode = mode
            self.mode_changed.emit(mode.value)
    
    def set_custom_settings(self, settings: Dict[str, Any]):
        """Set custom performance settings"""
        self._custom_settings = settings
        self._current_mode = PerformanceMode.CUSTOM
        self.mode_changed.emit('custom')
    
    def get_current_mode(self) -> PerformanceMode:
        """Get current performance mode"""
        return self._current_mode
    
    def get_mode_description(self, mode: PerformanceMode = None) -> str:
        """Get human-readable description of mode"""
        if mode is None:
            mode = self._current_mode
        
        descriptions = {
            PerformanceMode.HIGH: (
                "High Performance Mode\n"
                f"Optimized for: 16GB+ RAM, 8+ CPU cores\n"
                f"Your system: {self.system_info['memory_gb']}GB RAM, "
                f"{self.system_info['cpu_count']} cores\n"
                "Features: Ultra-responsive updates, all features enabled, "
                "maximum parallelism"
            ),
            PerformanceMode.BALANCED: (
                "Balanced Mode\n"
                f"Optimized for: 8-16GB RAM, 4-8 CPU cores\n"
                f"Your system: {self.system_info['memory_gb']}GB RAM, "
                f"{self.system_info['cpu_count']} cores\n"
                "Features: Good responsiveness, smart caching, "
                "all features enabled"
            ),
            PerformanceMode.LOW: (
                "Low Performance Mode\n"
                f"Optimized for: <8GB RAM, <4 CPU cores\n"
                f"Your system: {self.system_info['memory_gb']}GB RAM, "
                f"{self.system_info['cpu_count']} cores\n"
                "Features: Resource-efficient, aggressive caching, "
                "features optimized for performance"
            ),
            PerformanceMode.CUSTOM: (
                "Custom Mode\n"
                "User-defined performance settings"
            )
        }
        
        return descriptions.get(mode, "Unknown mode")
    
    def get_system_info_text(self) -> str:
        """Get formatted system information text"""
        info = self.system_info
        return (
            f"System Information:\n"
            f"  Memory: {info['memory_gb']} GB\n"
            f"  CPU Cores: {info['cpu_count']}\n"
            f"  CPU Frequency: {info['cpu_freq_mhz']} MHz\n"
            f"  Disk: {info['disk_gb']} GB ({'SSD' if info['is_ssd'] else 'HDD'})\n"
            f"  Platform: {info['platform']} ({info['architecture']})\n"
            f"\n"
            f"Auto-Detected Mode: {self._current_mode.value.upper()}"
        )
    
    def should_use_feature(self, feature_name: str) -> bool:
        """Check if a feature should be enabled in current mode"""
        settings = self.get_mode_settings()
        
        # Features that can be disabled in low-end mode
        low_end_optional_features = {
            'performance_profiler': settings.get('enable_profiler', True),
            'live_charts': True,  # Always enabled but auto-paused
            'recording_triggers': settings.get('enable_advanced_features', True),
            'export_functionality': True,  # Always available
        }
        
        return low_end_optional_features.get(feature_name, True)
