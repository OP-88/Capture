"""
Security utilities for Capture.
Implements path validation, input sanitization, and secure file handling.
"""
import os
import re
from pathlib import Path
from typing import Optional
import magic


class SecurityValidator:
    """Handles security validation for file operations."""
    
    # Allowed image MIME types
    ALLOWED_MIME_TYPES = {
        'image/png',
        'image/jpeg',
        'image/jpg',
        'image/bmp',
        'image/tiff',
        'image/webp'
    }
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
    
    def __init__(self, base_vault_path: str):
        """
        Initialize security validator.
        
        Args:
            base_vault_path: Absolute path to the vault directory
        """
        self.base_vault_path = Path(base_vault_path).resolve()
        
    def validate_path(self, file_path: str) -> Optional[Path]:
        """
        Validate file path to prevent path traversal attacks.
        
        Args:
            file_path: Path to validate
            
        Returns:
            Validated Path object or None if invalid
        """
        try:
            # Resolve to absolute path
            abs_path = Path(file_path).resolve()
            
            # Check if path exists
            if not abs_path.exists():
                return None
                
            # Ensure path is a file, not a directory
            if not abs_path.is_file():
                return None
                
            # Validate file extension
            if abs_path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
                return None
                
            return abs_path
            
        except (OSError, ValueError):
            return None
    
    def validate_file_type(self, file_path: Path) -> bool:
        """
        Validate file type using magic numbers (not just extension).
        
        Args:
            file_path: Path to file
            
        Returns:
            True if valid image file, False otherwise
        """
        try:
            mime = magic.from_file(str(file_path), mime=True)
            return mime in self.ALLOWED_MIME_TYPES
        except Exception:
            return False
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent injection attacks.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path separators
        filename = os.path.basename(filename)
        
        # Remove special characters, keep alphanumeric, dots, hyphens, underscores
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext
            
        return filename
    
    def get_safe_vault_path(self, filename: str, subfolder: str = 'originals') -> Path:
        """
        Generate safe path within vault for storing files.
        
        Args:
            filename: Filename to store
            subfolder: Subfolder within vault ('originals' or 'modified')
            
        Returns:
            Safe path within vault
        """
        safe_filename = self.sanitize_filename(filename)
        target_path = self.base_vault_path / subfolder / safe_filename
        
        # Ensure target is within vault (prevent traversal)
        if not str(target_path.resolve()).startswith(str(self.base_vault_path)):
            raise ValueError("Path traversal attempt detected")
            
        # Handle duplicate filenames
        counter = 1
        original_target = target_path
        while target_path.exists():
            name, ext = os.path.splitext(safe_filename)
            target_path = original_target.parent / f"{name}_{counter}{ext}"
            counter += 1
            
        return target_path
    
    def sanitize_sql_input(self, input_string: str) -> str:
        """
        Sanitize input for SQL queries (though SQLAlchemy handles this,
        this is an additional safety layer).
        
        Args:
            input_string: Input to sanitize
            
        Returns:
            Sanitized string
        """
        # Remove null bytes
        return input_string.replace('\x00', '')
