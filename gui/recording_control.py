"""
Recording Control Widget - controls for starting/stopping ROS2 bag recording
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,  # type: ignore
                             QGroupBox, QLabel, QLineEdit, QFileDialog, QCheckBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer  # type: ignore
from PyQt5.QtGui import QFont, QColor
import os
from datetime import datetime


class RecordingControlWidget(QWidget):
    """Widget for controlling ROS2 bag recording"""
    
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    
    def __init__(self, ros2_manager):
        super().__init__()
        self.ros2_manager = ros2_manager
        self.is_recording = False
        self.current_bag_name = None
        self.current_bag_metadata = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Group box
        group = QGroupBox("Recording Control")
        group_layout = QVBoxLayout()
        
        # Output directory selection
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Output Directory:"))
        
        self.dir_input = QLineEdit()
        default_dir = os.path.expanduser("~/ros2_recordings")
        self.dir_input.setText(default_dir)
        self.ros2_manager.set_output_directory(default_dir)
        dir_layout.addWidget(self.dir_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(browse_btn)
        
        group_layout.addLayout(dir_layout)
        
        # Bag name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Bag Name Prefix:"))
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("recording")
        self.name_input.setText("recording")
        name_layout.addWidget(self.name_input)
        
        group_layout.addLayout(name_layout)
        
        # Recording status
        self.status_label = QLabel("Status: Ready")
        status_font = QFont()
        status_font.setPointSize(12)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        self.status_label.setAlignment(Qt.AlignCenter)
        group_layout.addWidget(self.status_label)
        
        # Recording controls
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Recording")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-size: 14px; font-weight: bold; }")
        self.start_btn.clicked.connect(self.start_recording)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Recording")
        self.stop_btn.setMinimumHeight(50)
        self.stop_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-size: 14px; font-weight: bold; }")
        self.stop_btn.clicked.connect(self.stop_recording)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        group_layout.addLayout(control_layout)
        
        # Current recording info
        self.recording_info = QLabel("")
        self.recording_info.setWordWrap(True)
        self.recording_info.setAlignment(Qt.AlignCenter)
        group_layout.addWidget(self.recording_info)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        # Selected Topics Monitor
        topics_group = QGroupBox("📊 Selected Topics (Live Rates)")
        topics_layout = QVBoxLayout()
        
        # Topics table with rates
        self.selected_topics_table = QTableWidget()
        self.selected_topics_table.setColumnCount(3)
        self.selected_topics_table.setHorizontalHeaderLabels(['Topic Name', 'Rate (Hz)', 'Status'])
        header = self.selected_topics_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.selected_topics_table.setMaximumHeight(200)
        self.selected_topics_table.setEditTriggers(QTableWidget.NoEditTriggers)
        topics_layout.addWidget(self.selected_topics_table)
        
        # Info label
        self.topics_info_label = QLabel("No topics selected yet")
        self.topics_info_label.setStyleSheet("color: #666; font-style: italic;")
        topics_layout.addWidget(self.topics_info_label)
        
        topics_group.setLayout(topics_layout)
        layout.addWidget(topics_group)
        
        # Initialize topics tracking
        self.selected_topics_data = {}  # {topic_name: {'rate': 0.0, 'last_seen': time, 'stalled': False}}
        self.topic_rates_timer = QTimer()
        self.topic_rates_timer.timeout.connect(self.update_topic_rates)
        
        self.setLayout(layout)
        
    def browse_directory(self):
        """Open directory browser"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", self.dir_input.text()
        )
        if directory:
            self.dir_input.setText(directory)
            self.ros2_manager.set_output_directory(directory)
            
    def start_recording(self, robot_metadata=None):
        """
        Start bag recording
        
        Args:
            robot_metadata: Optional dict with robot info (hostname, topics, etc.)
        """
        output_dir = self.dir_input.text()
        if not output_dir:
            QMessageBox.warning(self, "Warning", "Please specify an output directory")
            return
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        self.ros2_manager.set_output_directory(output_dir)
        
        # Generate bag name with timestamp
        prefix = self.name_input.text() or "recording"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # If recording from discovered robot, include robot name
        if robot_metadata and 'hostname' in robot_metadata:
            robot_name = robot_metadata['hostname'].split('.')[0]  # Remove domain
            bag_name = f"{prefix}_{robot_name}_{timestamp}"
        else:
            bag_name = f"{prefix}_{timestamp}"
        
        # Save robot metadata to JSON if provided
        if robot_metadata:
            metadata_file = os.path.join(output_dir, f"{bag_name}_robot_info.json")
            try:
                import json
                with open(metadata_file, 'w') as f:
                    json.dump(robot_metadata, f, indent=2)
                print(f"✅ Saved robot metadata to {metadata_file}")
            except Exception as e:
                print(f"⚠️ Could not save robot metadata: {e}")
        
        # Start recording
        success = self.ros2_manager.start_recording(bag_name)
        
        if success:
            self.is_recording = True
            self.current_bag_name = bag_name
            self.current_bag_metadata = robot_metadata
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.dir_input.setEnabled(False)
            self.name_input.setEnabled(False)
            
            self.status_label.setText("Status: Recording")
            self.status_label.setStyleSheet("color: red;")
            
            bag_path = os.path.join(output_dir, bag_name)
            if robot_metadata:
                robot_info = f" (Robot: {robot_metadata.get('hostname', 'Unknown')})"
            else:
                robot_info = ""
            self.recording_info.setText(f"Recording to: {bag_path}{robot_info}")
            
            # Start rate monitoring
            self.start_rate_monitoring()
            
            self.recording_started.emit()
        else:
            QMessageBox.critical(self, "Error", "Failed to start recording. Make sure ROS2 is running.")
            
    def stop_recording(self):
        """Stop bag recording"""
        self.ros2_manager.stop_recording()
        
        self.is_recording = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.dir_input.setEnabled(True)
        self.name_input.setEnabled(True)
        
        self.status_label.setText("Status: Stopped")
        self.status_label.setStyleSheet("color: orange;")
        
        self.recording_info.setText("Recording stopped successfully")
        
        # Stop rate monitoring
        self.stop_rate_monitoring()
        
        self.recording_stopped.emit()
    
    def update_selected_topics(self, selected_topics):
        """Update the list of selected topics for recording"""
        # Initialize tracking for new topics
        for topic in selected_topics:
            if topic not in self.selected_topics_data:
                self.selected_topics_data[topic] = {
                    'rate': 0.0,
                    'last_rate': 0.0,
                    'stalled': False,
                    'stalled_count': 0
                }
        
        # Remove topics no longer selected
        removed_topics = [t for t in self.selected_topics_data if t not in selected_topics]
        for topic in removed_topics:
            del self.selected_topics_data[topic]
        
        # Update table
        self.refresh_selected_topics_table()
        
        # Start rate update timer if recording
        if self.is_recording and not self.topic_rates_timer.isActive():
            self.topic_rates_timer.start(1000)  # Update every second
    
    def refresh_selected_topics_table(self):
        """Refresh the selected topics table display"""
        self.selected_topics_table.setRowCount(len(self.selected_topics_data))
        
        if not self.selected_topics_data:
            self.topics_info_label.setText("No topics selected yet")
            return
        
        self.topics_info_label.setText(f"Monitoring {len(self.selected_topics_data)} topic(s)")
        
        for row, (topic_name, data) in enumerate(self.selected_topics_data.items()):
            # Topic name
            topic_item = QTableWidgetItem(topic_name)
            topic_item.setFont(QFont("Monospace", 9))
            self.selected_topics_table.setItem(row, 0, topic_item)
            
            # Rate
            rate = data['rate']
            rate_item = QTableWidgetItem(f"{rate:.2f} Hz")
            rate_item.setTextAlignment(Qt.AlignCenter)
            self.selected_topics_table.setItem(row, 1, rate_item)
            
            # Status with color coding
            if data['stalled']:
                status = "⚠️ STALLED"
                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor('#ff5252'))  # Red
                status_item.setFont(QFont("", -1, QFont.Bold))
            elif rate > 0:
                status = "✅ OK"
                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor('#4CAF50'))  # Green
            else:
                status = "⏸️ NO DATA"
                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor('#ff9800'))  # Orange
            
            status_item.setTextAlignment(Qt.AlignCenter)
            self.selected_topics_table.setItem(row, 2, status_item)
    
    def update_topic_rates(self):
        """Update topic rates (called periodically during recording)"""
        if not self.is_recording:
            self.topic_rates_timer.stop()
            return
        
        try:
            # Get current topics info from ROS2
            topics_info = self.ros2_manager.get_topics_info()
            current_time = datetime.now().timestamp()
            
            # Update rates for each selected topic
            for topic_name, data in self.selected_topics_data.items():
                # Find this topic in the list
                topic_data = next((t for t in topics_info if t['name'] == topic_name), None)
                
                if topic_data:
                    rate = topic_data.get('hz', 0.0)
                    data['last_rate'] = data['rate']
                    data['rate'] = rate
                    
                    # Detect stalling: rate dropped to 0 from non-zero
                    if data['last_rate'] > 0 and rate == 0:
                        data['stalled'] = True
                        data['stalled_count'] += 1
                    elif rate > 0:
                        data['stalled'] = False
                        data['stalled_count'] = 0
                else:
                    # Topic disappeared
                    data['rate'] = 0.0
                    data['stalled'] = True
                    data['stalled_count'] += 1
            
            # Refresh table display
            self.refresh_selected_topics_table()
            
        except Exception as e:
            print(f"Error updating topic rates: {e}")
    
    def start_rate_monitoring(self):
        """Start monitoring topic rates"""
        if not self.topic_rates_timer.isActive() and self.selected_topics_data:
            self.topic_rates_timer.start(1000)  # Update every second
    
    def stop_rate_monitoring(self):
        """Stop monitoring topic rates"""
        if self.topic_rates_timer.isActive():
            self.topic_rates_timer.stop()
