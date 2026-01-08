"""
Dark theme stylesheet for Capture - GNOME-native aesthetics.
"""


def get_dark_theme() -> str:
    """
    Get dark theme stylesheet for PyQt6.
    
    Returns:
        CSS stylesheet string
    """
    return """
    /* Main Window */
    QMainWindow {
        background-color: #2b2b2b;
        color: #e0e0e0;
    }
    
    /* Widgets */
    QWidget {
        background-color: #2b2b2b;
        color: #e0e0e0;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 10pt;
    }
    
    /* Message Boxes and Dialogs */
    QMessageBox {
        background-color: #2b2b2b;
        color: #e0e0e0;
    }
    
    QMessageBox QLabel {
        background-color: transparent;
        color: #e0e0e0;
        padding: 10px;
        font-size: 10pt;
    }
    
    QMessageBox QPushButton {
        background-color: #3a3a3a;
        color: #e0e0e0;
        border: 1px solid #4a4a4a;
        border-radius: 4px;
        padding: 6px 20px;
        min-width: 80px;
        font-weight: bold;
    }
    
    QMessageBox QPushButton:hover {
        background-color: #00BFA5;
        border-color: #00BFA5;
    }
    
    QMessageBox QPushButton:pressed {
        background-color: #009688;
    }
    
    /* File Dialogs */
    QFileDialog {
        background-color: #2b2b2b;
        color: #e0e0e0;
    }
    
    QFileDialog QListView,
    QFileDialog QTreeView,
    QFileDialog QTableView {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border: 1px solid #3a3a3a;
    }
    
    /* Context Menus */
    QMenu {
        background-color: #2b2b2b;
        color: #e0e0e0;
        border: 1px solid #3a3a3a;
        padding: 4px;
    }
    
    QMenu::item {
        background-color: transparent;
        padding: 8px 30px 8px 20px;
        border-radius: 4px;
    }
    
    QMenu::item:selected {
        background-color: #00BFA5;
        color: #ffffff;
    }
    
    QMenu::separator {
        height: 1px;
        background-color: #3a3a3a;
        margin: 4px 10px;
    }
    
    /* Input Dialogs */
    QInputDialog {
        background-color: #2b2b2b;
        color: #e0e0e0;
    }
    
    QInputDialog QLineEdit {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        padding: 6px;
    }
    
    /* Buttons */
    QPushButton {
        background-color: #3a3a3a;
        color: #e0e0e0;
        border: 1px solid #4a4a4a;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #4a4a4a;
        border-color: #00BFA5;
    }
    
    QPushButton:pressed {
        background-color: #00BFA5;
        color: #ffffff;
    }
    
    QPushButton:disabled {
        background-color: #2b2b2b;
        color: #5a5a5a;
        border-color: #3a3a3a;
    }
    
    /* Labels */
    QLabel {
        background-color: transparent;
        color: #e0e0e0;
    }
    
    /* List Widgets */
    QListWidget {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border: 1px solid #3a3a3a;
        border-radius: 8px;
        padding: 8px;
    }
    
    QListWidget::item {
        padding: 8px;
        border-radius: 4px;
    }
    
    QListWidget::item:selected {
        background-color: #00BFA5;
        color: #ffffff;
    }
    
    QListWidget::item:hover {
        background-color: #3a3a3a;
    }
    
    /* Toolbar */
    QToolBar {
        background-color: #2b2b2b;
        border: none;
        padding: 4px;
        spacing: 8px;
    }
    
    QToolBar QAction {
        color: #e0e0e0;
        padding: 6px 12px;
    }
    
    /* Status Bar */
    QStatusBar {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border-top: 1px solid #3a3a3a;
    }
    
    /* Line Edit */
    QLineEdit {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        padding: 6px;
    }
    
    QLineEdit:focus {
        border-color: #00BFA5;
    }
    
    /* Sliders */
    QSlider::groove:horizontal {
        background-color: #3a3a3a;
        height: 6px;
        border-radius: 3px;
    }
    
    QSlider::handle:horizontal {
        background-color: #00BFA5;
        width: 16px;
        height: 16px;
        margin: -5px 0;
        border-radius: 8px;
    }
    
    QSlider::handle:horizontal:hover {
        background-color: #00E5BF;
    }
    
    /* Group Box */
    QGroupBox {
        color: #e0e0e0;
        border: 1px solid #3a3a3a;
        border-radius: 6px;
        margin-top: 12px;
        padding-top: 12px;
        font-weight: bold;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }
    
    /* Combo Box */
    QComboBox {
        background-color: #2d2d2d;
        border: 1px solid #4a4a4a;
        border-radius: 6px;
        padding: 6px;
        color: #e0e0e0;
    }
    
    QComboBox:hover {
        border-color: #5a5a5a;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    
    QComboBox QAbstractItemView {
        background-color: #2d2d2d;
        border: 1px solid #4a4a4a;
        selection-background-color: #0d7377;
    }
    
    /* Status Bar */
    QStatusBar {
        background-color: #2d2d2d;
        color: #a0a0a0;
        border-top: 1px solid #3a3a3a;
    }
    
    /* Menu Bar */
    QMenuBar {
        background-color: #2d2d2d;
        color: #e0e0e0;
    }
    
    QMenuBar::item:selected {
        background-color: #3a3a3a;
    }
    
    QMenu {
        background-color: #2d2d2d;
        border: 1px solid #3a3a3a;
        color: #e0e0e0;
    }
    
    QMenu::item:selected {
        background-color: #0d7377;
    }
    
    /* Splitter */
    QSplitter::handle {
        background-color: #3a3a3a;
    }
    
    QSplitter::handle:hover {
        background-color: #4a4a4a;
    }
    
    /* Progress Bar */
    QProgressBar {
        background-color: #2d2d2d;
        border: 1px solid #4a4a4a;
        border-radius: 6px;
        text-align: center;
    }
    
    QProgressBar::chunk {
        background-color: #0d7377;
        border-radius: 6px;
    }
    
    /* Tab Widget */
    QTabWidget::pane {
        border: 1px solid #3a3a3a;
        background-color: #252525;
    }
    
    QTabBar::tab {
        background-color: #2d2d2d;
        border: 1px solid #3a3a3a;
        padding: 8px 16px;
        margin-right: 2px;
    }
    
    QTabBar::tab:selected {
        background-color: #0d7377;
        color: #ffffff;
    }
    
    QTabBar::tab:hover {
        background-color: #3a3a3a;
    }
    """
