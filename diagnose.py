#!/usr/bin/env python3
import sys
import os
import shutil
import platform
from pathlib import Path

def check_step(name):
    print(f"\n[CHECK] {name}...")

def pass_step(msg):
    print(f"  [PASS] {msg}")

def fail_step(msg, critical=True):
    print(f"  [FAIL] {msg}")
    if critical:
        print("  !!! CRITICAL FAILURE DETECTED !!!")

def diagnose():
    print("=== CAPTURE SYSTEM DIAGNOSTICS ===")
    print(f"Python: {sys.version}")
    print(f"Platform: {platform.platform()}")
    
    # 1. Environment Variables
    check_step("Environment Variables")
    vars_to_check = ['SNAP', 'SNAP_USER_DATA', 'TESSDATA_PREFIX', 'MAGIC', 'LD_LIBRARY_PATH', 'PYTHONPATH']
    for v in vars_to_check:
        val = os.environ.get(v)
        if val:
            pass_step(f"{v}: {val}")
        else:
            fail_step(f"{v} is NOT set", critical=False)

    # 2. Key Directories
    check_step("Critical Directories")
    if os.environ.get('SNAP'):
        snap_dir = Path(os.environ['SNAP'])
        check_paths = [
            snap_dir / "usr/share/tesseract-ocr/4.00/tessdata",
            snap_dir / "usr/lib/file/magic.mgc",
            snap_dir / "lib/python3.10/site-packages/src"
        ]
        for p in check_paths:
            if p.exists():
                pass_step(f"Found: {p}")
            else:
                fail_step(f"Missing: {p}")
    
    # 3. Python Dependencies
    check_step("Python Libraries")
    try:
        import cv2
        pass_step(f"OpenCV: {cv2.__version__}")
    except ImportError as e:
        fail_step(f"OpenCV Import Failed: {e}")

    try:
        import pytesseract
        pass_step(f"PyTesseract: {pytesseract.__version__}")
    except ImportError as e:
        fail_step(f"PyTesseract Import Failed: {e}")

    try:
        import magic
        pass_step("Python-Magic: Imported")
    except ImportError as e:
        fail_step(f"Python-Magic Import Failed: {e}")

    # 4. Tesseract Functionality
    check_step("OCR Engine (Tesseract)")
    tess_bin = shutil.which("tesseract")
    if tess_bin:
        pass_step(f"Binary found at: {tess_bin}")
        try:
            import pytesseract
            langs = pytesseract.get_languages()
            pass_step(f"Languages: {langs}")
            if 'eng' in langs:
                pass_step("English data found.")
            else:
                fail_step("English data MISSING from Tesseract.")
        except Exception as e:
            fail_step(f"Failed to query languages: {e}")
    else:
        fail_step("Tesseract binary NOT found.")

    # 5. Magic Database
    check_step("File Type Detection (LibMagic)")
    try:
        import magic
        # Create a temporary file to test
        with open("test_magic.txt", "w") as f:
            f.write("test")
        
        m = magic.Magic(mime=True)
        ftype = m.from_file("test_magic.txt")
        pass_step(f"Magic DB works. Detected 'test_magic.txt' as: {ftype}")
        os.remove("test_magic.txt")
    except Exception as e:
        fail_step(f"Magic DB Failed: {e}")

    print("\n=== DIAGNOSTICS COMPLETE ===")

if __name__ == "__main__":
    diagnose()
