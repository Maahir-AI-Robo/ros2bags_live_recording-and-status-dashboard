"""
Recording Templates - Save and load recording configurations
"""

import json
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QListWidget, QInputDialog, QMessageBox,
                             QGroupBox, QTextEdit)
from PyQt5.QtCore import pyqtSignal
from datetime import datetime


class RecordingTemplate:
    """Represents a recording configuration template"""
    
    def __init__(self, name="New Template"):
        self.name = name
        self.output_dir = ""
        self.bag_name_prefix = ""
        self.selected_topics = []
        self.record_all_topics = True
        self.compression_enabled = False
        self.max_bag_size_mb = 0
        self.max_bag_duration_sec = 0
        self.created_at = datetime.now().isoformat()
        self.description = ""
        
    def to_dict(self):
        """Convert to dictionary for JSON storage"""
        return {
            'name': self.name,
            'output_dir': self.output_dir,
            'bag_name_prefix': self.bag_name_prefix,
            'selected_topics': self.selected_topics,
            'record_all_topics': self.record_all_topics,
            'compression_enabled': self.compression_enabled,
            'max_bag_size_mb': self.max_bag_size_mb,
            'max_bag_duration_sec': self.max_bag_duration_sec,
            'created_at': self.created_at,
            'description': self.description
        }
        
    @staticmethod
    def from_dict(data):
        """Create from dictionary"""
        template = RecordingTemplate(data.get('name', 'Unnamed'))
        template.output_dir = data.get('output_dir', '')
        template.bag_name_prefix = data.get('bag_name_prefix', '')
        template.selected_topics = data.get('selected_topics', [])
        template.record_all_topics = data.get('record_all_topics', True)
        template.compression_enabled = data.get('compression_enabled', False)
        template.max_bag_size_mb = data.get('max_bag_size_mb', 0)
        template.max_bag_duration_sec = data.get('max_bag_duration_sec', 0)
        template.created_at = data.get('created_at', datetime.now().isoformat())
        template.description = data.get('description', '')
        return template


class RecordingTemplatesWidget(QWidget):
    """Widget for managing recording templates"""
    
    template_loaded = pyqtSignal(object)  # Emits RecordingTemplate when loaded
    
    def __init__(self, recording_control, topic_monitor):
        super().__init__()
        self.recording_control = recording_control
        self.topic_monitor = topic_monitor
        self.templates_dir = os.path.expanduser("~/.ros2_dashboard/templates")
        
        # Create templates directory if it doesn't exist
        os.makedirs(self.templates_dir, exist_ok=True)
        
        self.init_ui()
        self.load_templates_list()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Recording Templates")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Templates list
        list_group = QGroupBox("Saved Templates")
        list_layout = QVBoxLayout()
        
        self.templates_list = QListWidget()
        self.templates_list.itemDoubleClicked.connect(self.load_selected_template)
        list_layout.addWidget(self.templates_list)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Save Current as Template")
        self.save_btn.clicked.connect(self.save_current_configuration)
        button_layout.addWidget(self.save_btn)
        
        self.load_btn = QPushButton("📂 Load Template")
        self.load_btn.clicked.connect(self.load_selected_template)
        button_layout.addWidget(self.load_btn)
        
        self.delete_btn = QPushButton("🗑 Delete Template")
        self.delete_btn.clicked.connect(self.delete_template)
        button_layout.addWidget(self.delete_btn)
        
        layout.addLayout(button_layout)
        
        # Template info
        info_group = QGroupBox("Template Info")
        info_layout = QVBoxLayout()
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        info_layout.addWidget(self.info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Connect selection changed
        self.templates_list.currentItemChanged.connect(self.show_template_info)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def get_current_configuration(self):
        """Get current recording configuration"""
        template = RecordingTemplate()
        
        # Get from recording control widget
        template.output_dir = self.recording_control.output_dir_edit.text()
        template.bag_name_prefix = self.recording_control.bag_name_edit.text()
        
        # Get selected topics from topic monitor
        template.selected_topics = self.topic_monitor.get_selected_topics()
        template.record_all_topics = len(template.selected_topics) == 0
        
        return template
        
    def save_current_configuration(self):
        """Save current configuration as template"""
        name, ok = QInputDialog.getText(
            self,
            "Save Template",
            "Template name:",
            text=f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if not ok or not name:
            return
            
        description, ok = QInputDialog.getMultiLineText(
            self,
            "Template Description",
            "Description (optional):",
            ""
        )
        
        template = self.get_current_configuration()
        template.name = name
        template.description = description if ok else ""
        
        # Save to file
        filename = os.path.join(self.templates_dir, f"{name}.json")
        
        try:
            with open(filename, 'w') as f:
                json.dump(template.to_dict(), f, indent=2)
                
            QMessageBox.information(
                self,
                "Template Saved",
                f"Template '{name}' saved successfully!"
            )
            
            self.load_templates_list()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Failed",
                f"Failed to save template:\n{str(e)}"
            )
            
    def load_templates_list(self):
        """Load list of available templates"""
        self.templates_list.clear()
        
        try:
            files = [f for f in os.listdir(self.templates_dir) if f.endswith('.json')]
            for filename in sorted(files):
                name = filename[:-5]  # Remove .json extension
                self.templates_list.addItem(name)
                
        except Exception as e:
            print(f"Error loading templates: {e}")
            
    def load_selected_template(self):
        """Load the selected template"""
        current_item = self.templates_list.currentItem()
        
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a template to load.")
            return
            
        template_name = current_item.text()
        filename = os.path.join(self.templates_dir, f"{template_name}.json")
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            template = RecordingTemplate.from_dict(data)
            
            # Apply template to recording control
            self.recording_control.output_dir_edit.setText(template.output_dir)
            self.recording_control.bag_name_edit.setText(template.bag_name_prefix)
            
            # Apply topic selection
            if template.record_all_topics:
                self.topic_monitor.clear_selection()
            else:
                self.topic_monitor.set_selected_topics(template.selected_topics)
                
            self.template_loaded.emit(template)
            
            QMessageBox.information(
                self,
                "Template Loaded",
                f"Template '{template_name}' loaded successfully!"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Load Failed",
                f"Failed to load template:\n{str(e)}"
            )
            
    def delete_template(self):
        """Delete the selected template"""
        current_item = self.templates_list.currentItem()
        
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a template to delete.")
            return
            
        template_name = current_item.text()
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete template '{template_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            filename = os.path.join(self.templates_dir, f"{template_name}.json")
            
            try:
                os.remove(filename)
                self.load_templates_list()
                self.info_text.clear()
                
                QMessageBox.information(
                    self,
                    "Template Deleted",
                    f"Template '{template_name}' deleted successfully!"
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Delete Failed",
                    f"Failed to delete template:\n{str(e)}"
                )
                
    def show_template_info(self, current, previous):
        """Show information about selected template"""
        if not current:
            self.info_text.clear()
            return
            
        template_name = current.text()
        filename = os.path.join(self.templates_dir, f"{template_name}.json")
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            template = RecordingTemplate.from_dict(data)
            
            info = f"""<b>Name:</b> {template.name}<br>
<b>Created:</b> {template.created_at[:19]}<br>
<b>Output Directory:</b> {template.output_dir}<br>
<b>Bag Prefix:</b> {template.bag_name_prefix}<br>
<b>Record All Topics:</b> {template.record_all_topics}<br>
<b>Selected Topics:</b> {len(template.selected_topics)}<br>
<b>Description:</b> {template.description if template.description else '<i>No description</i>'}
"""
            
            if not template.record_all_topics and template.selected_topics:
                info += f"<br><b>Topics:</b><br>"
                for topic in template.selected_topics[:10]:  # Show first 10
                    info += f"  • {topic}<br>"
                if len(template.selected_topics) > 10:
                    info += f"  ... and {len(template.selected_topics) - 10} more"
                    
            self.info_text.setHtml(info)
            
        except Exception as e:
            self.info_text.setPlainText(f"Error loading template info: {e}")
