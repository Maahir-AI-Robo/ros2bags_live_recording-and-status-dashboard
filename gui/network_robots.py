"""
Network Robots Widget - Display discovered ROS2 robots on the network
"""

from PyQt5.QtWidgets import (  # type: ignore
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QComboBox,
    QHeaderView, QProgressBar, QTextEdit, QSplitter, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal  # type: ignore
from PyQt5.QtGui import QFont, QColor  # type: ignore
from core.network_discovery import NetworkRobotDiscovery  # type: ignore
from datetime import datetime


class NetworkRobotsWidget(QWidget):
    """Widget for discovering and displaying robots on the network"""
    
    robot_selected = pyqtSignal(str, list)  # hostname, topics
    
    def __init__(self):
        super().__init__()
        self.discovery = NetworkRobotDiscovery()
        self.auto_refresh = False
        self.failed_robots = {}  # Track failed discovery attempts
        self.retry_attempts = {}  # Track retry count per robot
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        # Control panel
        controls = self.create_controls()
        layout.addWidget(controls)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Robots table
        robots_group = QGroupBox("Discovered Robots")
        robots_layout = QVBoxLayout()
        
        self.robots_table = QTableWidget()
        self.robots_table.setColumnCount(6)
        self.robots_table.setHorizontalHeaderLabels([
            'Robot/Host', 'Nodes', 'Topics', 'Services', 'Sensors', 'Last Seen'
        ])
        self.robots_table.horizontalHeader().setStretchLastSection(True)
        self.robots_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.robots_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.robots_table.itemSelectionChanged.connect(self.on_robot_selected)
        
        robots_layout.addWidget(self.robots_table)
        robots_group.setLayout(robots_layout)
        splitter.addWidget(robots_group)
        
        # Right: Robot details
        details_group = QGroupBox("Robot Details")
        details_layout = QVBoxLayout()
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setPlaceholderText("Select a robot to view details...")
        details_layout.addWidget(self.details_text)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        
        record_btn = QPushButton("📹 Record All Topics")
        record_btn.clicked.connect(self.record_robot_topics)
        actions_layout.addWidget(record_btn)
        
        export_btn = QPushButton("📤 Export Robot Info")
        export_btn.clicked.connect(self.export_robot_info)
        actions_layout.addWidget(export_btn)
        
        details_layout.addLayout(actions_layout)
        
        details_group.setLayout(details_layout)
        splitter.addWidget(details_group)
        
        splitter.setSizes([400, 300])
        layout.addWidget(splitter)
        
        # Status bar
        self.status_label = QLabel("Ready to discover robots")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def create_controls(self):
        """Create control panel"""
        group = QGroupBox("Network Discovery")
        layout = QVBoxLayout()
        
        # Domain selection
        domain_layout = QHBoxLayout()
        domain_layout.addWidget(QLabel("ROS Domain ID:"))
        
        self.domain_spin = QComboBox()
        self.domain_spin.addItems([str(i) for i in range(0, 11)])
        self.domain_spin.setCurrentText(str(self.discovery.current_domain))
        self.domain_spin.currentTextChanged.connect(self.on_domain_changed)
        domain_layout.addWidget(self.domain_spin)
        
        domain_layout.addWidget(QLabel("  "))
        
        scan_domains_btn = QPushButton("🔍 Scan All Domains")
        scan_domains_btn.clicked.connect(self.scan_all_domains)
        domain_layout.addWidget(scan_domains_btn)
        
        domain_layout.addStretch()
        layout.addLayout(domain_layout)
        
        # Discovery controls
        controls_layout = QHBoxLayout()
        
        discover_btn = QPushButton("🔄 Discover Robots")
        discover_btn.clicked.connect(self.discover_robots)
        discover_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        controls_layout.addWidget(discover_btn)
        
        self.auto_refresh_check = QCheckBox("Auto-refresh (every 10s)")
        self.auto_refresh_check.stateChanged.connect(self.toggle_auto_refresh)
        controls_layout.addWidget(self.auto_refresh_check)
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self.clear_results)
        controls_layout.addWidget(clear_btn)
        
        retry_btn = QPushButton("🔁 Retry Failed")
        retry_btn.clicked.connect(self.retry_failed_robots)
        controls_layout.addWidget(retry_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)
        
        group.setLayout(layout)
        return group
    
    def on_domain_changed(self, domain_str):
        """Handle domain ID change"""
        try:
            domain_id = int(domain_str)
            self.discovery.set_domain(domain_id)
            self.status_label.setText(f"Switched to ROS_DOMAIN_ID={domain_id}")
        except:
            pass
    
    def discover_robots(self):
        """Discover robots on the network"""
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)  # Indeterminate
        self.status_label.setText("Discovering robots on the network...")
        
        try:
            # Perform discovery
            robots = self.discovery.discover_network_robots()
            
            # Update table
            self.update_robots_table(robots)
            
            # Count successful vs failed
            success_count = len(robots)
            failed_count = len(self.failed_robots)
            
            if failed_count == 0:
                self.status_label.setText(f"✅ Found {success_count} robot(s) on domain {self.discovery.current_domain}")
            else:
                self.status_label.setText(f"✅ Found {success_count} robot(s), ❌ {failed_count} unreachable - Click 'Retry Failed' to reconnect")
            
        except Exception as e:
            self.status_label.setText(f"❌ Discovery failed: {str(e)}")
        finally:
            self.progress.setVisible(False)
    
    def clear_results(self):
        """Clear discovery results"""
        self.robots_table.setRowCount(0)
        self.details_text.clear()
        self.discovery.discovered_robots.clear()
        self.failed_robots.clear()
        self.retry_attempts.clear()
        self.status_label.setText("Results cleared")
    
    def retry_failed_robots(self):
        """Retry discovery for failed robots"""
        if not self.failed_robots:
            self.status_label.setText("No failed robots to retry")
            return
        
        self.status_label.setText(f"Retrying {len(self.failed_robots)} failed robots...")
        
        # Clear failed status to retry
        failed_list = list(self.failed_robots.keys())
        self.failed_robots.clear()
        
        # Re-run discovery
        try:
            robots = self.discovery.discover_network_robots()
            self.update_robots_table(robots)
            
            # Update retry counts
            for hostname in failed_list:
                if hostname in robots:
                    self.retry_attempts[hostname] = self.retry_attempts.get(hostname, 0) + 1
                    self.status_label.setText(f"✅ Recovered {hostname} (Retry #{self.retry_attempts[hostname]})")
                else:
                    self.failed_robots[hostname] = True
            
            if self.failed_robots:
                self.status_label.setText(f"⚠️ Still unable to reach {len(self.failed_robots)} robot(s)")
            else:
                self.status_label.setText(f"✅ All robots recovered!")
                
        except Exception as e:
            self.status_label.setText(f"❌ Retry failed: {str(e)}")
    
    def mark_robot_failed(self, hostname):
        """Mark a robot as failed discovery"""
        self.failed_robots[hostname] = True
        self.retry_attempts[hostname] = self.retry_attempts.get(hostname, 0) + 1
    
    def update_robots_table(self, robots):
        """Update the robots table with status indicators"""
        self.robots_table.setRowCount(0)
        
        # First add successful robots
        row = 0
        for hostname, robot in robots.items():
            self.robots_table.insertRow(row)
            
            # Robot/Host with status
            status_icon = "✅" if hostname not in self.failed_robots else "❌"
            host_text = f"{status_icon} {hostname}"
            host_item = QTableWidgetItem(host_text)
            host_item.setFont(QFont("", -1, QFont.Bold))
            
            # Color code success/failure
            if hostname not in self.failed_robots:
                host_item.setForeground(QColor('#4CAF50'))
            else:
                host_item.setForeground(QColor('#f44336'))
            
            self.robots_table.setItem(row, 0, host_item)
            
            # Nodes count
            nodes_item = QTableWidgetItem(str(len(robot.nodes)))
            nodes_item.setTextAlignment(Qt.AlignCenter)
            self.robots_table.setItem(row, 1, nodes_item)
            
            # Topics count
            topics_item = QTableWidgetItem(str(len(robot.topics)))
            topics_item.setTextAlignment(Qt.AlignCenter)
            self.robots_table.setItem(row, 2, topics_item)
            
            # Services count
            services_item = QTableWidgetItem(str(len(robot.services)))
            services_item.setTextAlignment(Qt.AlignCenter)
            self.robots_table.setItem(row, 3, services_item)
            
            # Sensors count
            sensors = self.discovery.get_robot_sensors(hostname)
            sensor_count = sum(len(topics) for topics in sensors.values())
            sensors_item = QTableWidgetItem(str(sensor_count))
            sensors_item.setTextAlignment(Qt.AlignCenter)
            if sensor_count > 0:
                sensors_item.setForeground(QColor('#4CAF50'))
            self.robots_table.setItem(row, 4, sensors_item)
            
            # Last seen
            last_seen = robot.last_seen.strftime('%H:%M:%S')
            time_item = QTableWidgetItem(last_seen)
            time_item.setTextAlignment(Qt.AlignCenter)
            self.robots_table.setItem(row, 5, time_item)
            
            row += 1
        
        # Then add failed robots
        for hostname in self.failed_robots.keys():
            self.robots_table.insertRow(row)
            
            # Robot/Host with failure status
            retry_count = self.retry_attempts.get(hostname, 0)
            host_text = f"❌ {hostname}"
            if retry_count > 0:
                host_text += f" (Retry #{retry_count})"
            
            host_item = QTableWidgetItem(host_text)
            host_item.setFont(QFont("", -1, QFont.Bold))
            host_item.setForeground(QColor('#f44336'))
            self.robots_table.setItem(row, 0, host_item)
            
            # Other cells show "Connection Failed"
            failed_msg = "Connection Failed"
            for col in range(1, 6):
                fail_item = QTableWidgetItem(failed_msg if col == 1 else "—")
                fail_item.setTextAlignment(Qt.AlignCenter)
                fail_item.setForeground(QColor('#999'))
                self.robots_table.setItem(row, col, fail_item)
            
            row += 1
        
        self.robots_table.resizeColumnsToContents()
    
    def on_robot_selected(self):
        """Handle robot selection"""
        selected_rows = self.robots_table.selectionModel().selectedRows()
        
        if not selected_rows:
            self.details_text.clear()
            return
        
        row = selected_rows[0].row()
        hostname = self.robots_table.item(row, 0).text()
        
        if hostname not in self.discovery.discovered_robots:
            return
        
        robot = self.discovery.discovered_robots[hostname]
        
        # Build details text
        details = f"🤖 Robot: {hostname}\n"
        details += f"{'='*60}\n\n"
        
        details += f"📡 Domain ID: {robot.domain_id}\n"
        details += f"🕐 Last Seen: {robot.last_seen.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Nodes
        details += f"📦 Nodes ({len(robot.nodes)}):\n"
        for node in robot.nodes[:10]:  # Show first 10
            details += f"  • {node}\n"
        if len(robot.nodes) > 10:
            details += f"  ... and {len(robot.nodes) - 10} more\n"
        details += "\n"
        
        # Sensors
        sensors = self.discovery.get_robot_sensors(hostname)
        if sensors:
            details += f"🔧 Sensors:\n"
            for sensor_type, topics in sensors.items():
                details += f"  {sensor_type.upper()} ({len(topics)}):\n"
                for topic in topics[:5]:  # Show first 5
                    details += f"    • {topic}\n"
                if len(topics) > 5:
                    details += f"    ... and {len(topics) - 5} more\n"
            details += "\n"
        
        # Topics
        details += f"📢 All Topics ({len(robot.topics)}):\n"
        for topic in robot.topics[:15]:  # Show first 15
            details += f"  • {topic}\n"
        if len(robot.topics) > 15:
            details += f"  ... and {len(robot.topics) - 15} more\n"
        details += "\n"
        
        # Services
        details += f"⚙️ Services ({len(robot.services)}):\n"
        for service in robot.services[:10]:  # Show first 10
            details += f"  • {service}\n"
        if len(robot.services) > 10:
            details += f"  ... and {len(robot.services) - 10} more\n"
        
        self.details_text.setPlainText(details)
        
        # Emit signal with selected robot topics
        self.robot_selected.emit(hostname, robot.topics)
    
    def record_robot_topics(self):
        """Record all topics from selected robot"""
        selected_rows = self.robots_table.selectionModel().selectedRows()
        
        if not selected_rows:
            self.status_label.setText("❌ No robot selected")
            return
        
        row = selected_rows[0].row()
        hostname = self.robots_table.item(row, 0).text()
        
        if hostname in self.discovery.discovered_robots:
            robot = self.discovery.discovered_robots[hostname]
            self.robot_selected.emit(hostname, robot.topics)
            self.status_label.setText(f"✅ Selected {len(robot.topics)} topics from {hostname}")
    
    def export_robot_info(self):
        """Export selected robot information"""
        selected_rows = self.robots_table.selectionModel().selectedRows()
        
        if not selected_rows:
            self.status_label.setText("❌ No robot selected")
            return
        
        row = selected_rows[0].row()
        hostname = self.robots_table.item(row, 0).text()
        
        if hostname in self.discovery.discovered_robots:
            robot = self.discovery.discovered_robots[hostname]
            
            # Export to JSON
            import json
            filename = f"robot_{hostname}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            robot_data = {
                'hostname': robot.hostname,
                'domain_id': robot.domain_id,
                'nodes': robot.nodes,
                'topics': robot.topics,
                'services': robot.services,
                'sensors': self.discovery.get_robot_sensors(hostname),
                'discovered_at': robot.last_seen.isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(robot_data, f, indent=2)
            
            self.status_label.setText(f"✅ Exported to {filename}")
    
    def scan_all_domains(self):
        """Scan all ROS2 domains"""
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.status_label.setText("Scanning domains 0-10...")
        
        try:
            results = self.discovery.scan_domains(0, 10)
            
            # Show results
            summary = "Domain Scan Results:\n\n"
            for domain_id, node_count in results.items():
                if node_count > 0:
                    summary += f"Domain {domain_id}: {node_count} nodes ✅\n"
            
            if all(count == 0 for count in results.values()):
                summary = "No active ROS2 nodes found on any domain (0-10)"
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Domain Scan Results", summary)
            
            self.status_label.setText("Domain scan complete")
            
        except Exception as e:
            self.status_label.setText(f"❌ Scan failed: {str(e)}")
        finally:
            self.progress.setVisible(False)
    
    def toggle_auto_refresh(self, state):
        """Toggle auto-refresh"""
        self.auto_refresh = (state == Qt.Checked)
        
        if self.auto_refresh:
            self.auto_refresh_timer = QTimer()
            self.auto_refresh_timer.timeout.connect(self.discover_robots)
            self.auto_refresh_timer.start(10000)  # Every 10 seconds
            self.status_label.setText("Auto-refresh enabled (10s interval)")
        else:
            if hasattr(self, 'auto_refresh_timer'):
                self.auto_refresh_timer.stop()
            self.status_label.setText("Auto-refresh disabled")
