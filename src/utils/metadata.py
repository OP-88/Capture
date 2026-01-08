"""
Metadata utilities for EXIF stripping and safe metadata extraction.
"""
from PIL import Image
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class MetadataHandler:
    """Handles safe metadata extraction and EXIF stripping."""
    
    @staticmethod
    def strip_exif(image_path: Path, output_path: Path) -> bool:
        """
        Strip EXIF metadata from image and save to output path.
        
        Args:
            image_path: Source image path
            output_path: Destination path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (removes alpha channel issues)
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = rgb_img
                
                # Save without EXIF data
                img.save(output_path, format='PNG', optimize=True)
            return True
        except Exception as e:
            print(f"Error stripping EXIF: {e}")
            return False
    
    @staticmethod
    def extract_safe_metadata(image_path: Path) -> Dict[str, Any]:
        """
        Extract safe metadata for database storage (no PII).
        
        Args:
            image_path: Path to image
            
        Returns:
            Dictionary with safe metadata
        """
        try:
            with Image.open(image_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'file_size': image_path.stat().st_size,
                    'created': datetime.fromtimestamp(image_path.stat().st_ctime).isoformat()
                }
        except Exception:
            return {}
