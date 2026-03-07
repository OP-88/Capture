"""
Main window for Capture application.
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QToolBar, QStatusBar, QFileDialog, QMessageBox,
                              QLabel, QPushButton, QSplitter, QInputDialog)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QPixmap, QImage
from pathlib import Path
import shutil
import cv2
import numpy as np

from src.gui.library_view import LibraryView
from src.gui.adjustment_panel import AdjustmentPanel
from src.gui.canvas_view import CanvasView
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
        self.working_image: np.ndarray = None  # Accumulates all changes (adjustments + sanitization)
        
        # Undo/Redo Stacks
        self.undo_stack: list = []
        self.redo_stack: list = []
        
        self.current_adjustments: dict = {'brightness': 0, 'contrast': 0, 'saturation': 0, 'sharpness': 0}
        self.sanitized_regions: list = []  # Store PII regions for re-application
        
        self.highlight_color = (255, 255, 0) # RGB Tuple for yellow
        
        self.init_ui()
        self.load_library()

        # Enable drag and drop
        self.setAcceptDrops(True)
    
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
        self.library_view.screenshot_delete_requested.connect(self.delete_screenshot)
        splitter.addWidget(self.library_view)
        
        # Preview panel (center)
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        self.canvas = CanvasView()
        self.canvas.setMinimumSize(400, 400)
        self.canvas.setStyleSheet("border: 1px solid #3a3a3a; border-radius: 8px;")
        preview_layout.addWidget(self.canvas)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.sharpen_btn = QPushButton("Sharpen")
        self.sharpen_btn.clicked.connect(self.sharpen_current)
        self.sharpen_btn.setEnabled(False)
        button_layout.addWidget(self.sharpen_btn)
        
        self.sanitize_btn = QPushButton("Sanitize PII")
        self.sanitize_btn.clicked.connect(self.sanitize_current)
        self.sanitize_btn.setEnabled(False)
        button_layout.addWidget(self.sanitize_btn)
        
        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setEnabled(False)
        button_layout.addWidget(self.copy_btn)
        
        self.download_btn = QPushButton("Download to Pictures")
        self.download_btn.clicked.connect(self.download_to_pictures)
        self.download_btn.setEnabled(False)
        button_layout.addWidget(self.download_btn)
        
        # Undo / Redo Buttons
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.clicked.connect(self.undo_action)
        self.undo_btn.setEnabled(False)
        button_layout.addWidget(self.undo_btn)
        
        self.redo_btn = QPushButton("Redo")
        self.redo_btn.clicked.connect(self.redo_action)
        self.redo_btn.setEnabled(False)
        button_layout.addWidget(self.redo_btn)
        
        preview_layout.addLayout(button_layout)
        
        splitter.addWidget(preview_widget)
        
        # Right Side Panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Adjustment panel (top of right side)
        self.adjustment_panel = AdjustmentPanel()
        self.adjustment_panel.adjustments_changed.connect(self.on_adjustments_changed)
        self.adjustment_panel.smart_optimize_requested.connect(self.on_smart_optimize_requested)
        self.adjustment_panel.set_enabled(False)
        right_layout.addWidget(self.adjustment_panel)
        
        # Tools layout for Focus Suite (bottom of right side)
        from PySide6.QtWidgets import QGroupBox
        tools_group = QGroupBox("Focus Suite Tools")
        tools_layout = QVBoxLayout(tools_group)
        
        self.highlight_btn = QPushButton("Lume Highlight")
        self.highlight_btn.clicked.connect(lambda: self.set_canvas_tool('highlight'))
        self.highlight_btn.setToolTip("Freeform highlighter tool")
        tools_layout.addWidget(self.highlight_btn)
        
        # Color chooser for highlight
        self.color_btn = QPushButton("Pick Highlight Color")
        self.color_btn.setStyleSheet("background-color: yellow; color: black;") # Default
        self.color_btn.clicked.connect(self.pick_highlight_color)
        tools_layout.addWidget(self.color_btn)
        
        self.blur_btn = QPushButton("Selective Blur")
        self.blur_btn.clicked.connect(lambda: self.set_canvas_tool('blur'))
        self.blur_btn.setToolTip("Precision manual blur tool")
        tools_layout.addWidget(self.blur_btn)
        
        tools_layout.addStretch()
        right_layout.addWidget(tools_group)
        
        right_panel.setMaximumWidth(320)
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 1)  # Library
        splitter.setStretchFactor(1, 2)  # Preview (larger)
        splitter.setStretchFactor(2, 0)  # Adjustments (fixed width)
        
        main_layout.addWidget(splitter)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add Air-Gap Status Shield (Permanent)
        self.airgap_shield = QLabel("🛡️")
        self.airgap_shield.setToolTip("Air-Gapped (Zero Network)")
        self.status_bar.addPermanentWidget(self.airgap_shield)
        
        self.status_bar.showMessage("Ready")
        
        # Undo / Redo Shortcuts
        from PySide6.QtGui import QKeySequence, QShortcut
        self.undo_shortcut = QShortcut(QKeySequence.StandardKey.Undo, self)
        self.undo_shortcut.activated.connect(self.undo_action)
        
        self.redo_shortcut = QShortcut(QKeySequence.StandardKey.Redo, self)
        self.redo_shortcut.activated.connect(self.redo_action)
    
    def create_toolbar(self):
        """Create application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Import action
        import_action = QAction("Import", self)
        import_action.triggered.connect(self.import_screenshots)
        toolbar.addAction(import_action)
        
        toolbar.addSeparator()
        
        # Export action
        export_action = QAction("Export", self)
        export_action.triggered.connect(self.export_current)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
    
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
        
        self.import_files_list(file_paths)
    
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
        self.working_image = self.current_image.copy()  # Initialize working copy
        self.sanitized_regions = []  # Reset sanitized regions
        
        if self.current_image is None:
            QMessageBox.critical(self, "Error", "Failed to load image")
            return
        
        # Clear Undo/Redo Stacks on new load
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.update_undo_redo_buttons()
        
        # Display preview
        self.display_preview(self.current_image)
        
        # Enable action buttons and adjustment panel
        self.sharpen_btn.setEnabled(True)
        self.sanitize_btn.setEnabled(True)
        self.copy_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        self.adjustment_panel.set_enabled(True)
        
        # Reset adjustments to default
        self.adjustment_panel.reset_adjustments()
        
        # Update status
        filename = Path(image_path).name
        self.status_bar.showMessage(f"Selected: {filename}")
    
    def display_preview(self, image_array: np.ndarray):
        """
        Display image in the interactive canvas.
        
        Args:
            image_array: Image as numpy array
        """
        # Convert to QPixmap
        rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb.shape
        bytes_per_line = 3 * width
        q_image = QImage(rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        
        self.canvas.set_image(pixmap, self.sanitized_regions)
        
        # Connect canvas signal if not already connected (using a flag or reconnecting safely)
        try:
            self.canvas.edit_applied.disconnect()
        except:
            pass
        self.canvas.edit_applied.connect(self.on_canvas_edit_applied)
        
    def set_canvas_tool(self, tool_name: str):
        self.canvas.set_tool(tool_name)
        self.status_bar.showMessage(f"Tool selected: {tool_name}")
        
    def on_canvas_edit_applied(self, tool_name: str, rect):
        """Handle a drawing action from the canvas."""
        if self.original_image is None or rect.isEmpty():
            return
            
        x, y, w, h = int(rect.x()), int(rect.y()), int(rect.width()), int(rect.height())
        
        self.push_undo_state()
        
        if tool_name == 'highlight':
            # Lume Highlighter
            self.original_image = self.image_processor.add_highlight(
                self.original_image, x, y, w, h, color=self.highlight_color, opacity=0.3
            )
        elif tool_name == 'blur':
            # Selective Stylus: blur region
            self.original_image = self.sanitizer.blur_region(
                self.original_image, x, y, w, h, blur_strength=25
            )
            
        # Re-apply adjustments to the new base original image
        self.on_adjustments_changed(self.current_adjustments)
        self.status_bar.showMessage(f"Applied {tool_name} to region ({x},{y},{w},{h})")
        
    def pick_highlight_color(self):
        """Open color dialog to pick highlight color."""
        from PySide6.QtWidgets import QColorDialog
        from PySide6.QtGui import QColor
        
        initial = QColor(self.highlight_color[0], self.highlight_color[1], self.highlight_color[2])
        color = QColorDialog.getColor(initial, self, "Select Highlight Color")
        if color.isValid():
            self.highlight_color = (color.red(), color.green(), color.blue())
            # Update button style locally to show color (white text for dark colors)
            luminance = (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()) / 255
            text_color = "black" if luminance > 0.5 else "white"
            self.color_btn.setStyleSheet(f"background-color: {color.name()}; color: {text_color};")

    def push_undo_state(self):
        """Save current original image state and adjustments to undo stack before modifications."""
        if self.original_image is not None:
            # Save a tuple: (image_copy, adjustments_copy)
            state = (self.original_image.copy(), self.current_adjustments.copy())
            self.undo_stack.append(state)
            if len(self.undo_stack) > 30: # Limit stack size
                self.undo_stack.pop(0)
            self.redo_stack.clear()
            self.update_undo_redo_buttons()

    def undo_action(self):
        """Undo last edit or adjustment."""
        if self.undo_stack:
            # Save current state to redo stack
            current_state = (self.original_image.copy(), self.current_adjustments.copy())
            self.redo_stack.append(current_state)
            
            # Pop previous state
            prev_image, prev_adjustments = self.undo_stack.pop()
            self.original_image = prev_image
            
            # Apply previous adjustments
            # Disconnect temporarily so setting sliders doesn't trigger new undo states
            self.adjustment_panel.adjustments_changed.disconnect(self.on_adjustments_changed)
            self.adjustment_panel.set_adjustments(
                brightness=prev_adjustments['brightness'],
                contrast=prev_adjustments['contrast'],
                sharpness=prev_adjustments['sharpness'],
                saturation=prev_adjustments['saturation']
            )
            self.adjustment_panel.adjustments_changed.connect(self.on_adjustments_changed)
            
            # Trigger visual update
            self.on_adjustments_changed(prev_adjustments, save_undo=False)
            
            self.update_undo_redo_buttons()
            self.status_bar.showMessage("Action undone")
            
    def redo_action(self):
        """Redo previously undone edit or adjustment."""
        if self.redo_stack:
            # Save current state to undo stack
            current_state = (self.original_image.copy(), self.current_adjustments.copy())
            self.undo_stack.append(current_state)
            
            # Pop next state
            next_image, next_adjustments = self.redo_stack.pop()
            self.original_image = next_image
            
            # Apply next adjustments
            self.adjustment_panel.adjustments_changed.disconnect(self.on_adjustments_changed)
            self.adjustment_panel.set_adjustments(
                brightness=next_adjustments['brightness'],
                contrast=next_adjustments['contrast'],
                sharpness=next_adjustments['sharpness'],
                saturation=next_adjustments['saturation']
            )
            self.adjustment_panel.adjustments_changed.connect(self.on_adjustments_changed)
            
            # Trigger visual update
            self.on_adjustments_changed(next_adjustments, save_undo=False)
            
            self.update_undo_redo_buttons()
            self.status_bar.showMessage("Action redone")
            
    def update_undo_redo_buttons(self):
        """Enable/disable undo/redo buttons based on stack state."""
        self.undo_btn.setEnabled(len(self.undo_stack) > 0)
        self.redo_btn.setEnabled(len(self.redo_stack) > 0)
    
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
        
        # Extract OCR boxes first to populate canvas magnets for future manual edits
        import tempfile, os
        from PySide6.QtGui import QImage
        
        # We need the original image path or a temp path if it's from clipboard
        if self.current_screenshot.original_path:
            image_path = Path(self.current_screenshot.original_path)
            
            # Populate OCR boxes for snapping
            all_text_boxes = self.sanitizer.detector.find_text_locations(image_path, [""]) # find all text
            self.sanitized_regions = all_text_boxes
            if self.current_image is not None:
                self.display_preview(self.current_image)
        else:
            image_path = None
            
        if not image_path:
             self.status_bar.showMessage("Cannot run auto-sanitize on unsaved images yet.")
             return

        # Push state before heavy edit
        self.push_undo_state()

        # Apply sanitization
        sanitized, detected_types = self.sanitizer.auto_sanitize(
            image_path,
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
            
            # Update all image references to preserve sanitization during adjustments
            # Update original image to include redactions (so future adjustments apply to redacted version)
            self.original_image = sanitized.copy()
            
            # Re-apply current adjustments to the new base
            self.on_adjustments_changed(self.current_adjustments)
            
            # Note: display_preview is handled by on_adjustments_changed
            
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
    
    def on_adjustments_changed(self, adjustments: dict, save_undo: bool = True):
        """
        Handle real-time adjustment changes with cumulative editing support.
        
        Args:
            adjustments: Dictionary of adjustment values
            save_undo: Boolean indicating if this change should be pushed to undo stack
        """
        if self.original_image is None:
            return
            
        if save_undo and adjustments != self.current_adjustments:
            self.push_undo_state()
        
        # Store current adjustments
        self.current_adjustments = adjustments
        
        # Apply adjustments to original image
        adjusted = self.image_processor.apply_manual_adjustments(
            self.original_image,
            brightness=adjustments['brightness'],
            contrast=adjustments['contrast'],
            saturation=adjustments['saturation'],
            sharpness=adjustments['sharpness']
        )
        
        # Update working image and current image
        self.working_image = adjusted.copy()
        self.current_image = adjusted
        self.display_preview(adjusted)
    
        self.display_preview(adjusted)
    
    def delete_screenshot(self, screenshot_id: int):
        """
        Delete a screenshot from library and filesystem.
        
        Args:
            screenshot_id: ID of screenshot to delete
        """
        reply = QMessageBox.question(
            self, "Delete Screenshot",
            "Delete this screenshot? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            screenshot = self.db_manager.get_screenshot(screenshot_id)
            if screenshot:
                # Delete files from vault
                try:
                    Path(screenshot.original_path).unlink(missing_ok=True)
                    if screenshot.modified_path:
                        Path(screenshot.modified_path).unlink(missing_ok=True)
                except Exception as e:
                    print(f"Error deleting files: {e}")
                
                # Remove from database
                if self.db_manager.delete_screenshot(screenshot_id):
                    self.status_bar.showMessage("Screenshot deleted")
                    # Reload library
                    self.load_library()
                    # Clear preview if deleted screenshot was selected
                    if self.current_screenshot and self.current_screenshot.id == screenshot_id:
                        self.current_screenshot = None
                        self.current_image = None
                        self.original_image = None
                        self.working_image = None
                        self.undo_stack.clear()
                        self.redo_stack.clear()
                        self.update_undo_redo_buttons()
                        # Clear canvas
                        blank = QPixmap(self.canvas.size())
                        blank.fill(Qt.GlobalColor.transparent)
                        self.canvas.set_image(blank)
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete screenshot from database")
    
    def download_to_pictures(self):
        """Download current working image to ~/Pictures/Capture/"""
        if self.working_image is None:
            return
        
        # Create Capture folder in Pictures
        from datetime import datetime
        pictures_dir = Path.home() / "Pictures" / "Capture"
        pictures_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.png"
        save_path = pictures_dir / filename
        
        # Save with EXIF stripping (use working_image which has all edits)
        if self.exporter.save_with_exif_strip(self.working_image, save_path, 'PNG'):
            self.status_bar.showMessage(f"Downloaded to {save_path}")
            QMessageBox.information(
                self, "Success",
                f"Image saved to:\n{save_path}"
            )
        else:
            QMessageBox.critical(self, "Error", "Failed to download image")

    # Drag and Drop Events
    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle drop event."""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if not files:
            return
            
        # Filter for valid images
        image_files = [f for f in files if Path(f).suffix.lower() in self.security_validator.ALLOWED_EXTENSIONS]
        
        if not image_files:
            return

        self.import_files_list(image_files)

    def import_files_list(self, file_paths):
        """Helper to import a list of file paths (shared by drag-drop and dialog)."""
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

    def on_smart_optimize_requested(self):
        """Handle Smart Optimize request from the LIP engine."""
        if self.original_image is None:
            return
            
        brightness, contrast = self.image_processor.smart_optimize(self.original_image)
        sharpness_score = self.image_processor.calculate_sharpness_score(self.original_image)
        
        # Recommend sharpness if edge density is low (e.g., var < 150)
        sharpness = 25 if sharpness_score < 150 else 0
        
        # Push undo state before smart optimize wipes adjustments
        self.push_undo_state()
        
        # Visually confirm by setting sliders
        self.adjustment_panel.set_adjustments(
            brightness=brightness,
            contrast=contrast,
            sharpness=sharpness
        )
        self.status_bar.showMessage(f"LIP Engine Optimized: B={brightness}, C={contrast}, S={sharpness}")

    def keyPressEvent(self, event):
        """Handle Ctrl+V (Paste) for direct import from clipboard."""
        from PySide6.QtGui import QKeySequence
        from PySide6.QtWidgets import QApplication
        
        if event.matches(QKeySequence.StandardKey.Paste):
            clipboard = QApplication.clipboard()
            image = clipboard.image()
            if not image.isNull():
                self.import_from_clipboard(image)
        else:
            super().keyPressEvent(event)
            
    def import_from_clipboard(self, qimage: QImage):
        """Save clipboard image to vault via temp file."""
        from datetime import datetime
        import tempfile
        import os
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"clipboard_{timestamp}.png")
        
        if qimage.save(temp_path, "PNG"):
            self.import_files_list([temp_path])
        else:
            QMessageBox.critical(self, "Error", "Failed to paste image from clipboard")
