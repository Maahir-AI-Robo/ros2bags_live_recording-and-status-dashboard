"""
Topic Monitor Widget - displays available ROS2 topics
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,  # type: ignore
                             QTableWidgetItem, QPushButton, QGroupBox, QHeaderView,
                             QLabel, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal  # type: ignore
from PyQt5.QtGui import QColor  # type: ignore


class TopicMonitorWidget(QWidget):
    """Widget for monitoring ROS2 topics"""
    
    topic_selected = pyqtSignal(str, bool)  # topic_name, is_selected
    topics_changed = pyqtSignal(list)  # emitted when selected topics change
    
    def __init__(self, ros2_manager, async_ros2_manager=None):
        super().__init__()
        self.ros2_manager = ros2_manager
        self.async_ros2_manager = async_ros2_manager  # NEW: optional async manager
        self.selected_topics = set()
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Group box
        group = QGroupBox("Available ROS2 Topics")
        group_layout = QVBoxLayout()
        
        # Info label
        info_layout = QHBoxLayout()
        self.topic_count_label = QLabel("Topics: 0")
        info_layout.addWidget(self.topic_count_label)
        info_layout.addStretch()
        
        # Selection buttons
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all_topics)
        info_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all_topics)
        info_layout.addWidget(deselect_all_btn)
        
        group_layout.addLayout(info_layout)
        
        # Topics table
        self.topics_table = QTableWidget()
        self.topics_table.setColumnCount(5)
        self.topics_table.setHorizontalHeaderLabels([
            "Record", "Topic Name", "Message Type", "Publishers", "Hz"
        ])
        
        # Set column widths
        header = self.topics_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        group_layout.addWidget(self.topics_table)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Topics")
        refresh_btn.clicked.connect(self.refresh_topics)
        group_layout.addWidget(refresh_btn)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        self.setLayout(layout)
        
        # Don't do initial refresh - let timer handle it
        
    def refresh_topics(self):
        """Refresh the list of available topics - NON-BLOCKING using async"""
        if self.async_ros2_manager:
            # Use async manager - callback when data ready
            self.async_ros2_manager.get_topics_async(self.update_topics_data)
        else:
            # Fallback: sync call with error handling
            try:
                topics_info = self.ros2_manager.get_topics_info()
                self.update_topics_data(topics_info)
            except Exception as e:
                print(f"Error refreshing topics: {e}")
                self.topic_count_label.setText(f"Topics: 0 (Error: ROS2 may not be running)")
            
    def on_topic_selected(self, topic_name, state):
        """Handle topic selection change"""
        if state == Qt.Checked:
            self.selected_topics.add(topic_name)
        else:
            self.selected_topics.discard(topic_name)
            
        self.topic_selected.emit(topic_name, state == Qt.Checked)
        # Also emit list of all selected topics
        self.topics_changed.emit(list(self.selected_topics))
        
    def select_all_topics(self):
        """Select all topics for recording"""
        for row in range(self.topics_table.rowCount()):
            checkbox_widget = self.topics_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(True)
                    
    def deselect_all_topics(self):
        """Deselect all topics"""
        for row in range(self.topics_table.rowCount()):
            checkbox_widget = self.topics_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(False)
                    
    def get_selected_topics(self):
        """Get list of selected topics"""
        return list(self.selected_topics)
        
    def set_selected_topics(self, topics):
        """Set selected topics from a list"""
        self.selected_topics = set(topics)
        self.refresh_topics()
        
    def clear_selection(self):
        """Clear all topic selections"""
        self.selected_topics.clear()
        self.refresh_topics()
    
    def update_topics_data(self, topics_info):
        """
        Update topics from async data - WORLD-CLASS PERFORMANCE.
        This method is called from background thread with pre-fetched data.
        """
        try:
            self.topics_table.setRowCount(len(topics_info))
            self.topic_count_label.setText(f"Topics: {len(topics_info)}")
            
            for idx, topic_info in enumerate(topics_info):
                # Checkbox for recording selection
                checkbox = QCheckBox()
                checkbox.setChecked(topic_info['name'] in self.selected_topics)
                checkbox.stateChanged.connect(
                    lambda state, name=topic_info['name']: self.on_topic_selected(name, state)
                )
                
                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_widget)
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(Qt.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                
                self.topics_table.setCellWidget(idx, 0, checkbox_widget)
                
                # Topic name
                name_item = QTableWidgetItem(topic_info['name'])
                self.topics_table.setItem(idx, 1, name_item)
                
                # Message type
                msg_type_item = QTableWidgetItem(topic_info.get('type', 'Unknown'))
                self.topics_table.setItem(idx, 2, msg_type_item)
                
                # Publisher count
                pub_count = topic_info.get('publisher_count', 0)
                pub_item = QTableWidgetItem(str(pub_count))
                pub_item.setTextAlignment(Qt.AlignCenter)
                
                # Color code based on publisher count
                if pub_count > 0:
                    pub_item.setForeground(QColor('green'))
                else:
                    pub_item.setForeground(QColor('gray'))
                    
                self.topics_table.setItem(idx, 3, pub_item)
                
                # Frequency
                hz = topic_info.get('hz', 0.0)
                hz_item = QTableWidgetItem(f"{hz:.1f}")
                hz_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.topics_table.setItem(idx, 4, hz_item)
            
        except Exception as e:
            print(f"Error updating topics data: {e}")
            self.topic_count_label.setText(f"Topics: 0 (Error)")

