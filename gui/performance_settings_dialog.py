"""
Performance Settings Dialog
Allows users to view and change performance modes
"""

from PyQt5.QtWidgets import (  # type: ignore
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QRadioButton, QGroupBox, QPushButton, QTextEdit,
    QSpinBox, QCheckBox, QFormLayout, QTabWidget, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal  # type: ignore
from core.performance_modes import PerformanceMode, PerformanceModeManager  # type: ignore


class PerformanceSettingsDialog(QDialog):
    """Dialog for managing performance settings"""
    
    mode_changed = pyqtSignal(PerformanceMode)
    
    def __init__(self, performance_manager: PerformanceModeManager, parent=None):
        super().__init__(parent)
        self.performance_manager = performance_manager
        self.setWindowTitle("Performance Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self.setup_ui()
        self.load_current_settings()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Create tabs
        tabs = QTabWidget()
        
        # Tab 1: Performance Modes
        mode_tab = QWidget()
        mode_layout = QVBoxLayout(mode_tab)
        
        # System info
        info_group = QGroupBox("System Information")
        info_layout = QVBoxLayout()
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        self.info_text.setPlainText(self.performance_manager.get_system_info_text())
        info_layout.addWidget(self.info_text)
        info_group.setLayout(info_layout)
        mode_layout.addWidget(info_group)
        
        # Performance modes
        modes_group = QGroupBox("Performance Mode")
        modes_layout = QVBoxLayout()
        
        self.mode_radios = {}
        
        # High performance
        self.mode_radios[PerformanceMode.HIGH] = QRadioButton("High Performance")
        high_desc = QLabel("  Ultra-responsive (16GB+ RAM, 8+ cores)\n"
                          "  • 1s ROS2 updates\n"
                          "  • 250ms metrics updates\n"
                          "  • 500ms chart updates\n"
                          "  • 6 threads, 4 concurrent operations")
        high_desc.setStyleSheet("color: #666; font-size: 10px; margin-left: 20px;")
        modes_layout.addWidget(self.mode_radios[PerformanceMode.HIGH])
        modes_layout.addWidget(high_desc)
        
        # Balanced
        self.mode_radios[PerformanceMode.BALANCED] = QRadioButton("Balanced")
        balanced_desc = QLabel("  Recommended for most systems (8-16GB RAM, 4-8 cores)\n"
                              "  • 3s ROS2 updates\n"
                              "  • 500ms metrics updates\n"
                              "  • 1s chart updates\n"
                              "  • 3 threads, 2 concurrent operations")
        balanced_desc.setStyleSheet("color: #666; font-size: 10px; margin-left: 20px;")
        modes_layout.addWidget(self.mode_radios[PerformanceMode.BALANCED])
        modes_layout.addWidget(balanced_desc)
        
        # Low performance
        self.mode_radios[PerformanceMode.LOW] = QRadioButton("Low Performance")
        low_desc = QLabel("  Resource-efficient (<8GB RAM, <4 cores)\n"
                         "  • 5s ROS2 updates\n"
                         "  • 1s metrics updates\n"
                         "  • 2s chart updates\n"
                         "  • 2 threads, 1 concurrent operation")
        low_desc.setStyleSheet("color: #666; font-size: 10px; margin-left: 20px;")
        modes_layout.addWidget(self.mode_radios[PerformanceMode.LOW])
        modes_layout.addWidget(low_desc)
        
        # Custom (future feature)
        self.mode_radios[PerformanceMode.CUSTOM] = QRadioButton("Custom")
        self.mode_radios[PerformanceMode.CUSTOM].setEnabled(False)
        custom_desc = QLabel("  User-defined settings (coming soon)")
        custom_desc.setStyleSheet("color: #999; font-size: 10px; margin-left: 20px;")
        modes_layout.addWidget(self.mode_radios[PerformanceMode.CUSTOM])
        modes_layout.addWidget(custom_desc)
        
        modes_group.setLayout(modes_layout)
        mode_layout.addWidget(modes_group)
        
        # Auto-detect button
        auto_detect_btn = QPushButton("🔍 Auto-Detect Optimal Mode")
        auto_detect_btn.clicked.connect(self.auto_detect_mode)
        mode_layout.addWidget(auto_detect_btn)
        
        mode_layout.addStretch()
        tabs.addTab(mode_tab, "Performance Modes")
        
        # Tab 2: Advanced Settings
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        
        advanced_info = QLabel(
            "Advanced settings for fine-tuning performance.\n"
            "Note: Changing these requires application restart."
        )
        advanced_info.setStyleSheet("color: #666; font-style: italic;")
        advanced_layout.addWidget(advanced_info)
        
        # Current mode settings display
        settings_group = QGroupBox("Current Mode Settings")
        settings_layout = QFormLayout()
        
        self.settings_text = QTextEdit()
        self.settings_text.setReadOnly(True)
        self.settings_text.setMaximumHeight(300)
        settings_layout.addRow(self.settings_text)
        
        settings_group.setLayout(settings_layout)
        advanced_layout.addWidget(settings_group)
        
        advanced_layout.addStretch()
        tabs.addTab(advanced_tab, "Advanced")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_settings)
        button_layout.addWidget(apply_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept_settings)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_current_settings(self):
        """Load and display current settings"""
        current_mode = self.performance_manager.get_current_mode()
        
        # Select current mode radio button
        if current_mode in self.mode_radios:
            self.mode_radios[current_mode].setChecked(True)
        
        # Update settings display
        self.update_settings_display()
    
    def update_settings_display(self):
        """Update the settings display text"""
        # Get selected mode
        selected_mode = self.get_selected_mode()
        if selected_mode:
            settings = self.performance_manager.get_mode_settings(selected_mode)
            
            settings_text = "Current Mode Settings:\n\n"
            
            settings_text += "Timer Intervals:\n"
            settings_text += f"  ROS2 Update: {settings['ros2_update_interval']}ms\n"
            settings_text += f"  Metrics Update: {settings['metrics_update_interval']}ms\n"
            settings_text += f"  History Update: {settings['history_update_interval']}ms\n"
            settings_text += f"  Chart Update: {settings['chart_update_interval']}ms\n\n"
            
            settings_text += "Thread Pool:\n"
            settings_text += f"  Max Threads: {settings['max_threads']}\n"
            settings_text += f"  Concurrent Operations: {settings['max_concurrent_threads']}\n\n"
            
            settings_text += "Cache Settings:\n"
            settings_text += f"  Cache Timeout: {settings['cache_timeout']}s\n"
            settings_text += f"  System Metrics Cache: {settings['system_metrics_cache']}s\n"
            settings_text += f"  Topic Check Interval: {settings['topic_check_interval']}s\n\n"
            
            settings_text += "Chart Settings:\n"
            settings_text += f"  Buffer Size: {settings['chart_buffer_size']} samples\n"
            settings_text += f"  Auto-Pause: {'Yes' if settings['chart_auto_pause'] else 'No'}\n\n"
            
            settings_text += "Memory Settings:\n"
            settings_text += f"  History Max Entries: {settings['history_max_entries']}\n"
            settings_text += f"  Profiler Enabled: {'Yes' if settings['enable_profiler'] else 'No'}\n"
            settings_text += f"  Lazy Load Widgets: {'Yes' if settings['lazy_load_widgets'] else 'No'}\n"
            
            self.settings_text.setPlainText(settings_text)
    
    def get_selected_mode(self) -> PerformanceMode:
        """Get the currently selected mode"""
        for mode, radio in self.mode_radios.items():
            if radio.isChecked():
                return mode
        return PerformanceMode.BALANCED
    
    def auto_detect_mode(self):
        """Auto-detect and select optimal mode"""
        # Re-detect system specs
        self.performance_manager.system_info = self.performance_manager._detect_system_specs()
        optimal_mode = self.performance_manager._auto_detect_mode()
        
        # Update UI
        if optimal_mode in self.mode_radios:
            self.mode_radios[optimal_mode].setChecked(True)
            self.update_settings_display()
        
        # Update system info display
        self.info_text.setPlainText(self.performance_manager.get_system_info_text())
    
    def apply_settings(self):
        """Apply selected settings without closing dialog"""
        selected_mode = self.get_selected_mode()
        self.performance_manager.set_mode(selected_mode)
        self.mode_changed.emit(selected_mode)
        self.update_settings_display()
    
    def accept_settings(self):
        """Apply settings and close dialog"""
        self.apply_settings()
        self.accept()
