#!/usr/bin/env python3
"""
Capture - Screenshot Enhancement Tool
Launch script.
"""
import sys
from pathlib import Path

# Add src directory to Python path
import shutil

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.main import main
except ImportError:
    # This might happen if installed via pip and src is in site-packages, 
    # but sys.path patch above usually handles local dev.
    # If installed as a package, 'src' should be top-level or 'capture.src' depending on layout.
    # Given the current layout, 'src' is expected to be a package.
    try:
        from src.main import main
    except ImportError:
         print("CRITICAL ERROR: 'src' package not found. Is the application installed correctly?")
         sys.exit(1)

def check_integrity():
    """
    The Checker Module: Runs a "Pre-flight Check" to ensure the environment is sane.
    """
    print("--- [ SELF-DIAGNOSTIC START ] ---")
    
    # 1. Brain Check (Source Code)
    try:
        import src
        print("[PASS] Brain: 'src' package found.")
    except ImportError:
        print("[FAIL] Brain: 'src' package MISSING. The application code is gone.")
        return False

    # 2. Eyes Check (Tesseract Binary)
    # Tesseract is critical for OCR. 
    # In Snap, it should be at /usr/bin/tesseract (inside the snap)
    tesseract_path = shutil.which("tesseract")
    if tesseract_path:
        print(f"[PASS] Eyes: Tesseract binary found at {tesseract_path}")
    else:
        print("[FAIL] Eyes: Tesseract binary MISSING. OCR will not work.")
        # We might continue, but PII redaction implies OCR is needed.
        # Let's consider it critical for "FORENSIC" tools.
        return False

    # 3. Language Check (English Data)
    # We check if we can actually run tesseract with 'eng'
    # Or check TESSDATA_PREFIX. 
    # Simple check: try listing langs or check default behavior implies 'eng' exists if not specified.
    # Better: check for the file if we know where it should be, or ask tesseract.
    # Reading Check (Language Data)
    try:
        import pytesseract
        langs = pytesseract.get_languages()
        print(f"Tesseract Languages Found: {langs}")
        if 'eng' not in langs:
             print("CRITICAL ERROR: 'eng' language pack not found.")
             # Don't exit yet, let's see what happens
    except Exception as e:
        print(f"CRITICAL ERROR: Could not get Tesseract languages: {e}")
        # Print environment for debugging
        import os
        print(f"TESSDATA_PREFIX: {os.environ.get('TESSDATA_PREFIX', 'Not Set')}")
    
    print("--- [ SELF-DIAGNOSTIC COMPLETE ] ---")
    return True

if __name__ == '__main__':
    if check_integrity():
        print("Starting Application...")
        main()
    else:
        print("\nCRITICAL: Integrity Check Failed. The application cannot start safely.")
        print("Please check the logs above for details.")
        sys.exit(1)

