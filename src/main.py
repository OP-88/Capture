"""
Capture - Screenshot Enhancement Tool
Main application entry point.
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from src.gui.main_window import MainWindow


def main():
    """Main application entry point."""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Capture")
    app.setOrganizationName("OP-88")
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
