"""
Main window for Capture application.
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QToolBar, QStatusBar, QFileDialog, QMessageBox,
                              QLabel, QPushButton, QSplitter, QInputDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QPixmap, QImage
from pathlib import Path
import shutil
import cv2
import numpy as np

from src.gui.library_view import LibraryView
from src.gui.adjustment_panel import AdjustmentPanel
from src.gui.styles import get_dark_theme
from src.core.database import DatabaseManager, Screenshot
from src.core.image_processor import ImageProcessor
from src.core.sanitizer import PIISanitizer
from src.core.exporter import Exporter
from src.utils.security import SecurityValidator
from src.utils.metadata import MetadataHandler


class MainWindow(QMainWindow):
    """Main application window for Capture."""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.security_validator = SecurityValidator()
        self.image_processor = ImageProcessor()
        self.sanitizer = PIISanitizer()
        self.exporter = Exporter()
        
        self.current_screenshot: Screenshot = None
        self.current_image: np.ndarray = None
        self.original_image: np.ndarray = None  # Store original for reset
        
        self.init_ui()
        self.load_library()
    
    def init_ui(self):
        """Initialize UI components."""
        self.setWindowTitle("Capture - Screenshot Enhancement Tool")
        self.setGeometry(100, 100, 1400, 900)
        
        # Apply dark theme
        self.setStyleSheet(get_dark_theme())
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for library and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Library view (left side)
        self.library_view = LibraryView()
        self.library_view.screenshot_selected.connect(self.on_screenshot_selected)
        splitter.addWidget(self.library_view)
        
        # Preview panel (center)
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        self.preview_label = QLabel("Select a screenshot to preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(400, 400)
        self.preview_label.setStyleSheet("border: 1px solid #3a3a3a; border-radius: 8px;")
        preview_layout.addWidget(self.preview_label)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.sharpen_btn = QPushButton("🔍 Sharpen")
        self.sharpen_btn.clicked.connect(self.sharpen_current)
        self.sharpen_btn.setEnabled(False)
        button_layout.addWidget(self.sharpen_btn)
        
        self.sanitize_btn = QPushButton("🔒 Sanitize PII")
        self.sanitize_btn.clicked.connect(self.sanitize_current)
        self.sanitize_btn.setEnabled(False)
        button_layout.addWidget(self.sanitize_btn)
        
        self.copy_btn = QPushButton("📋 Copy to Clipboard")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setEnabled(False)
        button_layout.addWidget(self.copy_btn)
        
        preview_layout.addLayout(button_layout)
        
        splitter.addWidget(preview_widget)
        
        # Adjustment panel (right side)
        self.adjustment_panel = AdjustmentPanel()
        self.adjustment_panel.adjustments_changed.connect(self.on_adjustments_changed)
        self.adjustment_panel.reset_requested.connect(self.on_reset_adjustments)
        self.adjustment_panel.setMaximumWidth(320)
        self.adjustment_panel.set_enabled(False)
        splitter.addWidget(self.adjustment_panel)
        
        splitter.setStretchFactor(0, 1)  # Library
        splitter.setStretchFactor(1, 2)  # Preview (larger)
        splitter.setStretchFactor(2, 0)  # Adjustments (fixed width)
        
        main_layout.addWidget(splitter)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_toolbar(self):
        """Create application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Import action
        import_action = QAction("📥 Import", self)
        import_action.triggered.connect(self.import_screenshots)
        toolbar.addAction(import_action)
        
        toolbar.addSeparator()
        
        # Export action
        export_action = QAction("💾 Export", self)
        export_action.triggered.connect(self.export_current)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # Refresh action
        refresh_action = QAction("🔄 Refresh", self)
        refresh_action.triggered.connect(self.load_library)
        toolbar.addAction(refresh_action)
    
    def load_library(self):
        """Load all screenshots from database."""
        screenshots = self.db_manager.get_all_screenshots()
        self.library_view.load_screenshots(screenshots)
        self.status_bar.showMessage(f"Loaded {len(screenshots)} screenshots")
    
    def import_screenshots(self):
        """Import new screenshots into library."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Import Screenshots",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)"
        )
        
        if not file_paths:
            return
        
        imported_count = 0
        
        for file_path in file_paths:
            # Validate path and file type
            validated_path = self.security_validator.validate_path(file_path)
            if not validated_path:
                QMessageBox.warning(self, "Invalid File", f"Invalid file: {file_path}")
                continue
            
            if not self.security_validator.validate_file_type(validated_path):
                QMessageBox.warning(self, "Invalid Type", f"Not a valid image: {file_path}")
                continue
            
            try:
                # Copy to vault
                vault_path = self.security_validator.get_safe_vault_path(
                    validated_path.name,
                    'originals'
                )
                shutil.copy2(validated_path, vault_path)
                
                # Extract metadata
                metadata = MetadataHandler.extract_safe_metadata(vault_path)
                
                # Add to database
                screenshot = self.db_manager.add_screenshot(
                    str(vault_path),
                    image_metadata=metadata
                )
                
                if screenshot:
                    imported_count += 1
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Error importing {file_path}: {e}")
        
        self.status_bar.showMessage(f"Imported {imported_count} screenshot(s)")
        self.load_library()
    
    def on_screenshot_selected(self, screenshot_id: int):
        """
        Handle screenshot selection.
        
        Args:
            screenshot_id: Selected screenshot ID
        """
        self.current_screenshot = self.db_manager.get_screenshot(screenshot_id)
        
        if not self.current_screenshot:
            return
        
        # Load image
        image_path = self.current_screenshot.modified_path or self.current_screenshot.original_path
        self.current_image = cv2.imread(image_path)
        self.original_image = self.current_image.copy()  # Store original
        
        if self.current_image is None:
            QMessageBox.critical(self, "Error", "Failed to load image")
            return
        
        # Display preview
        self.display_preview(self.current_image)
        
        # Enable action buttons and adjustment panel
        self.sharpen_btn.setEnabled(True)
        self.sanitize_btn.setEnabled(True)
        self.copy_btn.setEnabled(True)
        self.adjustment_panel.set_enabled(True)
        
        # Reset adjustments to default
        self.adjustment_panel.reset_adjustments()
        
        # Update status
        filename = Path(image_path).name
        self.status_bar.showMessage(f"Selected: {filename}")
    
    def display_preview(self, image_array: np.ndarray):
        """
        Display image in preview panel.
        
        Args:
            image_array: Image as numpy array
        """
        # Convert to QPixmap
        rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb.shape
        bytes_per_line = 3 * width
        q_image = QImage(rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        
        # Scale to fit preview
        scaled_pixmap = pixmap.scaled(
            self.preview_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.preview_label.setPixmap(scaled_pixmap)
    
    def sharpen_current(self):
        """Apply sharpening to current screenshot."""
        if not self.current_screenshot or self.current_image is None:
            return
        
        # Apply sharpening
        sharpened = self.image_processor.sharpen_image(
            Path(self.current_screenshot.original_path),
            strength=1.5
        )
        
        if sharpened is None:
            QMessageBox.critical(self, "Error", "Failed to sharpen image")
            return
        
        # Save to modified folder
        modified_path = self.security_validator.get_safe_vault_path(
            Path(self.current_screenshot.original_path).name,
            'modified'
        )
        
        if self.image_processor.save_image(sharpened, modified_path):
            # Update database
            self.db_manager.update_screenshot(
                self.current_screenshot.id,
                modified_path=str(modified_path)
            )
            
            # Update current image and display
            self.current_image = sharpened
            self.display_preview(sharpened)
            self.status_bar.showMessage("Sharpening applied")
        else:
            QMessageBox.critical(self, "Error", "Failed to save sharpened image")
    
    def sanitize_current(self):
        """Apply PII sanitization to current screenshot."""
        if not self.current_screenshot:
            return
        
        self.status_bar.showMessage("Sanitizing... (this may take a moment)")
        
        # Apply sanitization
        sanitized, detected_types = self.sanitizer.auto_sanitize(
            Path(self.current_screenshot.original_path),
            method='blur'
        )
        
        if sanitized is None:
            QMessageBox.critical(self, "Error", "Failed to sanitize image")
            return
        
        if not detected_types:
            QMessageBox.information(self, "No PII Detected", "No PII patterns were detected in this image.")
            self.status_bar.showMessage("No PII detected")
            return
        
        # Save to modified folder
        modified_path = self.security_validator.get_safe_vault_path(
            Path(self.current_screenshot.original_path).name,
            'modified'
        )
        
        if self.image_processor.save_image(sanitized, modified_path):
            # Update database with sanitization log
            log = f"PII detected and redacted: {', '.join(detected_types)}"
            self.db_manager.update_screenshot(
                self.current_screenshot.id,
                modified_path=str(modified_path),
                sanitization_log=log
            )
            
            # Update current image and display
            self.current_image = sanitized
            self.display_preview(sanitized)
            
            QMessageBox.information(
                self,
                "Sanitization Complete",
                f"Detected and redacted: {', '.join(detected_types)}"
            )
            self.status_bar.showMessage(f"Sanitized: {len(detected_types)} PII type(s) redacted")
        else:
            QMessageBox.critical(self, "Error", "Failed to save sanitized image")
    
    def copy_to_clipboard(self):
        """Copy current image to clipboard."""
        if self.current_image is None:
            return
        
        if self.exporter.copy_to_clipboard(self.current_image):
            self.status_bar.showMessage("Copied to clipboard")
            QMessageBox.information(self, "Success", "Image copied to clipboard!")
        else:
            QMessageBox.critical(self, "Error", "Failed to copy to clipboard")
    
    def export_current(self):
        """Export current image to file."""
        if self.current_image is None:
            QMessageBox.warning(self, "No Image", "Please select an image first")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Image",
            "",
            "PNG (*.png);;JPEG (*.jpg *.jpeg)"
        )
        
        if not file_path:
            return
        
        # Determine format from extension
        ext = Path(file_path).suffix.lower()
        format_type = 'PNG' if ext == '.png' else 'JPEG'
        
        if self.exporter.save_with_exif_strip(self.current_image, Path(file_path), format_type):
            self.status_bar.showMessage(f"Exported to {file_path}")
            QMessageBox.information(self, "Success", "Image exported successfully!")
        else:
            QMessageBox.critical(self, "Error", "Failed to export image")
    
    def on_adjustments_changed(self, adjustments: dict):
        """
        Handle real-time adjustment changes.
        
        Args:
            adjustments: Dictionary of adjustment values
        """
        if self.original_image is None:
            return
        
        # Apply adjustments to original image (not compounding)
        adjusted = self.image_processor.apply_manual_adjustments(
            self.original_image,
            brightness=adjustments['brightness'],
            contrast=adjustments['contrast'],
            saturation=adjustments['saturation'],
            sharpness=adjustments['sharpness']
        )
        
        # Update current image and preview
        self.current_image = adjusted
        self.display_preview(adjusted)
        
        # Update status
        active_adjustments = [k for k, v in adjustments.items() if v != 0]
        if active_adjustments:
            status_msg = f"Active adjustments: {', '.join(active_adjustments)}"
            self.status_bar.showMessage(status_msg)
        else:
            self.status_bar.showMessage("No adjustments applied")
    
    def on_reset_adjustments(self):
        """
        Reset adjustments and restore original image.
        """
        if self.original_image is None:
            return
        
        # Restore original image
        self.current_image = self.original_image.copy()
        self.display_preview(self.current_image)
        
        self.status_bar.showMessage("Adjustments reset")
