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
    /* Main Application */
    QMainWindow {
        background-color: #1e1e1e;
        color: #e0e0e0;
    }
    
    /* Toolbar */
    QToolBar {
        background-color: #2d2d2d;
        border: none;
        spacing: 8px;
        padding: 4px;
    }
    
    QToolButton {
        background-color: #3a3a3a;
        border: 1px solid #4a4a4a;
        border-radius: 6px;
        padding: 8px 16px;
        color: #e0e0e0;
        font-weight: 500;
    }
    
    QToolButton:hover {
        background-color: #4a4a4a;
        border-color: #5a5a5a;
    }
    
    QToolButton:pressed {
        background-color: #333333;
    }
    
    /* Buttons */
    QPushButton {
        background-color: #3a3a3a;
        border: 1px solid #4a4a4a;
        border-radius: 6px;
        padding: 8px 16px;
        color: #e0e0e0;
        font-weight: 500;
        min-height: 24px;
    }
    
    QPushButton:hover {
        background-color: #4a4a4a;
        border-color: #5a5a5a;
    }
    
    QPushButton:pressed {
        background-color: #333333;
    }
    
    QPushButton:disabled {
        background-color: #2a2a2a;
        color: #666666;
    }
    
    /* Primary buttons */
    QPushButton#primaryButton {
        background-color: #0d7377;
        border-color: #0f9398;
    }
    
    QPushButton#primaryButton:hover {
        background-color: #0f9398;
    }
    
    /* Scrollbars */
    QScrollBar:vertical {
        background-color: #2d2d2d;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #4a4a4a;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #5a5a5a;
    }
    
    QScrollBar:horizontal {
        background-color: #2d2d2d;
        height: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #4a4a4a;
        border-radius: 6px;
        min-width: 20px;
    }
    
    /* List/Grid Views */
    QListWidget, QTableWidget, QTreeWidget {
        background-color: #252525;
        border: 1px solid #3a3a3a;
        border-radius: 8px;
        padding: 4px;
        outline: none;
    }
    
    QListWidget::item, QTableWidget::item, QTreeWidget::item {
        padding: 8px;
        border-radius: 4px;
    }
    
    QListWidget::item:hover, QTableWidget::item:hover, QTreeWidget::item:hover {
        background-color: #2d2d2d;
    }
    
    QListWidget::item:selected, QTableWidget::item:selected, QTreeWidget::item:selected {
        background-color: #0d7377;
        color: #ffffff;
    }
    
    /* Labels */
    QLabel {
        color: #e0e0e0;
        background-color: transparent;
    }
    
    /* Line Edits */
    QLineEdit, QTextEdit {
        background-color: #2d2d2d;
        border: 1px solid #4a4a4a;
        border-radius: 6px;
        padding: 6px;
        color: #e0e0e0;
        selection-background-color: #0d7377;
    }
    
    QLineEdit:focus, QTextEdit:focus {
        border-color: #0f9398;
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
