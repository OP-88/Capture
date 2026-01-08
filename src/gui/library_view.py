"""
Library/Vault view for Capture.
Displays screenshot gallery in grid layout with thumbnails.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                              QListWidgetItem, QLabel, QPushButton, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QImage
from pathlib import Path
from typing import List, Optional
import cv2

from src.core.database import Screenshot


class LibraryView(QWidget):
    """Grid view gallery for screenshots."""
    
    # Signals
    screenshot_selected = pyqtSignal(int)  # Emits screenshot ID
    screenshot_double_clicked = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_screenshots: List[Screenshot] = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tags...")
        self.search_input.textChanged.connect(self.filter_screenshots)
        search_layout.addWidget(QLabel("🔍"))
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Grid view (using QListWidget in icon mode)
        self.grid_widget = QListWidget()
        self.grid_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.grid_widget.setIconSize(QSize(200, 200))
        self.grid_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.grid_widget.setSpacing(10)
        self.grid_widget.setMovement(QListWidget.Movement.Static)
        self.grid_widget.itemClicked.connect(self.on_item_clicked)
        self.grid_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.grid_widget)
        
        # Info label
        self.info_label = QLabel("No screenshots in library")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
    
    def load_screenshots(self, screenshots: List[Screenshot]):
        """
        Load screenshots into grid view.
        
        Args:
            screenshots: List of Screenshot objects
        """
        self.current_screenshots = screenshots
        self.grid_widget.clear()
        
        if not screenshots:
            self.info_label.setText("No screenshots in library")
            self.info_label.show()
            return
        
        self.info_label.hide()
        
        for screenshot in screenshots:
            self.add_screenshot_item(screenshot)
        
        self.update_info_label()
    
    def add_screenshot_item(self, screenshot: Screenshot):
        """
        Add screenshot item to grid.
        
        Args:
            screenshot: Screenshot object
        """
        # Create thumbnail
        thumbnail = self.create_thumbnail(screenshot.original_path)
        
        # Create list item
        item = QListWidgetItem()
        item.setIcon(thumbnail)
        
        # Set item text (filename + date)
        filename = Path(screenshot.original_path).name
        date_str = screenshot.import_date.strftime("%Y-%m-%d %H:%M")
        item.setText(f"{filename}\n{date_str}")
        
        # Store screenshot ID in item data
        item.setData(Qt.ItemDataRole.UserRole, screenshot.id)
        
        self.grid_widget.addItem(item)
    
    def create_thumbnail(self, image_path: str) -> QPixmap:
        """
        Create thumbnail from image path.
        
        Args:
            image_path: Path to image
            
        Returns:
            QPixmap thumbnail
        """
        try:
            # Load image with OpenCV
            img = cv2.imread(image_path)
            if img is None:
                return QPixmap()
            
            # Resize to thumbnail size
            height, width = img.shape[:2]
            max_size = 200
            
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            
            resized = cv2.resize(img, (new_width, new_height))
            
            # Convert to QPixmap
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            return QPixmap.fromImage(qt_image)
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return QPixmap()
    
    def on_item_clicked(self, item: QListWidgetItem):
        """Handle item click."""
        screenshot_id = item.data(Qt.ItemDataRole.UserRole)
        self.screenshot_selected.emit(screenshot_id)
    
    def on_item_double_clicked(self, item: QListWidgetItem):
        """Handle item double click."""
        screenshot_id = item.data(Qt.ItemDataRole.UserRole)
        self.screenshot_double_clicked.emit(screenshot_id)
    
    def filter_screenshots(self, search_text: str):
        """
        Filter screenshots by search text.
        
        Args:
            search_text: Search query
        """
        if not search_text:
            # Show all items
            for i in range(self.grid_widget.count()):
                self.grid_widget.item(i).setHidden(False)
            return
        
        search_lower = search_text.lower()
        
        for i in range(self.grid_widget.count()):
            item = self.grid_widget.item(i)
            item_text = item.text().lower()
            
            # Also check tags from screenshot object
            screenshot_id = item.data(Qt.ItemDataRole.UserRole)
            screenshot = next((s for s in self.current_screenshots if s.id == screenshot_id), None)
            
            match = search_lower in item_text
            if screenshot and screenshot.tags:
                match = match or search_lower in screenshot.tags.lower()
            
            item.setHidden(not match)
    
    def update_info_label(self):
        """Update info label with count."""
        count = len(self.current_screenshots)
        self.info_label.setText(f"{count} screenshot{'s' if count != 1 else ''} in library")
    
    def get_selected_screenshot_id(self) -> Optional[int]:
        """
        Get currently selected screenshot ID.
        
        Returns:
            Screenshot ID or None
        """
        items = self.grid_widget.selectedItems()
        if items:
            return items[0].data(Qt.ItemDataRole.UserRole)
        return None
