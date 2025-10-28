"""
Topic Echo Widget - displays live topic messages
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,  # type: ignore
                             QPushButton, QGroupBox, QComboBox, QLabel,
                             QSpinBox, QCheckBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, pyqtSignal, QObject  # type: ignore
from PyQt5.QtGui import QFont  # type: ignore
import subprocess
import threading


class EchoReader(QObject):
    """Helper class to read echo output in thread and emit signals"""
    message_received = pyqtSignal(str)
    echo_finished = pyqtSignal()
    
    def __init__(self, process, max_messages):
        super().__init__()
        self.process = process
        self.max_messages = max_messages
        self.is_running = True
        
    def read_output(self):
        """Read output from process and emit signals"""
        msg_count = 0
        
        try:
            for line in self.process.stdout:
                if not self.is_running:
                    break
                    
                self.message_received.emit(line.rstrip())
                
                # Count messages (look for separator)
                if line.strip() == '---':
                    msg_count += 1
                    if msg_count >= self.max_messages:
                        self.message_received.emit(f"\n=== Reached max messages ({self.max_messages}) ===\n")
                        self.echo_finished.emit()
                        break
                        
        except Exception as e:
            self.message_received.emit(f"Error reading output: {e}")
        finally:
            self.echo_finished.emit()
    
    def stop(self):
        """Stop reading"""
        self.is_running = False


class TopicEchoWidget(QWidget):
    """Widget for echoing topic messages"""
    
    def __init__(self, ros2_manager):
        super().__init__()
        self.ros2_manager = ros2_manager
        self.echo_process = None
        self.echo_reader = None
        self.echo_thread = None
        self.is_echoing = False
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Group box
        group = QGroupBox("Topic Echo - Live Message Preview")
        group_layout = QVBoxLayout()
        
        # Controls
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("Topic:"))
        self.topic_combo = QComboBox()
        self.topic_combo.setEditable(True)
        self.topic_combo.setMinimumWidth(300)
        control_layout.addWidget(self.topic_combo)
        
        refresh_topics_btn = QPushButton("↻")
        refresh_topics_btn.setMaximumWidth(40)
        refresh_topics_btn.clicked.connect(self.refresh_topic_list)
        control_layout.addWidget(refresh_topics_btn)
        
        control_layout.addWidget(QLabel("Max Messages:"))
        self.max_messages_spin = QSpinBox()
        self.max_messages_spin.setMinimum(1)
        self.max_messages_spin.setMaximum(100)
        self.max_messages_spin.setValue(10)
        control_layout.addWidget(self.max_messages_spin)
        
        self.truncate_check = QCheckBox("Truncate Arrays")
        self.truncate_check.setChecked(True)
        control_layout.addWidget(self.truncate_check)
        
        control_layout.addStretch()
        
        self.start_echo_btn = QPushButton("Start Echo")
        self.start_echo_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.start_echo_btn.clicked.connect(self.start_echo)
        control_layout.addWidget(self.start_echo_btn)
        
        self.stop_echo_btn = QPushButton("Stop Echo")
        self.stop_echo_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.stop_echo_btn.clicked.connect(self.stop_echo)
        self.stop_echo_btn.setEnabled(False)
        control_layout.addWidget(self.stop_echo_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_output)
        control_layout.addWidget(clear_btn)
        
        group_layout.addLayout(control_layout)
        
        # Output display
        self.echo_output = QTextEdit()
        self.echo_output.setReadOnly(True)
        self.echo_output.setFont(QFont("Monospace", 9))
        self.echo_output.setMinimumHeight(200)
        group_layout.addWidget(self.echo_output)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        self.setLayout(layout)
        
        # Initial topic list refresh
        self.refresh_topic_list()
        
    def refresh_topic_list(self):
        """Refresh the list of available topics"""
        current_text = self.topic_combo.currentText()
        self.topic_combo.clear()
        
        topics = self.ros2_manager.get_topics_info()
        topic_names = [t['name'] for t in topics]
        self.topic_combo.addItems(topic_names)
        
        # Restore previous selection if it exists
        index = self.topic_combo.findText(current_text)
        if index >= 0:
            self.topic_combo.setCurrentIndex(index)
            
    def start_echo(self):
        """Start echoing the selected topic"""
        topic = self.topic_combo.currentText()
        if not topic:
            self.echo_output.append("Please select a topic\n")
            return
            
        if self.is_echoing:
            return
            
        self.echo_output.append(f"=== Starting echo on {topic} ===\n")
        
        # Build command
        cmd = ['ros2', 'topic', 'echo', topic]
        
        if self.truncate_check.isChecked():
            cmd.extend(['--truncate-length', '100'])
            
        max_msgs = self.max_messages_spin.value()
        
        try:
            self.echo_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            self.is_echoing = True
            self.start_echo_btn.setEnabled(False)
            self.stop_echo_btn.setEnabled(True)
            
            # Create echo reader with signals
            self.echo_reader = EchoReader(self.echo_process, max_msgs)
            self.echo_reader.message_received.connect(self.append_message)
            self.echo_reader.echo_finished.connect(self.stop_echo)
            
            # Start thread to read output
            self.echo_thread = threading.Thread(
                target=self.echo_reader.read_output,
                daemon=True
            )
            self.echo_thread.start()
            
        except Exception as e:
            self.echo_output.append(f"Error starting echo: {e}\n")
    
    @pyqtSlot(str)
    def append_message(self, message):
        """Append message to output (called from signal in main thread)"""
        self.echo_output.append(message)
            
    def stop_echo(self):
        """Stop echoing"""
        self.is_echoing = False
        
        # Stop the reader
        if self.echo_reader:
            self.echo_reader.stop()
            self.echo_reader = None
        
        if self.echo_process:
            try:
                self.echo_process.terminate()
                self.echo_process.wait(timeout=2)
            except:
                self.echo_process.kill()
            finally:
                self.echo_process = None
                
        self.start_echo_btn.setEnabled(True)
        self.stop_echo_btn.setEnabled(False)
        self.echo_output.append("\n=== Echo stopped ===\n")
        
    def clear_output(self):
        """Clear the output display"""
        self.echo_output.clear()
