"""
Bag Playback Widget - controls for playing back recorded bags
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,  # type: ignore
                             QGroupBox, QLabel, QSlider, QComboBox, QFileDialog,
                             QCheckBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QTimer  # type: ignore
import subprocess
import os


class BagPlaybackWidget(QWidget):
    """Widget for playing back ROS2 bags"""
    
    def __init__(self, ros2_manager):
        super().__init__()
        self.ros2_manager = ros2_manager
        self.playback_process = None
        self.is_playing = False
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Group box
        group = QGroupBox("Bag Playback Control")
        group_layout = QVBoxLayout()
        
        # Bag selection
        bag_layout = QHBoxLayout()
        bag_layout.addWidget(QLabel("Bag File:"))
        
        self.bag_combo = QComboBox()
        self.bag_combo.setMinimumWidth(400)
        bag_layout.addWidget(self.bag_combo)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_bag)
        bag_layout.addWidget(browse_btn)
        
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.refresh_bag_list)
        bag_layout.addWidget(refresh_btn)
        
        bag_layout.addStretch()
        
        group_layout.addLayout(bag_layout)
        
        # Playback options
        options_layout = QHBoxLayout()
        
        self.loop_check = QCheckBox("Loop")
        options_layout.addWidget(self.loop_check)
        
        options_layout.addWidget(QLabel("Rate:"))
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setMinimum(0.1)
        self.rate_spin.setMaximum(10.0)
        self.rate_spin.setValue(1.0)
        self.rate_spin.setSingleStep(0.1)
        self.rate_spin.setSuffix("x")
        options_layout.addWidget(self.rate_spin)
        
        self.start_paused_check = QCheckBox("Start Paused")
        options_layout.addWidget(self.start_paused_check)
        
        options_layout.addStretch()
        
        group_layout.addLayout(options_layout)
        
        # Playback controls
        control_layout = QHBoxLayout()
        
        self.play_btn = QPushButton("▶ Play")
        self.play_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.play_btn.setMinimumHeight(40)
        self.play_btn.clicked.connect(self.play_bag)
        control_layout.addWidget(self.play_btn)
        
        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setMinimumHeight(40)
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.pause_playback)
        control_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.clicked.connect(self.stop_playback)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        group_layout.addLayout(control_layout)
        
        # Status
        self.status_label = QLabel("Status: Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        group_layout.addWidget(self.status_label)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        self.setLayout(layout)
        
        # Initial bag list
        self.refresh_bag_list()
        
    def refresh_bag_list(self):
        """Refresh the list of available bags"""
        self.bag_combo.clear()
        
        recordings_dir = self.ros2_manager.get_recordings_directory()
        if os.path.exists(recordings_dir):
            for item in os.listdir(recordings_dir):
                item_path = os.path.join(recordings_dir, item)
                if os.path.isdir(item_path):
                    # Check if it's a bag directory
                    if os.path.exists(os.path.join(item_path, 'metadata.yaml')):
                        self.bag_combo.addItem(item_path)
                        
    def browse_bag(self):
        """Browse for bag file"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Bag Directory", 
            self.ros2_manager.get_recordings_directory()
        )
        if directory:
            index = self.bag_combo.findText(directory)
            if index >= 0:
                self.bag_combo.setCurrentIndex(index)
            else:
                self.bag_combo.addItem(directory)
                self.bag_combo.setCurrentText(directory)
                
    def play_bag(self):
        """Start playing the selected bag"""
        bag_path = self.bag_combo.currentText()
        if not bag_path or not os.path.exists(bag_path):
            self.status_label.setText("Status: Please select a valid bag file")
            return
            
        if self.is_playing:
            return
            
        # Build command
        cmd = ['ros2', 'bag', 'play', bag_path]
        
        if self.loop_check.isChecked():
            cmd.append('--loop')
            
        rate = self.rate_spin.value()
        cmd.extend(['--rate', str(rate)])
        
        if self.start_paused_check.isChecked():
            cmd.append('--start-paused')
            
        try:
            self.playback_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.is_playing = True
            self.play_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            
            self.status_label.setText(f"Status: Playing at {rate}x speed")
            
        except Exception as e:
            self.status_label.setText(f"Status: Error - {e}")
            
    def pause_playback(self):
        """Pause playback (note: ROS2 bag play doesn't support pause natively)"""
        self.status_label.setText("Status: Pause not supported - use Stop")
        
    def stop_playback(self):
        """Stop playback"""
        self.is_playing = False
        
        if self.playback_process:
            try:
                self.playback_process.terminate()
                self.playback_process.wait(timeout=5)
            except:
                self.playback_process.kill()
            finally:
                self.playback_process = None
                
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        
        self.status_label.setText("Status: Stopped")
