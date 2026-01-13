"""
PII Sanitization module for Capture.
Detects and redacts sensitive data: IPs, API keys, emails, etc.
"""
import re
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Optional
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


class PIIDetector:
    """Detects PII patterns in text and images."""
    
    # Regex patterns for common PII
    PATTERNS = {
        'ipv4': r'\b(?:[0-9]{1,3}[.,]){3}[0-9]{1,3}\b',
        'ipv6': r'\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+?1[-.]?)?\(?[0-9]{3}\)?[-.]?[0-9]{3}[-.]?[0-9]{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'api_key_generic': r'\b[A-Za-z0-9_\-]{20,}\b',
        'aws_access_key': r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b',
        'aws_secret': r'\b[A-Za-z0-9/+=]{40}\b',
        'jwt': r'\beyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]+\b',
        'private_key': r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----',
        'github_token': r'\bghp_[A-Za-z0-9]{36}\b',
        'stripe_key': r'\b(?:sk|pk)_(?:live|test)_[A-Za-z0-9]{24,}\b',
        'slack_token': r'\bxox[baprs]-([0-9a-zA-Z]{10,48})\b',
        'google_api': r'\bAIza[0-9A-Za-z-_]{35}\b',
        'context_secret': r'(?i)\b[a-z0-9_]*(?:password|passwd|secret|token|key|pwd|auth|api|email|phone)[a-z0-9_]*\s*[:=]\s*["\']?([A-Za-z0-9+/=._@-]+)["\']?',
    }
    
    def detect_in_text(self, text: str) -> Dict[str, List[str]]:
        """
        Detect PII patterns in text.
        
        Args:
            text: Text to scan
            
        Returns:
            Dictionary mapping pattern names to found matches
        """
        findings = {}
        
        for name, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                findings[name] = matches
        
        return findings
    
    def extract_text_from_image(self, image_path: Path) -> Optional[str]:
        """
        Extract text from image using OCR.
        
        Args:
            image_path: Path to image
            
        Returns:
            Extracted text or None if OCR unavailable
        """
        if not TESSERACT_AVAILABLE:
            print("Warning: pytesseract not available. OCR disabled.")
            return None
        
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return None
            
            # Convert to grayscale for better OCR
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Extract text
            text = pytesseract.image_to_string(gray)
            return text
        except Exception as e:
            print(f"Error extracting text: {e}")
            return None
    
    def find_text_locations(self, image_path: Path, search_terms: List[str]) -> List[Tuple[int, int, int, int]]:
        """
        Find bounding boxes of specific text in image using OCR.
        
        Args:
            image_path: Path to image
            search_terms: List of terms to locate
            
        Returns:
            List of bounding boxes (x, y, width, height)
        """
        if not TESSERACT_AVAILABLE:
            return []
        
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return []
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Get bounding box data
            data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            
            boxes = []
            for i, word in enumerate(data['text']):
                for term in search_terms:
                    if term.lower() in word.lower():
                        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                        boxes.append((x, y, w, h))
            
            return boxes
        except Exception as e:
            print(f"Error finding text locations: {e}")
            return []


class PIISanitizer:
    """Sanitizes images by redacting detected PII."""
    
    def __init__(self):
        self.detector = PIIDetector()
    
    def blur_region(
        self,
        image_array: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int,
        blur_strength: int = 25
    ) -> np.ndarray:
        """
        Apply blur to specific region.
        
        Args:
            image_array: Image as numpy array
            x, y: Top-left corner
            width, height: Region dimensions
            blur_strength: Blur kernel size (odd number)
            
        Returns:
            Image with blurred region
        """
        result = image_array.copy()
        
        # Ensure blur_strength is odd
        if blur_strength % 2 == 0:
            blur_strength += 1
        
        try:
            # Extract ROI
            roi = result[y:y+height, x:x+width]
            
            # Apply Gaussian blur
            blurred_roi = cv2.GaussianBlur(roi, (blur_strength, blur_strength), 0)
            
            # Replace ROI
            result[y:y+height, x:x+width] = blurred_roi
        except Exception as e:
            print(f"Error blurring region: {e}")
        
        return result
    
    def pixelate_region(
        self,
        image_array: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int,
        pixel_size: int = 10
    ) -> np.ndarray:
        """
        Apply pixelation to specific region.
        
        Args:
            image_array: Image as numpy array
            x, y: Top-left corner
            width, height: Region dimensions
            pixel_size: Size of pixelation blocks
            
        Returns:
            Image with pixelated region
        """
        result = image_array.copy()
        
        try:
            # Extract ROI
            roi = result[y:y+height, x:x+width]
            
            # Resize down and up to create pixelation effect
            h, w = roi.shape[:2]
            temp = cv2.resize(roi, (w // pixel_size, h // pixel_size), interpolation=cv2.INTER_LINEAR)
            pixelated = cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)
            
            # Replace ROI
            result[y:y+height, x:x+width] = pixelated
        except Exception as e:
            print(f"Error pixelating region: {e}")
        
        return result
    
    def auto_sanitize(self, image_path: Path, method: str = 'blur') -> Tuple[Optional[np.ndarray], List[str]]:
        """
        Automatically detect and sanitize PII in image.
        
        Args:
            image_path: Path to image
            method: Sanitization method ('blur' or 'pixelate')
            
        Returns:
            Tuple of (sanitized image array, list of detected PII types)
        """
        # Extract text using OCR
        text = self.detector.extract_text_from_image(image_path)
        
        if not text:
            # OCR failed or unavailable, return original
            img = cv2.imread(str(image_path))
            return img, []
        
        # Detect PII in extracted text
        findings = self.detector.detect_in_text(text)
        
        if not findings:
            # No PII detected
            img = cv2.imread(str(image_path))
            return img, []
        
        # Read image
        img = cv2.imread(str(image_path))
        
        # Collect all PII terms to redact
        all_terms = []
        for pii_type, matches in findings.items():
            all_terms.extend(matches)
        
        # Find locations of PII terms
        boxes = self.detector.find_text_locations(image_path, all_terms)
        
        # Apply sanitization
        for x, y, w, h in boxes:
            # Add padding
            padding = 5
            x = max(0, x - padding)
            y = max(0, y - padding)
            w += 2 * padding
            h += 2 * padding
            
            if method == 'blur':
                img = self.blur_region(img, x, y, w, h)
            elif method == 'pixelate':
                img = self.pixelate_region(img, x, y, w, h)
        
        detected_types = list(findings.keys())
        return img, detected_types
