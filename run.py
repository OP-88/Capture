#!/usr/bin/env python3
"""
Capture - Screenshot Enhancement Tool
Launch script.
"""
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import main

if __name__ == '__main__':
    main()
