"""
Service Monitor Widget - displays ROS2 services
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,  # type: ignore
                             QTableWidgetItem, QPushButton, QGroupBox, QHeaderView,
                             QLabel)
from PyQt5.QtCore import Qt  # type: ignore
from PyQt5.QtGui import QColor  # type: ignore
from PyQt5.QtGui import QColor


class ServiceMonitorWidget(QWidget):
    """Widget for monitoring ROS2 services"""
    
    def __init__(self, ros2_manager, async_ros2_manager=None):
        super().__init__()
        self.ros2_manager = ros2_manager
        self.async_ros2_manager = async_ros2_manager  # NEW: optional async manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Group box
        group = QGroupBox("ROS2 Services")
        group_layout = QVBoxLayout()
        
        # Info label
        info_layout = QHBoxLayout()
        self.service_count_label = QLabel("Services: 0")
        info_layout.addWidget(self.service_count_label)
        info_layout.addStretch()
        
        refresh_btn = QPushButton("Refresh Services")
        refresh_btn.clicked.connect(self.refresh_services)
        info_layout.addWidget(refresh_btn)
        
        group_layout.addLayout(info_layout)
        
        # Services table
        self.services_table = QTableWidget()
        self.services_table.setColumnCount(3)
        self.services_table.setHorizontalHeaderLabels([
            "Service Name", "Service Type", "Servers"
        ])
        
        header = self.services_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        group_layout.addWidget(self.services_table)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        self.setLayout(layout)
        
    def refresh_services(self):
        """Refresh the list of ROS2 services - NON-BLOCKING using async"""
        if self.async_ros2_manager:
            # Use async manager - callback when data ready
            self.async_ros2_manager.get_services_async(self.update_services_data)
        else:
            # Fallback: sync call with error handling
            try:
                services_info = self.ros2_manager.get_services_info()
                self.update_services_data(services_info)
            except Exception as e:
                print(f"Error refreshing services: {e}")
                self.service_count_label.setText("Services: 0 (Error)")

    def update_services_data(self, services_info):
        """Update services from async data - HIGH PERFORMANCE"""
        try:
            self.services_table.setRowCount(len(services_info))
            self.service_count_label.setText(f"Services: {len(services_info)}")
            
            for idx, service_info in enumerate(services_info):
                name_item = QTableWidgetItem(service_info['name'])
                self.services_table.setItem(idx, 0, name_item)
                
                type_item = QTableWidgetItem(service_info.get('type', 'Unknown'))
                self.services_table.setItem(idx, 1, type_item)
                
                server_item = QTableWidgetItem(str(service_info.get('server_count', 1)))
                server_item.setTextAlignment(Qt.AlignCenter)
                self.services_table.setItem(idx, 2, server_item)
                
        except Exception as e:
            print(f"Error updating services data: {e}")
