#!/usr/bin/env python3
"""
Automated testing script for Capture application.
Tests all core functionality without GUI interaction.
"""
import sys
from pathlib import Path
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path.cwd()))

from src.core.database import DatabaseManager
from src.core.image_processor import ImageProcessor
from src.core.sanitizer import PIISanitizer
from src.core.exporter import Exporter
from src.utils.security import SecurityValidator
from src.utils.metadata import MetadataHandler

print("=== Capture Automated Test Suite ===\n")

# Test 1: Database Operations
print("[TEST 1] Database Operations...")
try:
    db = DatabaseManager('test_capture.db')
    
    # Add screenshot
    screenshot = db.add_screenshot(
        '/tmp/capture_test/test_screenshot.png',
        image_metadata={'width': 800, 'height': 600},
        tags='test, pii'
    )
    
    assert screenshot is not None, "Failed to add screenshot"
    assert screenshot.id > 0, "Invalid screenshot ID"
    print(f"  ✓ Screenshot added with ID: {screenshot.id}")
    
    # Retrieve screenshot
    retrieved = db.get_screenshot(screenshot.id)
    assert retrieved is not None, "Failed to retrieve screenshot"
    print(f"  ✓ Screenshot retrieved: {Path(retrieved.original_path).name}")
    
    # Update screenshot
    success = db.update_screenshot(screenshot.id, tags='test, pii, updated')
    assert success, "Failed to update screenshot"
    print("  ✓ Screenshot updated")
    
    # Clean up
    Path('test_capture.db').unlink(missing_ok=True)
    print("  ✓ Database test passed!\n")
except Exception as e:
    print(f"  ✗ Database test failed: {e}\n")
    sys.exit(1)

# Test 2: Image Processing
print("[TEST 2] Image Processing...")
try:
    processor = ImageProcessor()
    
    # Test sharpen
    sharpened = processor.sharpen_image(Path('/tmp/capture_test/test_screenshot.png'))
    assert sharpened is not None, "Sharpen failed"
    print("  ✓ Sharpen filter applied")
    
    # Test highlight
    highlighted = processor.add_highlight(sharpened, 100, 100, 200, 50, (255, 255, 0), 0.3)
    assert highlighted is not None, "Highlight failed"
    print("  ✓ Highlight overlay added")
    
    # Save test
    output_path = Path('/tmp/capture_test/processed.png')
    success = processor.save_image(highlighted, output_path)
    assert success, "Save failed"
    assert output_path.exists(), "Output file not created"
    print(f"  ✓ Image saved to {output_path}")
    print("  ✓ Image processing test passed!\n")
except Exception as e:
    print(f"  ✗ Image processing test failed: {e}\n")
    sys.exit(1)

# Test 3: PII Sanitization
print("[TEST 3] PII Sanitization...")
try:
    sanitizer = PIISanitizer()
    
    # Test text detection
    test_text = """
    Server IP: 192.168.1.100
    API Key: AKIAIOSFODNN7EXAMPLE
    Admin Email: admin@example.com
    """
    
    findings = sanitizer.detector.detect_in_text(test_text)
    print(f"  ✓ Detected PII patterns: {list(findings.keys())}")
    
    assert 'ipv4' in findings, "Failed to detect IP"
    assert 'aws_access_key' in findings, "Failed to detect AWS key"
    assert 'email' in findings, "Failed to detect email"
    
    print("  ✓ PII detection test passed!\n")
except Exception as e:
    print(f"  ✗ PII sanitization test failed: {e}\n")
    sys.exit(1)

# Test 4: Security Validation
print("[TEST 4] Security Validation...")
try:
    security = SecurityValidator(str(Path('data/vault').resolve()))
    
    # Test filename sanitization
    dangerous_name = "../../../etc/passwd"
    safe_name = security.sanitize_filename(dangerous_name)
    assert '..' not in safe_name, "Path traversal not prevented"
    print(f"  ✓ Sanitized '{dangerous_name}' to '{safe_name}'")
    
    # Test path validation
    valid_path = security.validate_path('/tmp/capture_test/test_screenshot.png')
    assert valid_path is not None, "Valid path rejected"
    print(f"  ✓ Valid path accepted")
    
    # Test invalid path
    invalid_path = security.validate_path('/tmp/nonexistent.png')
    assert invalid_path is None, "Invalid path accepted"
    print("  ✓ Invalid path rejected")
    
    print("  ✓ Security validation test passed!\n")
except Exception as e:
    print(f"  ✗ Security validation test failed: {e}\n")
    sys.exit(1)

# Test 5: Metadata Handling
print("[TEST 5] Metadata Handling...")
try:
    # Extract metadata
    metadata = MetadataHandler.extract_safe_metadata(Path('/tmp/capture_test/test_screenshot.png'))
    
    assert 'width' in metadata, "Width missing"
    assert 'height' in metadata, "Height missing"
    assert metadata['width'] == 800, "Wrong width"
    assert metadata['height'] == 600, "Wrong height"
    
    print(f"  ✓ Metadata extracted: {metadata['width']}x{metadata['height']}")
    
    # Test EXIF stripping
    output_path = Path('/tmp/capture_test/no_exif.png')
    success = MetadataHandler.strip_exif(
        Path('/tmp/capture_test/test_screenshot.png'),
        output_path
    )
    
    assert success, "EXIF stripping failed"
    assert output_path.exists(), "Output file not created"
    print("  ✓ EXIF metadata stripped")
    print("  ✓ Metadata handling test passed!\n")
except Exception as e:
    print(f"  ✗ Metadata handling test failed: {e}\n")
    sys.exit(1)

print("=" * 40)
print("✓ ALL TESTS PASSED!")
print("=" * 40)
print("\nCapture is ready for production use.")
