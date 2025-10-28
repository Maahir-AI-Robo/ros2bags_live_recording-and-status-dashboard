"""
Main Window for ROS2 Dashboard
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,   # type: ignore
                             QPushButton, QLabel, QTableWidget, QTableWidgetItem,
                             QGroupBox, QGridLayout, QStatusBar, QSplitter,
                             QMessageBox, QFileDialog, QHeaderView, QTabWidget, QShortcut,
                             QSystemTrayIcon, QMenu)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot  # type: ignore
from PyQt5.QtGui import QFont, QColor, QKeySequence  # type: ignore
import os
import json
from datetime import datetime

from core.ros2_manager import ROS2Manager  # type: ignore
from core.metrics_collector import MetricsCollector  # type: ignore
from core.async_worker import AsyncROS2Manager  # type: ignore
from gui.topic_monitor import TopicMonitorWidget  # type: ignore
from gui.recording_control import RecordingControlWidget  # type: ignore
from gui.metrics_display import MetricsDisplayWidget  # type: ignore
from gui.node_monitor import NodeMonitorWidget  # type: ignore
from gui.service_monitor import ServiceMonitorWidget  # type: ignore
from gui.topic_echo import TopicEchoWidget  # type: ignore
from gui.bag_playback import BagPlaybackWidget  # type: ignore
from gui.advanced_stats import AdvancedStatsWidget  # type: ignore
from gui.network_upload import NetworkUploadWidget  # type: ignore
from gui.live_charts import LiveChartsWidget  # type: ignore
from gui.themes import ThemeManager  # type: ignore
from gui.recording_templates import RecordingTemplatesWidget  # type: ignore
from gui.network_robots import NetworkRobotsWidget  # type: ignore
from core.network_manager import NetworkManager  # type: ignore
from core.recording_triggers import SmartRecordingManager  # type: ignore
from core.performance_profiler import PerformanceProfiler  # type: ignore
from core.performance_modes import PerformanceModeManager, PerformanceMode  # type: ignore
from gui.performance_settings_dialog import PerformanceSettingsDialog  # type: ignore


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize performance manager FIRST
        self.performance_manager = PerformanceModeManager()
        self.perf_settings = self.performance_manager.get_mode_settings()
        
        print(f"\n{'='*60}")
        print(f"ROS2 Dashboard - Adaptive Performance Mode")
        print(f"{'='*60}")
        print(self.performance_manager.get_system_info_text())
        print(f"\nUsing {self.performance_manager.get_current_mode().value.upper()} mode")
        print(f"{'='*60}\n")
        
        self.ros2_manager = ROS2Manager()
        self.async_ros2 = AsyncROS2Manager(
            self.ros2_manager,
            max_threads=self.perf_settings['max_threads'],
            cache_timeout=self.perf_settings['cache_timeout']
        )
        self.metrics_collector = MetricsCollector()
        self.network_manager = None  # Initialize later
        self.is_recording = False
        self.theme_manager = ThemeManager()  # Theme management
        
        # DEBOUNCING - prevent excessive updates
        self._last_ros2_update = 0
        self._ros2_update_cooldown = 1.0  # At least 1 second between updates
        self._last_metrics_update = 0
        self._metrics_update_cooldown = 0.5  # At least 0.5 seconds between metrics
        
        self.init_ui()
        self.setup_timers()
        self.setup_system_tray()  # Setup notifications
        
        # Start network manager after UI is ready (non-blocking)
        QTimer.singleShot(1000, self.init_network_manager)
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("ROS2 Data Recording & Status Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("ROS2 Bags Recording Dashboard")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Create splitter for resizable sections
        splitter = QSplitter(Qt.Vertical)
        
        # Top section: Recording controls and status
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        
        # Recording control panel
        self.recording_control = RecordingControlWidget(self.ros2_manager)
        self.recording_control.recording_started.connect(self.on_recording_started)
        self.recording_control.recording_stopped.connect(self.on_recording_stopped)
        top_layout.addWidget(self.recording_control)
        
        # Metrics display
        self.metrics_display = MetricsDisplayWidget(self.metrics_collector)
        top_layout.addWidget(self.metrics_display)
        
        splitter.addWidget(top_widget)
        
        # Middle section: Tabbed interface for different features
        self.tabs = QTabWidget()
        
        # Tab 1: Topic Monitor
        self.topic_monitor = TopicMonitorWidget(self.ros2_manager)
        self.tabs.addTab(self.topic_monitor, "📡 Topics")
        
        # Connect topic selection changes to recording control
        self.topic_monitor.topics_changed.connect(self.recording_control.update_selected_topics)
        
        # Tab 2: Node Monitor
        self.node_monitor = NodeMonitorWidget(self.ros2_manager)
        self.tabs.addTab(self.node_monitor, "🔧 Nodes")
        
        # Tab 3: Service Monitor
        self.service_monitor = ServiceMonitorWidget(self.ros2_manager)
        self.tabs.addTab(self.service_monitor, "⚙️ Services")
        
        # Tab 4: Topic Echo
        self.topic_echo = TopicEchoWidget(self.ros2_manager)
        self.tabs.addTab(self.topic_echo, "👁️ Topic Echo")
        
        # Tab 5: Bag Playback
        self.bag_playback = BagPlaybackWidget(self.ros2_manager)
        self.tabs.addTab(self.bag_playback, "▶️ Playback")
        
        # Tab 6: Advanced Stats
        self.advanced_stats = AdvancedStatsWidget(self.ros2_manager)
        self.tabs.addTab(self.advanced_stats, "📊 Stats")
        
        # Tab 7: Live Charts (NEW - Real-time visualization with adaptive performance) ⭐
        self.live_charts = LiveChartsWidget(
            self.metrics_collector, 
            self.ros2_manager,
            buffer_size=self.perf_settings['chart_buffer_size'],
            update_interval=self.perf_settings['chart_update_interval'],
            auto_pause=self.perf_settings['chart_auto_pause']
        )
        self.tabs.addTab(self.live_charts, "📈 Live Charts")
        
        # Tab 8: Network Robots (NEW - Discover robots on network) ⭐
        self.network_robots = NetworkRobotsWidget()
        self.network_robots.robot_selected.connect(self.on_robot_selected)
        self.tabs.addTab(self.network_robots, "🤖 Network Robots")
        
        # Tab 9: Templates (Recording templates) ⭐
        self.templates = RecordingTemplatesWidget(self.recording_control, self.topic_monitor)
        self.tabs.addTab(self.templates, "📋 Templates")
        
        # Tab 10: Network Upload (will be initialized later)
        # Create a placeholder network manager for now
        from core.network_manager import NetworkManager
        placeholder_network_manager = NetworkManager()
        self.network_upload = NetworkUploadWidget(placeholder_network_manager)
        self.tabs.addTab(self.network_upload, "☁️ Upload")
        
        splitter.addWidget(self.tabs)
        
        # Bottom section: Recording history and file info
        self.recording_history = self.create_recording_history()
        splitter.addWidget(self.recording_history)
        
        # Set splitter sizes
        splitter.setSizes([300, 400, 200])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.update_status("Ready")
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Setup keyboard shortcuts ⭐ NEW
        self.setup_shortcuts()
    
    def setup_menu_bar(self):
        """Setup application menu bar"""
        menubar = self.menuBar()
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        theme_action = view_menu.addAction("Toggle &Theme")
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self.toggle_theme)
        
        view_menu.addSeparator()
        
        charts_action = view_menu.addAction("&Live Charts")
        charts_action.setShortcut("Ctrl+L")
        charts_action.triggered.connect(lambda: self.tabs.setCurrentIndex(6))
        
        # Settings menu
        settings_menu = menubar.addMenu("&Settings")
        
        perf_action = settings_menu.addAction("&Performance Mode...")
        perf_action.triggered.connect(self.show_performance_settings)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        shortcuts_action = help_menu.addAction("&Keyboard Shortcuts")
        shortcuts_action.setShortcut("Ctrl+H")
        shortcuts_action.triggered.connect(self.show_keyboard_shortcuts_help)
        
        help_menu.addSeparator()
        
        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self.show_about_dialog)
        
    def show_about_dialog(self):
        """Show about dialog"""
        mode = self.performance_manager.get_current_mode().value.upper()
        about_text = f"""
<h2>ROS2 Dashboard</h2>
<p>Advanced recording and monitoring dashboard for ROS2</p>
<p><b>Performance Mode:</b> {mode}</p>
<p><b>System:</b> {self.performance_manager.system_info['memory_gb']}GB RAM, 
{self.performance_manager.system_info['cpu_count']} CPU cores</p>
<hr>
<p><i>For best results, adjust performance mode in Settings → Performance Mode</i></p>
        """
        QMessageBox.about(self, "About ROS2 Dashboard", about_text)
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts for quick access"""
        # Ctrl+R - Start/Stop Recording
        record_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        record_shortcut.activated.connect(self.toggle_recording)
        
        # Ctrl+S - Stop Recording (if active)
        stop_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        stop_shortcut.activated.connect(self.stop_recording_shortcut)
        
        # Ctrl+P - Open Playback Tab
        playback_shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        playback_shortcut.activated.connect(lambda: self.tabs.setCurrentIndex(4))
        
        # Ctrl+E - Export Performance Report
        export_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        export_shortcut.activated.connect(self.export_metrics)
        
        # Ctrl+L - Switch to Live Charts
        charts_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        charts_shortcut.activated.connect(lambda: self.tabs.setCurrentIndex(6))
        
        # Ctrl+H - Show Help
        help_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        help_shortcut.activated.connect(self.show_keyboard_shortcuts_help)
        
        # Ctrl+T - Toggle Theme
        theme_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        theme_shortcut.activated.connect(self.toggle_theme)
        
    def toggle_theme(self):
        """Toggle between dark and light theme (Ctrl+T)"""
        from PyQt5.QtWidgets import QApplication
        theme = self.theme_manager.toggle_theme(QApplication.instance())
        self.update_status(f"🎨 Theme switched to: {theme.title()}")
        
    def set_initial_theme(self):
        """Set initial theme on startup"""
        from PyQt5.QtWidgets import QApplication
        self.theme_manager.set_theme(QApplication.instance(), 'light')
    
    def show_performance_settings(self):
        """Show performance settings dialog"""
        dialog = PerformanceSettingsDialog(self.performance_manager, self)
        dialog.mode_changed.connect(self.on_performance_mode_changed)
        dialog.exec_()
    
    def on_performance_mode_changed(self, mode):
        """Handle performance mode change"""
        # Get new settings
        self.perf_settings = self.performance_manager.get_mode_settings()
        
        # Update async manager
        self.async_ros2.max_threads = self.perf_settings['max_threads']
        self.async_ros2.cache_timeout = self.perf_settings['cache_timeout']
        
        # Update metrics collector caching
        self.metrics_collector.system_metrics_cache_timeout = self.perf_settings['system_metrics_cache']
        
        # Update timers
        self.ros2_timer.setInterval(self.perf_settings['ros2_update_interval'])
        self.metrics_timer.setInterval(self.perf_settings['metrics_update_interval'])
        self.history_timer.setInterval(self.perf_settings['history_update_interval'])
        
        # Update live charts if exists
        if hasattr(self, 'live_charts'):
            self.live_charts.update_interval = self.perf_settings['chart_update_interval']
            self.live_charts.buffer_size = self.perf_settings['chart_buffer_size']
            self.live_charts.auto_pause = self.perf_settings['chart_auto_pause']
        
        mode_name = mode if isinstance(mode, str) else mode.value
        self.update_status(f"⚡ Performance mode changed to: {mode_name.upper()}")
        
        QMessageBox.information(
            self,
            "Performance Mode Changed",
            f"Performance mode set to: {mode_name.upper()}\n\n"
            f"Settings will take effect immediately.\n"
            f"Some changes may require tab switching to fully apply."
        )
        
    def toggle_recording(self):
        """Toggle recording state (start/stop) - bound to Ctrl+R."""
        if not self.recording_control.is_recording:
            # Start recording
            selected_topics = self.topic_monitor.selected_topics
            if not selected_topics:
                self.show_notification(
                    "Recording Failed",
                    "No topics selected for recording",
                    QSystemTrayIcon.Warning
                )
                QMessageBox.warning(self, "No Topics Selected", 
                                  "Please select topics to record in the Topics tab.")
                return
            
            self.recording_control.start_recording()
            self.show_notification(
                "Recording Started",
                f"Recording {len(selected_topics)} topic(s)",
                QSystemTrayIcon.Information
            )
        else:
            # Stop recording
            self.recording_control.stop_recording()
            self.show_notification(
                "Recording Stopped",
                "Recording saved successfully",
                QSystemTrayIcon.Information
            )
            
    def stop_recording_shortcut(self):
        """Stop recording (Ctrl+S shortcut)."""
        if self.recording_control.is_recording:
            self.recording_control.stop_recording()
            self.show_notification(
                "Recording Stopped",
                "Recording saved successfully",
                QSystemTrayIcon.Information
            )
            
    def export_metrics(self):
        """Export current metrics (Ctrl+E shortcut)."""
        try:
            filename = f"ros2_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            metrics = self.metrics_collector.get_live_metrics()
            
            with open(filename, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            self.show_notification(
                "Metrics Exported",
                f"Saved to {filename}",
                QSystemTrayIcon.Information
            )
            QMessageBox.information(self, "Export Successful", 
                                  f"Metrics exported to {filename}")
        except Exception as e:
            self.show_notification(
                "Export Failed",
                str(e),
                QSystemTrayIcon.Critical
            )
            QMessageBox.critical(self, "Export Failed", f"Error: {e}")
                
    def show_keyboard_shortcuts_help(self):
        """Show keyboard shortcuts help dialog (Ctrl+H)"""
        help_text = """
<h2>Keyboard Shortcuts</h2>
<table>
<tr><td><b>Ctrl+R</b></td><td>Start/Stop Recording</td></tr>
<tr><td><b>Ctrl+S</b></td><td>Stop Recording</td></tr>
<tr><td><b>Ctrl+P</b></td><td>Open Playback Tab</td></tr>
<tr><td><b>Ctrl+L</b></td><td>Open Live Charts Tab</td></tr>
<tr><td><b>Ctrl+E</b></td><td>Export Metrics & Performance Data</td></tr>
<tr><td><b>Ctrl+T</b></td><td>Toggle Dark/Light Theme</td></tr>
<tr><td><b>Ctrl+H</b></td><td>Show this Help Dialog</td></tr>
</table>
<p><i>Tip: Use shortcuts for fastest workflow!</i></p>
        """
        QMessageBox.information(self, "Keyboard Shortcuts", help_text)
        
    def create_recording_history(self):
        """Create recording history widget"""
        group = QGroupBox("Recording History & File Information")
        layout = QVBoxLayout()
        
        # Table for recordings
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Filename", "Size (MB)", "Duration", "Topics", "Start Time", "Status"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.history_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.refresh_recording_history)
        button_layout.addWidget(refresh_btn)
        
        open_folder_btn = QPushButton("Open Recordings Folder")
        open_folder_btn.clicked.connect(self.open_recordings_folder)
        button_layout.addWidget(open_folder_btn)
        
        layout.addLayout(button_layout)
        
        group.setLayout(layout)
        return group
        
    def setup_timers(self):
        """Setup update timers - AGGRESSIVE intervals to reduce lag"""
        perf = self.perf_settings
        
        # ROS2 info timer - INCREASED interval (less frequent)
        self.ros2_timer = QTimer()
        self.ros2_timer.timeout.connect(self.update_ros2_info_async)
        # Use slower updates - 3+ seconds between calls
        self.ros2_timer.start(max(3000, perf.get('ros2_update_interval', 3000)))
        
        # Metrics timer - INCREASED interval
        self.metrics_timer = QTimer()
        self.metrics_timer.timeout.connect(self.update_metrics)
        # Use slower updates - 1 second between calls
        self.metrics_timer.start(max(1000, perf.get('metrics_update_interval', 1000)))
        
        # Recording history timer - INCREASED interval
        self.history_timer = QTimer()
        self.history_timer.timeout.connect(self.refresh_recording_history)
        # Update every 5 seconds instead of 2
        self.history_timer.start(max(5000, perf.get('history_update_interval', 5000)))
        
        # Connect to performance mode changes
        self.performance_manager.mode_changed.connect(self.on_performance_mode_changed)
    
    def setup_system_tray(self):
        """Setup system tray icon and desktop notifications."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
        self.tray_icon.setToolTip("ROS2 Dashboard")
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = tray_menu.addAction("Show Dashboard")
        show_action.triggered.connect(self.show)
        
        tray_menu.addSeparator()
        
        record_action = tray_menu.addAction("Start Recording")
        record_action.triggered.connect(self.toggle_recording)
        
        tray_menu.addSeparator()
        
        quit_action = tray_menu.addAction("Exit")
        quit_action.triggered.connect(self.close)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Connect tray icon double-click to show window
        self.tray_icon.activated.connect(self.on_tray_activated)
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()
    
    def show_notification(self, title: str, message: str, icon=QSystemTrayIcon.Information):
        """Show desktop notification."""
        if hasattr(self, 'tray_icon') and self.tray_icon.supportsMessages():
            self.tray_icon.showMessage(title, message, icon, 3000)  # 3 second duration
        
    def init_network_manager(self):
        """Initialize network manager after UI is ready"""
        try:
            self.network_manager = NetworkManager()
            self.network_manager.start()
            
            # Update the network upload widget
            if hasattr(self, 'network_upload'):
                self.network_upload.network_manager = self.network_manager
                
            print("Network Manager initialized")
        except Exception as e:
            print(f"Warning: Could not initialize Network Manager: {e}")
            self.network_manager = None
            
    def update_ros2_info_async(self):
        """
        AGGRESSIVE debounced ROS2 updates - prevent excessive calls
        """
        import time
        
        # DEBOUNCE - skip if updated recently
        current_time = time.time()
        if current_time - self._last_ros2_update < self._ros2_update_cooldown:
            return
        self._last_ros2_update = current_time
        
        # Skip if window is minimized or hidden
        if not self.isVisible():
            return
        
        # Allow up to 1 thread
        if self.async_ros2.active_thread_count() >= 1:
            return  # Skip if thread already running
            
        current_tab = self.tabs.currentIndex()
        
        # Update ONLY the active tab (most efficient)
        if current_tab == 0:  # Topics
            self.async_ros2.get_topics_async(self.topic_monitor.update_topics_data)
        elif current_tab == 1:  # Nodes
            self.async_ros2.get_nodes_async(self.node_monitor.update_nodes_data)
        elif current_tab == 2:  # Services
            self.async_ros2.get_services_async(self.service_monitor.update_services_data)
        
    def update_metrics(self):
        """Update dashboard metrics - AGGRESSIVE debouncing"""
        import time
        
        # DEBOUNCE - skip if updated recently
        current_time = time.time()
        if current_time - self._last_metrics_update < self._metrics_update_cooldown:
            return
        self._last_metrics_update = current_time
        
        if self.is_recording:
            # During recording: full metrics update
            self.metrics_collector.update(self.ros2_manager)
        else:
            # When not recording: update live metrics (system stats + topic count)
            # This uses cached values for performance
            live_metrics = self.metrics_collector.get_live_metrics(self.ros2_manager)
        
        # Always update the display
        self.metrics_display.update_display()
    
    def on_robot_selected(self, hostname: str, topics: list):
        """Handle robot selection from network discovery - seamless workflow"""
        if not topics:
            self.update_status(f"⚠️ Robot {hostname} has no topics")
            return
        
        # Store selected robot info
        self.selected_robot = {
            'hostname': hostname,
            'topics': topics,
            'selected_at': datetime.now()
        }
        
        # Auto-select discovered topics in topic monitor
        if hasattr(self, 'topic_monitor'):
            # Refresh topic list first to ensure we have latest
            self.topic_monitor.refresh_topics()
            
            # Auto-select matching topics
            selected_count = 0
            for topic in topics:
                # Try to select the topic in the topic monitor
                for row in range(self.topic_monitor.topic_table.rowCount()):
                    table_topic = self.topic_monitor.topic_table.item(row, 0)
                    if table_topic and table_topic.text() == topic:
                        self.topic_monitor.topic_table.selectRow(row)
                        selected_count += 1
                        break
            
            # Switch to topics tab
            self.tabs.setCurrentIndex(0)
            
            self.update_status(f"🤖 Selected {selected_count}/{len(topics)} topics from robot: {hostname}")
            
            # Show workflow dialog
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Robot Selected - Ready to Record")
            msg.setText(f"✅ Robot: {hostname}\n"
                       f"📊 Topics: {selected_count} selected\n\n"
                       f"Next Steps:")
            msg.setInformativeText(
                "1️⃣ Review selected topics in the Topics tab\n"
                "2️⃣ Click 'Start Recording' to begin\n"
                "3️⃣ Recording will auto-upload to server when complete\n\n"
                "💡 Tip: You can add/remove topics before recording"
            )
            msg.setStandardButtons(QMessageBox.Ok)
            
            # Add quick action buttons
            record_button = msg.addButton("🎬 Start Recording Now", QMessageBox.ActionRole)
            
            result = msg.exec_()
            
            # Check if user clicked record button
            if msg.clickedButton() == record_button:
                # Trigger recording immediately with robot metadata
                if selected_count > 0:
                    self.recording_control.start_recording(robot_metadata=self.selected_robot)
                else:
                    QMessageBox.warning(self, "No Topics", 
                                      "No matching topics found. Please select topics manually.")
        else:
            self.update_status(f"🤖 Robot {hostname} selected with {len(topics)} topics")
            
    @pyqtSlot()
    def on_recording_started(self):
        """Handle recording started event"""
        self.is_recording = True
        self.metrics_collector.reset()
        self.update_status("Recording in progress...")
        
        # Speed up metrics timer during recording
        self.metrics_timer.setInterval(self.perf_settings['metrics_update_interval'])
        
        # Show notification
        self.show_notification("Recording Started", "ROS2 bag recording in progress")
        
    @pyqtSlot()
    def on_recording_stopped(self):
        """Handle recording stopped event - with auto-upload support"""
        self.is_recording = False
        self.update_status("Recording stopped")
        
        # Slow down metrics timer when not recording (save CPU, still show live topics)
        # Use 2x the normal interval when idle
        idle_interval = self.perf_settings['metrics_update_interval'] * 2
        self.metrics_timer.setInterval(idle_interval)
        
        self.refresh_recording_history()
        
        # Show notification
        self.show_notification("Recording Stopped", "Recording saved successfully")
        
        # Auto-upload if enabled and network manager is ready
        if self.network_manager and hasattr(self, 'network_upload'):
            # Check if auto-upload is enabled
            if hasattr(self.network_upload, 'auto_upload') and self.network_upload.auto_upload:
                # Get the recording path
                if hasattr(self.recording_control, 'current_bag_name'):
                    bag_name = self.recording_control.current_bag_name
                    output_dir = self.recording_control.dir_input.text()
                    bag_path = os.path.join(output_dir, bag_name)
                    
                    # Include robot metadata in upload
                    metadata = {}
                    if hasattr(self.recording_control, 'current_bag_metadata'):
                        metadata = self.recording_control.current_bag_metadata or {}
                    
                    # Trigger upload
                    self.update_status(f"📤 Auto-uploading {bag_name}...")
                    self.show_notification(
                        "Auto-Upload Starting",
                        f"Uploading {bag_name} to server..."
                    )
                    
                    # The actual upload will be handled by network_upload widget
                    # Just switch to upload tab to show progress
                    try:
                        # Add metadata tag if from robot discovery
                        if metadata and 'hostname' in metadata:
                            tags = f"robot:{metadata['hostname']}"
                            self.network_upload.tags_input.setText(tags)
                        
                        # Queue the upload (network_upload will handle it)
                        QTimer.singleShot(1000, lambda: self.network_upload.upload_directory(bag_path))
                    except Exception as e:
                        print(f"Auto-upload error: {e}")
        
        # Show completion message with robot info if available
        if hasattr(self.recording_control, 'current_bag_metadata'):
            metadata = self.recording_control.current_bag_metadata
            if metadata and 'hostname' in metadata:
                msg = f"✅ Recording from robot '{metadata['hostname']}' saved successfully!"
                self.update_status(msg)
        
        # Show notification
        self.show_notification("Recording Stopped", "Recording saved successfully")
        
        # Auto-upload if enabled and network manager is ready
        if self.network_manager:
            bag_path = self.ros2_manager.get_current_bag_path()
            if bag_path and os.path.exists(bag_path):
                metadata = {
                    'type': 'ros2_bag',
                    'component': 'robot_recording',
                    'timestamp': datetime.now().isoformat()
                }
                self.network_upload.add_recording_upload(bag_path, metadata)
        
    def refresh_recording_history(self):
        """Refresh the recording history table"""
        recordings_dir = self.ros2_manager.get_recordings_directory()
        if not os.path.exists(recordings_dir):
            return
            
        # Get all bag files
        bag_files = []
        for root, dirs, files in os.walk(recordings_dir):
            if 'metadata.yaml' in files:
                bag_files.append(root)
                
        # Update table
        self.history_table.setRowCount(len(bag_files))
        
        for idx, bag_path in enumerate(sorted(bag_files, reverse=True)):
            # Get bag info
            bag_info = self.ros2_manager.get_bag_info(bag_path)
            
            # Filename
            filename_item = QTableWidgetItem(os.path.basename(bag_path))
            self.history_table.setItem(idx, 0, filename_item)
            
            # Size
            size_mb = bag_info.get('size_mb', 0)
            size_item = QTableWidgetItem(f"{size_mb:.2f}")
            size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.history_table.setItem(idx, 1, size_item)
            
            # Duration
            duration = bag_info.get('duration', '0s')
            self.history_table.setItem(idx, 2, QTableWidgetItem(duration))
            
            # Topics
            topic_count = bag_info.get('topic_count', 0)
            topics_item = QTableWidgetItem(str(topic_count))
            topics_item.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(idx, 3, topics_item)
            
            # Start time
            start_time = bag_info.get('start_time', 'Unknown')
            self.history_table.setItem(idx, 4, QTableWidgetItem(start_time))
            
            # Status
            status = "Complete" if bag_info.get('is_complete', True) else "Incomplete"
            status_item = QTableWidgetItem(status)
            if status == "Complete":
                status_item.setForeground(QColor('green'))
            else:
                status_item.setForeground(QColor('orange'))
            self.history_table.setItem(idx, 5, status_item)
            
    def open_recordings_folder(self):
        """Open the recordings folder in file manager"""
        recordings_dir = self.ros2_manager.get_recordings_directory()
        if os.path.exists(recordings_dir):
            os.system(f'xdg-open "{recordings_dir}"')
        else:
            QMessageBox.warning(self, "Warning", "Recordings directory does not exist yet.")
            
    def update_status(self, message):
        """Update status bar message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.statusBar.showMessage(f"[{timestamp}] {message}")
        
    def closeEvent(self, event):
        """Handle window close event - proper cleanup"""
        if self.is_recording:
            reply = QMessageBox.question(
                self, 'Confirm Exit',
                'Recording is in progress. Do you want to stop and exit?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.ros2_manager.stop_recording()
                if self.network_manager:
                    self.network_manager.stop()
                
                # Shutdown async manager thread pools
                if hasattr(self, 'async_ros2'):
                    self.async_ros2.shutdown()
                
                event.accept()
            else:
                event.ignore()
        else:
            if self.network_manager:
                self.network_manager.stop()
            
            # Shutdown async manager thread pools
            if hasattr(self, 'async_ros2'):
                self.async_ros2.shutdown()
            
            event.accept()
