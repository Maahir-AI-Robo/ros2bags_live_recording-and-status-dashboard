#!/usr/bin/env python3
"""
ROS2 Bags Recording and Live Status Dashboard
Main entry point for the application
"""

import sys
from PyQt5.QtWidgets import QApplication  # type: ignore
from PyQt5.QtCore import Qt  # type: ignore
from gui.main_window import MainWindow  # type: ignore


def main():
    """Main application entry point"""
    # Enable High DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # type: ignore
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # type: ignore
    
    app = QApplication(sys.argv)
    app.setApplicationName("ROS2 Dashboard")
    app.setOrganizationName("ROS2 Monitoring")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
