"""
Node Monitor Widget - displays ROS2 nodes and their information
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,  # type: ignore
                             QTableWidgetItem, QPushButton, QGroupBox, QHeaderView,
                             QLabel)
from PyQt5.QtCore import Qt  # type: ignore
from PyQt5.QtGui import QColor  # type: ignore


class NodeMonitorWidget(QWidget):
    """Widget for monitoring ROS2 nodes"""
    
    def __init__(self, ros2_manager):
        super().__init__()
        self.ros2_manager = ros2_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Group box
        group = QGroupBox("ROS2 Nodes")
        group_layout = QVBoxLayout()
        
        # Info label
        info_layout = QHBoxLayout()
        self.node_count_label = QLabel("Nodes: 0")
        info_layout.addWidget(self.node_count_label)
        info_layout.addStretch()
        
        refresh_btn = QPushButton("Refresh Nodes")
        refresh_btn.clicked.connect(self.refresh_nodes)
        info_layout.addWidget(refresh_btn)
        
        group_layout.addLayout(info_layout)
        
        # Nodes table
        self.nodes_table = QTableWidget()
        self.nodes_table.setColumnCount(4)
        self.nodes_table.setHorizontalHeaderLabels([
            "Node Name", "Namespace", "Publishers", "Subscribers"
        ])
        
        header = self.nodes_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        group_layout.addWidget(self.nodes_table)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        self.setLayout(layout)
        
    def refresh_nodes(self):
        """Refresh the list of ROS2 nodes"""
        try:
            nodes_info = self.ros2_manager.get_nodes_info()
            
            self.nodes_table.setRowCount(len(nodes_info))
            self.node_count_label.setText(f"Nodes: {len(nodes_info)}")
            
            for idx, node_info in enumerate(nodes_info):
                # Node name
                name_item = QTableWidgetItem(node_info['name'])
                self.nodes_table.setItem(idx, 0, name_item)
                
                # Namespace
                namespace_item = QTableWidgetItem(node_info.get('namespace', '/'))
                self.nodes_table.setItem(idx, 1, namespace_item)
                
                # Publishers
                pub_count = node_info.get('publishers', 0)
                pub_item = QTableWidgetItem(str(pub_count))
                pub_item.setTextAlignment(Qt.AlignCenter)
                if pub_count > 0:
                    pub_item.setForeground(QColor('green'))
                self.nodes_table.setItem(idx, 2, pub_item)
                
                # Subscribers
                sub_count = node_info.get('subscribers', 0)
                sub_item = QTableWidgetItem(str(sub_count))
                sub_item.setTextAlignment(Qt.AlignCenter)
                if sub_count > 0:
                    sub_item.setForeground(QColor('blue'))
                self.nodes_table.setItem(idx, 3, sub_item)
                
        except Exception as e:
            print(f"Error refreshing nodes: {e}")
            self.node_count_label.setText("Nodes: 0 (Error)")

    def update_nodes_data(self, nodes_info):
        """Update nodes from async data - HIGH PERFORMANCE"""
        try:
            self.nodes_table.setRowCount(len(nodes_info))
            self.node_count_label.setText(f"Nodes: {len(nodes_info)}")
            
            for idx, node_info in enumerate(nodes_info):
                name_item = QTableWidgetItem(node_info['name'])
                self.nodes_table.setItem(idx, 0, name_item)
                
                full_name_item = QTableWidgetItem(node_info['full_name'])
                self.nodes_table.setItem(idx, 1, full_name_item)
                
                namespace_item = QTableWidgetItem(node_info['namespace'])
                self.nodes_table.setItem(idx, 2, namespace_item)
                
                pub_item = QTableWidgetItem(str(node_info.get('publishers', 0)))
                pub_item.setTextAlignment(Qt.AlignCenter)
                self.nodes_table.setItem(idx, 3, pub_item)
                
                sub_item = QTableWidgetItem(str(node_info.get('subscribers', 0)))
                sub_item.setTextAlignment(Qt.AlignCenter)
                self.nodes_table.setItem(idx, 4, sub_item)
                
        except Exception as e:
            print(f"Error updating nodes data: {e}")
