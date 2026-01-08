"""
Export functionality for Capture.
Handles clipboard operations and secure file export with EXIF stripping.
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Optional
from PyQt6.QtGui import QImage, QPixmap, QClipboard
from PyQt6.QtWidgets import QApplication
from PIL import Image
import io


class Exporter:
    """Handles image export operations."""
    
    @staticmethod
    def copy_to_clipboard(image_array: np.ndarray) -> bool:
        """
        Copy image to system clipboard.
        
        Args:
            image_array: Image as numpy array (BGR)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert BGR to RGB
            rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            
            # Convert to QImage
            height, width, channel = rgb.shape
            bytes_per_line = 3 * width
            q_image = QImage(rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            
            # Copy to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(QPixmap.fromImage(q_image))
            
            return True
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            return False
    
    @staticmethod
    def save_with_exif_strip(
        image_array: np.ndarray,
        output_path: Path,
        format: str = 'PNG',
        quality: int = 95
    ) -> bool:
        """
        Save image with EXIF metadata stripped.
        
        Args:
            image_array: Image as numpy array (BGR)
            output_path: Destination path
            format: Output format ('PNG' or 'JPEG')
            quality: JPEG quality (1-100), ignored for PNG
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert BGR to RGB
            rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(rgb)
            
            # Save without EXIF
            if format.upper() == 'PNG':
                pil_image.save(output_path, 'PNG', optimize=True)
            elif format.upper() in ['JPEG', 'JPG']:
                # Convert RGBA to RGB if necessary
                if pil_image.mode == 'RGBA':
                    pil_image = pil_image.convert('RGB')
                pil_image.save(output_path, 'JPEG', quality=quality, optimize=True)
            else:
                return False
            
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    @staticmethod
    def get_image_bytes(image_array: np.ndarray, format: str = 'PNG') -> Optional[bytes]:
        """
        Convert image array to bytes for in-memory operations.
        
        Args:
            image_array: Image as numpy array (BGR)
            format: Output format
            
        Returns:
            Image bytes or None
        """
        try:
            rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb)
            
            byte_io = io.BytesIO()
            pil_image.save(byte_io, format=format)
            return byte_io.getvalue()
        except Exception as e:
            print(f"Error converting to bytes: {e}")
            return None
