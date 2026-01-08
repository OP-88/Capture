"""
Image processing engine for Capture.
Implements enhancement features: sharpen, highlight, and upscale.
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
from typing import Tuple, Optional, List


class ImageProcessor:
    """Handles image enhancement operations."""
    
    @staticmethod
    def sharpen_image(image_path: Path, strength: float = 1.5) -> Optional[np.ndarray]:
        """
        Apply unsharp mask filter to improve text legibility.
        
        Args:
            image_path: Path to source image
            strength: Sharpening strength (1.0-3.0 recommended)
            
        Returns:
            Sharpened image as numpy array or None
        """
        try:
            # Read image
            img = cv2.imread(str(image_path))
            if img is None:
                return None
            
            # Apply Gaussian blur
            gaussian = cv2.GaussianBlur(img, (0, 0), 2.0)
            
            # Unsharp mask: original + (original - blurred) * strength
            sharpened = cv2.addWeighted(img, 1.0 + strength, gaussian, -strength, 0)
            
            return sharpened
        except Exception as e:
            print(f"Error sharpening image: {e}")
            return None
    
    @staticmethod
    def add_highlight(
        image_array: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Tuple[int, int, int] = (255, 255, 0),
        opacity: float = 0.3
    ) -> np.ndarray:
        """
        Add semi-transparent highlight rectangle to image.
        
        Args:
            image_array: Image as numpy array
            x, y: Top-left corner coordinates
            width, height: Rectangle dimensions
            color: RGB color tuple
            opacity: Transparency (0.0-1.0)
            
        Returns:
            Image with highlight overlay
        """
        try:
            # Create overlay
            overlay = image_array.copy()
            
            # BGR color for OpenCV
            bgr_color = (color[2], color[1], color[0])
            
            # Draw filled rectangle
            cv2.rectangle(overlay, (x, y), (x + width, y + height), bgr_color, -1)
            
            # Blend with original
            result = cv2.addWeighted(overlay, opacity, image_array, 1 - opacity, 0)
            
            return result
        except Exception as e:
            print(f"Error adding highlight: {e}")
            return image_array
    
    @staticmethod
    def add_border_highlight(
        image_array: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Tuple[int, int, int] = (255, 0, 0),
        thickness: int = 3
    ) -> np.ndarray:
        """
        Add border highlight to image (no fill).
        
        Args:
            image_array: Image as numpy array
            x, y: Top-left corner coordinates
            width, height: Rectangle dimensions
            color: RGB color tuple
            thickness: Border thickness in pixels
            
        Returns:
            Image with border highlight
        """
        try:
            result = image_array.copy()
            bgr_color = (color[2], color[1], color[0])
            cv2.rectangle(result, (x, y), (x + width, y + height), bgr_color, thickness)
            return result
        except Exception as e:
            print(f"Error adding border: {e}")
            return image_array
    
    @staticmethod
    def upscale_placeholder(image_path: Path, scale_factor: int = 2) -> Optional[np.ndarray]:
        """
        Placeholder for AI-based upscaling (currently uses bicubic).
        Future: Integrate Real-ESRGAN or similar.
        
        Args:
            image_path: Path to source image
            scale_factor: Upscaling factor
            
        Returns:
            Upscaled image or None
        """
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return None
            
            height, width = img.shape[:2]
            new_dims = (width * scale_factor, height * scale_factor)
            
            # Using bicubic interpolation (placeholder for AI model)
            upscaled = cv2.resize(img, new_dims, interpolation=cv2.INTER_CUBIC)
            
            return upscaled
        except Exception as e:
            print(f"Error upscaling image: {e}")
            return None
    
    @staticmethod
    def save_image(image_array: np.ndarray, output_path: Path) -> bool:
        """
        Save processed image to disk.
        
        Args:
            image_array: Image as numpy array
            output_path: Destination path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cv2.imwrite(str(output_path), image_array)
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    @staticmethod
    def array_to_pillow(image_array: np.ndarray) -> Image.Image:
        """
        Convert OpenCV numpy array to PIL Image.
        
        Args:
            image_array: OpenCV BGR image
            
        Returns:
            PIL Image in RGB
        """
        # Convert BGR to RGB
        rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)
    
    @staticmethod
    def pillow_to_array(pil_image: Image.Image) -> np.ndarray:
        """
        Convert PIL Image to OpenCV numpy array.
        
        Args:
            pil_image: PIL Image
            
        Returns:
            OpenCV BGR array
        """
        rgb = np.array(pil_image)
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
