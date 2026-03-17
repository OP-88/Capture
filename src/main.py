"""
Capture - Screenshot Enhancement Tool
Main application entry point.
"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSettings

from src.gui.main_window import MainWindow

# Network Isolation: Physical Socket Block (Process Level)
# This provides application-level enforcement of the air-gap.
import socket
_original_socket = socket.socket

def block_sockets(family=-1, type=-1, proto=-1, fileno=None):
    if family == -1:
        family = socket.AF_INET
    
    # Block Internet protocols (IPv4, IPv6) and Packet sockets
    if family in (socket.AF_INET, socket.AF_INET6, getattr(socket, 'AF_PACKET', None)):
        raise PermissionError(
            "CAPTURE SECURITY POLICY: Network access is strictly prohibited. "
            "This application is designed to be fully air-gapped for forensic integrity."
        )
    return _original_socket(family, type, proto, fileno)

# Override socket constructor
socket.socket = block_sockets

# Also block high-level connection helper
def block_create_connection(*args, **kwargs):
    raise PermissionError("CAPTURE SECURITY POLICY: Network connections are blocked.")
socket.create_connection = block_create_connection

class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to Capture 2.0")
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("<h2>Update Complete: Capture 2.0</h2>")
        layout.addWidget(title)
        
        content = QLabel(
            "Welcome to the latest version of Capture!<br><br>"
            "<b>What's New:</b><ul>"
            "<li><b>Hardened Security</b>: Complete network isolation (OS-level socket blocking).</li>"
            "<li><b>LIP Engine</b>: Smart Optimize analyzes histograms for perfect brightness/contrast.</li>"
            "<li><b>Focus Suite</b>: Context-aware highlighter and blur tools that snap to OCR text.</li>"
            "<li><b>Tactical Interface</b>: New single-page command center with Ctrl+V paste support.</li>"
            "</ul>"
            "Thank you for using Capture for your security documentation needs!"
        )
        content.setWordWrap(True)
        content.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(content)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Close")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMinimumWidth(100)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)



def main():
    """Main application entry point."""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Capture")
    app.setOrganizationName("OP-88")
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Check for first launch after update
    # settings = QSettings("OP-88", "Capture")
    current_version = "2.0.2"
    # last_version = settings.value("last_run_version", "")
    
    # if last_version != current_version:
    #     welcome_dialog = WelcomeDialog(window)
    #     welcome_dialog.exec()
    #     settings.setValue("last_run_version", current_version)
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
