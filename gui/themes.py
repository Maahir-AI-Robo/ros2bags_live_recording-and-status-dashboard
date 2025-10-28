"""
Theme Management - Dark/Light theme support
"""

DARK_THEME = """
QMainWindow, QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

QGroupBox {
    border: 1px solid #404040;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
    color: #e0e0e0;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

QPushButton {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 6px 12px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #3d3d3d;
    border: 1px solid #505050;
}

QPushButton:pressed {
    background-color: #1a1a1a;
}

QPushButton:disabled {
    background-color: #252525;
    color: #606060;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #252525;
    color: #e0e0e0;
    border: 1px solid #404040;
    border-radius: 3px;
    padding: 4px;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #2196F3;
}

QComboBox {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
    border-radius: 3px;
    padding: 4px;
}

QComboBox:hover {
    border: 1px solid #505050;
}

QComboBox::drop-down {
    border: none;
}

QTableWidget {
    background-color: #1e1e1e;
    alternate-background-color: #252525;
    color: #e0e0e0;
    gridline-color: #404040;
    border: 1px solid #404040;
}

QTableWidget::item {
    padding: 4px;
}

QTableWidget::item:selected {
    background-color: #2196F3;
    color: white;
}

QHeaderView::section {
    background-color: #2d2d2d;
    color: #e0e0e0;
    padding: 6px;
    border: 1px solid #404040;
    font-weight: bold;
}

QTabWidget::pane {
    border: 1px solid #404040;
    background-color: #1e1e1e;
}

QTabBar::tab {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #2196F3;
    color: white;
}

QTabBar::tab:hover {
    background-color: #3d3d3d;
}

QProgressBar {
    border: 1px solid #404040;
    border-radius: 3px;
    text-align: center;
    background-color: #252525;
    color: #e0e0e0;
}

QProgressBar::chunk {
    background-color: #2196F3;
}

QCheckBox {
    color: #e0e0e0;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #404040;
    border-radius: 3px;
    background-color: #252525;
}

QCheckBox::indicator:checked {
    background-color: #2196F3;
    border-color: #2196F3;
}

QCheckBox::indicator:hover {
    border-color: #505050;
}

QLabel {
    color: #e0e0e0;
}

QStatusBar {
    background-color: #2d2d2d;
    color: #e0e0e0;
}

QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 12px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #404040;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #505050;
}

QScrollBar:horizontal {
    background-color: #1e1e1e;
    height: 12px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #404040;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #505050;
}

QMenu {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
}

QMenu::item:selected {
    background-color: #2196F3;
}

QToolTip {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
    padding: 4px;
}
"""

LIGHT_THEME = """
QMainWindow, QWidget {
    background-color: #f5f5f5;
    color: #212121;
}

QGroupBox {
    border: 1px solid #bdbdbd;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
    color: #212121;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

QPushButton {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #bdbdbd;
    border-radius: 4px;
    padding: 6px 12px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #e0e0e0;
    border: 1px solid #9e9e9e;
}

QPushButton:pressed {
    background-color: #d0d0d0;
}

QPushButton:disabled {
    background-color: #fafafa;
    color: #9e9e9e;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #bdbdbd;
    border-radius: 3px;
    padding: 4px;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #2196F3;
}

QComboBox {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #bdbdbd;
    border-radius: 3px;
    padding: 4px;
}

QComboBox:hover {
    border: 1px solid #9e9e9e;
}

QComboBox::drop-down {
    border: none;
}

QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #fafafa;
    color: #212121;
    gridline-color: #e0e0e0;
    border: 1px solid #bdbdbd;
}

QTableWidget::item {
    padding: 4px;
}

QTableWidget::item:selected {
    background-color: #2196F3;
    color: white;
}

QHeaderView::section {
    background-color: #eeeeee;
    color: #212121;
    padding: 6px;
    border: 1px solid #bdbdbd;
    font-weight: bold;
}

QTabWidget::pane {
    border: 1px solid #bdbdbd;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #eeeeee;
    color: #212121;
    border: 1px solid #bdbdbd;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #2196F3;
    color: white;
}

QTabBar::tab:hover {
    background-color: #e0e0e0;
}

QProgressBar {
    border: 1px solid #bdbdbd;
    border-radius: 3px;
    text-align: center;
    background-color: #ffffff;
    color: #212121;
}

QProgressBar::chunk {
    background-color: #2196F3;
}

QCheckBox {
    color: #212121;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #bdbdbd;
    border-radius: 3px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #2196F3;
    border-color: #2196F3;
}

QCheckBox::indicator:hover {
    border-color: #9e9e9e;
}

QLabel {
    color: #212121;
}

QStatusBar {
    background-color: #eeeeee;
    color: #212121;
}

QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 12px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #bdbdbd;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #9e9e9e;
}

QScrollBar:horizontal {
    background-color: #f5f5f5;
    height: 12px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #bdbdbd;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #9e9e9e;
}

QMenu {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #bdbdbd;
}

QMenu::item:selected {
    background-color: #2196F3;
    color: white;
}

QToolTip {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #bdbdbd;
    padding: 4px;
}
"""


class ThemeManager:
    """Manages application themes"""
    
    THEMES = {
        'dark': DARK_THEME,
        'light': LIGHT_THEME
    }
    
    def __init__(self):
        self.current_theme = 'light'
        
    def get_theme(self, theme_name='light'):
        """Get theme stylesheet"""
        return self.THEMES.get(theme_name, LIGHT_THEME)
        
    def toggle_theme(self, app):
        """Toggle between dark and light theme"""
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        app.setStyleSheet(self.get_theme(self.current_theme))
        return self.current_theme
        
    def set_theme(self, app, theme_name):
        """Set specific theme"""
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            app.setStyleSheet(self.get_theme(theme_name))
            return True
        return False
