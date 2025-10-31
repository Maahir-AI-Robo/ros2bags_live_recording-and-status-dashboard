"""
Dynamic System Detection and Auto-Tuning
Automatically detects hardware specs and adjusts performance parameters
"""

import psutil
import os
import platform
from typing import Dict, Tuple


class SystemDetector:
    """Detects system hardware specs and returns optimal settings"""
    
    @staticmethod
    def get_system_specs() -> Dict[str, any]:
        """Get comprehensive system specifications"""
        try:
            cpu_count = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            virtual_memory = psutil.virtual_memory()
            
            # Detect GPU (basic detection)
            has_gpu = SystemDetector._detect_gpu()
            
            # Detect disk type (SSD vs HDD - affects I/O performance)
            disk_info = SystemDetector._detect_disk_type()
            
            specs = {
                'cpu_cores': cpu_count,
                'cpu_freq_mhz': int(cpu_freq.max) if cpu_freq else 2000,
                'ram_gb': virtual_memory.total / (1024**3),
                'available_ram_gb': virtual_memory.available / (1024**3),
                'has_gpu': has_gpu,
                'disk_type': disk_info['type'],  # 'ssd' or 'hdd'
                'disk_speed': disk_info['speed'],  # 'fast' or 'slow'
                'system_category': SystemDetector._classify_system(cpu_count, virtual_memory.total),
                'platform': platform.system(),
            }
            
            return specs
        except Exception as e:
            # Return defaults if detection fails
            return SystemDetector._get_default_specs()
    
    @staticmethod
    def _detect_gpu() -> bool:
        """Try to detect if GPU is available"""
        try:
            # Check for NVIDIA GPU
            if os.path.exists('/proc/driver/nvidia/version'):
                return True
            
            # Check for AMD GPU
            if os.path.exists('/sys/module/amdgpu'):
                return True
            
            # Try importing GPU libraries
            try:
                import torch
                return torch.cuda.is_available()
            except ImportError:
                pass
            
            return False
        except Exception:
            return False
    
    @staticmethod
    def _detect_disk_type() -> Dict[str, str]:
        """Detect if system uses SSD or HDD"""
        try:
            # Try to detect SSD vs HDD based on device properties
            disk_io = psutil.disk_io_counters()
            if disk_io and disk_io.read_time > 0:
                # Calculate average time per operation
                avg_time = (disk_io.read_time + disk_io.write_time) / (disk_io.read_count + disk_io.write_count + 1)
                
                # SSDs typically have < 5ms latency, HDDs > 10ms
                if avg_time < 5:
                    return {'type': 'ssd', 'speed': 'fast'}
                else:
                    return {'type': 'hdd', 'speed': 'slow'}
            
            return {'type': 'unknown', 'speed': 'medium'}
        except Exception:
            return {'type': 'unknown', 'speed': 'medium'}
    
    @staticmethod
    def _classify_system(cpu_cores: int, ram_bytes: float) -> str:
        """Classify system as low-end, mid-range, or high-end"""
        ram_gb = ram_bytes / (1024**3)
        
        if cpu_cores <= 2 and ram_gb <= 4:
            return 'low-end'
        elif cpu_cores <= 4 and ram_gb <= 8:
            return 'mid-range'
        elif cpu_cores <= 8 and ram_gb <= 16:
            return 'mid-high'
        else:
            return 'high-end'
    
    @staticmethod
    def _get_default_specs() -> Dict[str, any]:
        """Return default specs if detection fails"""
        return {
            'cpu_cores': 4,
            'cpu_freq_mhz': 2000,
            'ram_gb': 8,
            'available_ram_gb': 4,
            'has_gpu': False,
            'disk_type': 'unknown',
            'disk_speed': 'medium',
            'system_category': 'mid-range',
            'platform': platform.system(),
        }


class DynamicPerformanceTuner:
    """Generates performance settings based on system specs"""
    
    @staticmethod
    def get_tuned_settings(specs: Dict[str, any]) -> Dict[str, any]:
        """Generate performance settings based on system specs"""
        category = specs['system_category']
        cpu_cores = specs['cpu_cores']
        ram_gb = specs['ram_gb']
        has_gpu = specs['has_gpu']
        
        if category == 'low-end':
            return DynamicPerformanceTuner._settings_low_end(cpu_cores, ram_gb, has_gpu)
        elif category == 'mid-range':
            return DynamicPerformanceTuner._settings_mid_range(cpu_cores, ram_gb, has_gpu)
        elif category == 'mid-high':
            return DynamicPerformanceTuner._settings_mid_high(cpu_cores, ram_gb, has_gpu)
        else:  # high-end
            return DynamicPerformanceTuner._settings_high_end(cpu_cores, ram_gb, has_gpu)
    
    @staticmethod
    def _settings_low_end(cpu_cores: int, ram_gb: float, has_gpu: bool) -> Dict[str, any]:
        """Settings for low-end systems (2-core, <= 4GB RAM)"""
        return {
            # Chart rendering
            'chart_update_interval': 500,      # 500ms - very conservative
            'plot_skip_threshold': 8,          # Update plots every 8 cycles (4 seconds)
            'stats_update_frequency': 50,      # Every 50 cycles (25 seconds)
            'autoscale_enabled': False,        # Disabled by default
            'autoscale_frequency': 100,        # Very infrequent if enabled
            
            # Metrics collection
            'system_metrics_cache': 3.0,       # 3 seconds - very aggressive caching
            'disk_check_interval': 12.0,       # Every 12 seconds
            'topic_async_interval': 5.0,       # Every 5 seconds
            
            # CPU backoff thresholds
            'cpu_backoff_threshold_high': 75.0,  # Back off at 75%
            'cpu_backoff_threshold_critical': 85.0,  # Skip at 85%
            'cpu_interval_multiplier': 3.0,    # Triple interval when backed off
            
            # Buffer sizes
            'max_buffer_size': 300,            # Smaller buffers (5 minutes at 1Hz)
            'statistics_buffer_size': 100,     # Smaller stats buffer
            
            # Threading
            'max_threads': 1,                  # Single thread only
            'topic_worker_enabled': False,     # No background workers
            
            # Update timers
            'ros2_update_interval': 3000,      # 3 seconds
            'metrics_update_interval': 1500,   # 1.5 seconds
            'history_update_interval': 30000,  # 30 seconds
        }
    
    @staticmethod
    def _settings_mid_range(cpu_cores: int, ram_gb: float, has_gpu: bool) -> Dict[str, any]:
        """Settings for mid-range systems (4-core, 8GB RAM)"""
        return {
            # Chart rendering
            'chart_update_interval': 400,      # 400ms
            'plot_skip_threshold': 5,          # Update plots every 5 cycles (2 seconds)
            'stats_update_frequency': 30,      # Every 30 cycles
            'autoscale_enabled': False,        # Disabled by default
            'autoscale_frequency': 50,         # Infrequent
            
            # Metrics collection
            'system_metrics_cache': 2.0,       # 2 seconds
            'disk_check_interval': 8.0,        # Every 8 seconds
            'topic_async_interval': 3.0,       # Every 3 seconds
            
            # CPU backoff thresholds
            'cpu_backoff_threshold_high': 80.0,
            'cpu_backoff_threshold_critical': 90.0,
            'cpu_interval_multiplier': 2.0,
            
            # Buffer sizes
            'max_buffer_size': 600,            # 10 minutes at 1Hz
            'statistics_buffer_size': 200,
            
            # Threading
            'max_threads': 2,
            'topic_worker_enabled': True,
            
            # Update timers
            'ros2_update_interval': 2000,      # 2 seconds
            'metrics_update_interval': 800,    # 800ms
            'history_update_interval': 20000,  # 20 seconds
        }
    
    @staticmethod
    def _settings_mid_high(cpu_cores: int, ram_gb: float, has_gpu: bool) -> Dict[str, any]:
        """Settings for mid-high systems (8-core, 16GB RAM)"""
        return {
            # Chart rendering
            'chart_update_interval': 300,      # 300ms
            'plot_skip_threshold': 3,          # Update plots every 3 cycles (900ms)
            'stats_update_frequency': 20,      # Every 20 cycles
            'autoscale_enabled': False,        # Disabled by default
            'autoscale_frequency': 30,         # More frequent if enabled
            
            # Metrics collection
            'system_metrics_cache': 1.5,       # 1.5 seconds
            'disk_check_interval': 6.0,        # Every 6 seconds
            'topic_async_interval': 2.0,       # Every 2 seconds
            
            # CPU backoff thresholds
            'cpu_backoff_threshold_high': 80.0,
            'cpu_backoff_threshold_critical': 90.0,
            'cpu_interval_multiplier': 1.5,
            
            # Buffer sizes
            'max_buffer_size': 1200,           # 20 minutes at 1Hz
            'statistics_buffer_size': 400,
            
            # Threading
            'max_threads': 4,
            'topic_worker_enabled': True,
            
            # Update timers
            'ros2_update_interval': 1500,      # 1.5 seconds
            'metrics_update_interval': 500,    # 500ms
            'history_update_interval': 15000,  # 15 seconds
        }
    
    @staticmethod
    def _settings_high_end(cpu_cores: int, ram_gb: float, has_gpu: bool) -> Dict[str, any]:
        """Settings for high-end systems (8+ cores, 16+ GB RAM)"""
        # Increase some parameters based on core count
        extra_threads = max(2, cpu_cores // 4)
        
        return {
            # Chart rendering
            'chart_update_interval': 250,      # 250ms - smoother
            'plot_skip_threshold': 2,          # Update plots every 2 cycles (500ms)
            'stats_update_frequency': 15,      # Every 15 cycles
            'autoscale_enabled': False,        # Still disabled by default
            'autoscale_frequency': 20,         # More frequent if enabled
            
            # Metrics collection
            'system_metrics_cache': 1.0,       # 1 second
            'disk_check_interval': 4.0,        # Every 4 seconds
            'topic_async_interval': 1.5,       # Every 1.5 seconds
            
            # CPU backoff thresholds
            'cpu_backoff_threshold_high': 80.0,
            'cpu_backoff_threshold_critical': 90.0,
            'cpu_interval_multiplier': 1.2,
            
            # Buffer sizes
            'max_buffer_size': 2000,           # 33 minutes at 1Hz (or longer with slower updates)
            'statistics_buffer_size': 600,
            
            # Threading
            'max_threads': extra_threads,
            'topic_worker_enabled': True,
            
            # Update timers
            'ros2_update_interval': 1000,      # 1 second
            'metrics_update_interval': 300,    # 300ms
            'history_update_interval': 10000,  # 10 seconds
        }
    
    @staticmethod
    def merge_with_performance_mode(dynamic_settings: Dict[str, any], 
                                     performance_mode: str) -> Dict[str, any]:
        """Merge dynamic settings with performance mode overrides"""
        # If performance mode is explicitly set, apply mode-specific overrides
        # to the dynamic settings
        
        if performance_mode == 'ULTRA_PERFORMANCE':
            # Make more aggressive even for good systems
            dynamic_settings['plot_skip_threshold'] = max(dynamic_settings['plot_skip_threshold'], 4)
            dynamic_settings['system_metrics_cache'] = max(dynamic_settings['system_metrics_cache'], 2.0)
            dynamic_settings['chart_update_interval'] = min(dynamic_settings['chart_update_interval'], 500)
        
        elif performance_mode == 'BALANCED':
            # Keep defaults from system detection
            pass
        
        elif performance_mode == 'QUALITY':
            # Make less aggressive for better visuals
            dynamic_settings['plot_skip_threshold'] = min(dynamic_settings['plot_skip_threshold'], 2)
            dynamic_settings['chart_update_interval'] = max(dynamic_settings['chart_update_interval'], 200)
            dynamic_settings['autoscale_enabled'] = True
        
        return dynamic_settings


def get_adaptive_settings() -> Dict[str, any]:
    """Main function: Detect system and return optimal settings"""
    specs = SystemDetector.get_system_specs()
    settings = DynamicPerformanceTuner.get_tuned_settings(specs)
    return settings, specs


if __name__ == '__main__':
    # Test the detection
    specs = SystemDetector.get_system_specs()
    settings = DynamicPerformanceTuner.get_tuned_settings(specs)
    
    print("\n" + "="*60)
    print("SYSTEM DETECTION AND AUTO-TUNING")
    print("="*60)
    
    print("\nSystem Specifications:")
    print(f"  CPU Cores: {specs['cpu_cores']}")
    print(f"  CPU Frequency: {specs['cpu_freq_mhz']} MHz")
    print(f"  RAM: {specs['ram_gb']:.1f} GB")
    print(f"  Available RAM: {specs['available_ram_gb']:.1f} GB")
    print(f"  GPU: {'Yes' if specs['has_gpu'] else 'No'}")
    print(f"  Disk Type: {specs['disk_type']}")
    print(f"  System Category: {specs['system_category']}")
    
    print("\nAuto-Tuned Settings:")
    print(f"  Chart Update Interval: {settings['chart_update_interval']}ms")
    print(f"  Plot Skip Threshold: every {settings['plot_skip_threshold']} cycles")
    print(f"  Stats Update Frequency: every {settings['stats_update_frequency']} cycles")
    print(f"  System Metrics Cache: {settings['system_metrics_cache']}s")
    print(f"  Max Buffer Size: {settings['max_buffer_size']} points")
    print(f"  CPU Backoff Threshold: {settings['cpu_backoff_threshold_high']}%")
    print(f"  Max Threads: {settings['max_threads']}")
    print(f"  ROS2 Update Interval: {settings['ros2_update_interval']}ms")
    print(f"  Metrics Update Interval: {settings['metrics_update_interval']}ms")
    print("\n" + "="*60)
