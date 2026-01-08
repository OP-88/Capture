"""
Adjustment Panel for granular image enhancement controls.
Google Photos-style slider-based adjustments.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QSlider, QPushButton, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Dict


class AdjustmentPanel(QWidget):
    """Google Photos-style adjustment controls."""
    
    # Signal emitted when any adjustment changes
    adjustments_changed = pyqtSignal(dict)  # {brightness, contrast, saturation, sharpness}
    reset_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sliders: Dict[str, QSlider] = {}
        self.value_labels: Dict[str, QLabel] = {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize the adjustment panel UI."""
        layout = QVBoxLayout(self)
        
        # Group box for adjustments
        group = QGroupBox("Image Adjustments")
        group_layout = QVBoxLayout()
        
        # Brightness slider
        self.add_slider(
            group_layout,
            "brightness",
            "Brightness",
            -100, 100, 0
        )
        
        # Contrast slider
        self.add_slider(
            group_layout,
            "contrast",
            "Contrast",
            -100, 100, 0
        )
        
        # Saturation slider
        self.add_slider(
            group_layout,
            "saturation",
            "Saturation",
            -100, 100, 0
        )
        
        # Sharpness slider
        self.add_slider(
            group_layout,
            "sharpness",
            "Sharpness",
            0, 100, 0
        )
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        # Reset button
        reset_btn = QPushButton("⟲ Reset All Adjustments")
        reset_btn.clicked.connect(self.reset_adjustments)
        layout.addWidget(reset_btn)
        
        # Add stretch to push controls to top
        layout.addStretch()
    
    def add_slider(self, layout: QVBoxLayout, key: str, label: str, 
                   min_val: int, max_val: int, default: int):
        """
        Add a labeled slider with value display.
        
        Args:
            layout: Parent layout
            key: Slider identifier
            label: Display label
            min_val: Minimum value
            max_val: Maximum value
            default: Default value
        """
        # Container for this slider
        slider_container = QVBoxLayout()
        
        # Header row: Label + Value
        header = QHBoxLayout()
        name_label = QLabel(label)
        name_label.setStyleSheet("font-weight: bold;")
        value_label = QLabel(str(default))
        value_label.setMinimumWidth(40)
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        value_label.setStyleSheet("color: #00BFA5;")  # Teal accent
        
        header.addWidget(name_label)
        header.addStretch()
        header.addWidget(value_label)
        
        slider_container.addLayout(header)
        
        # Slider
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval((max_val - min_val) // 10)
        
        # Connect slider to update value label and emit signal
        slider.valueChanged.connect(lambda v: self.on_slider_changed(key, v))
        
        slider_container.addWidget(slider)
        
        # Min/Max labels
        range_labels = QHBoxLayout()
        range_labels.addWidget(QLabel(str(min_val)))
        range_labels.addStretch()
        range_labels.addWidget(QLabel(str(max_val)))
        slider_container.addLayout(range_labels)
        
        # Store references
        self.sliders[key] = slider
        self.value_labels[key] = value_label
        
        # Add to parent layout
        layout.addLayout(slider_container)
        layout.addSpacing(10)
    
    def on_slider_changed(self, key: str, value: int):
        """
        Handle slider value change.
        
        Args:
            key: Slider identifier
            value: New value
        """
        # Update value label
        self.value_labels[key].setText(str(value))
        
        # Emit full adjustment state
        self.adjustments_changed.emit(self.get_adjustments())
    
    def get_adjustments(self) -> Dict[str, int]:
        """
        Get current adjustment values.
        
        Returns:
            Dictionary of adjustment values
        """
        return {
            'brightness': self.sliders['brightness'].value(),
            'contrast': self.sliders['contrast'].value(),
            'saturation': self.sliders['saturation'].value(),
            'sharpness': self.sliders['sharpness'].value()
        }
    
    def reset_adjustments(self):
        """Reset all sliders to default (0)."""
        for key, slider in self.sliders.items():
            default = 0 if key != 'sharpness' else 0
            slider.setValue(default)
        
        # Emit reset signal
        self.reset_requested.emit()
    
    def set_enabled(self, enabled: bool):
        """
        Enable or disable all controls.
        
        Args:
            enabled: Whether controls should be enabled
        """
        for slider in self.sliders.values():
            slider.setEnabled(enabled)
