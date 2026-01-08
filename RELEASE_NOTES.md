# Capture Release Notes

## Version 1.0.0 - Initial Release

**Release Date:** January 8, 2026

### Overview

Capture is a local-first screenshot enhancement and library tool designed for security professionals on Fedora GNOME. This initial release provides forensic-grade screenshot management with PII sanitization, chain-of-custody tracking, and report-ready image enhancement.

### Core Features

#### Screenshot Library (The Vault)
- Grid-view gallery with thumbnail generation
- Metadata tracking (date, tags, dimensions, file size)
- Search and filter functionality
- Chain-of-custody: separate storage for originals and modified versions

#### Image Enhancement Suite
- **Sharpen Filter**: Unsharp mask for terminal text legibility
- **Highlight Tool**: Semi-transparent rectangle annotations
- **Upscale Placeholder**: Ready for AI integration (Real-ESRGAN)

#### PII Sanitization Engine
- **Automatic Detection** via Regex + OCR:
  - IPv4/IPv6 addresses
  - Email addresses
  - API keys (AWS, GitHub, Stripe, generic 32+ char)
  - JWT tokens
  - Private keys
- **Redaction Methods**: Blur or pixelate
- **Audit Logging**: Tracks what was sanitized

#### Secure Export
- **Clipboard Integration**: QClipboard for instant copy
- **File Export**: PNG/JPEG with EXIF stripping
- **Privacy**: All metadata removed from exports

### Security Features

✅ **Path Traversal Prevention** - Validates all file paths  
✅ **File Type Validation** - Magic number detection (not just extensions)  
✅ **EXIF Stripping** - Removes location/device metadata  
✅ **Input Sanitization** - SQL injection prevention  
✅ **Local-First Processing** - Zero cloud uploads  

### Technical Stack

- **Backend**: Python 3.12+
- **GUI**: PyQt6 with dark GNOME-native theme
- **Database**: SQLite with SQLAlchemy ORM
- **Image Processing**: OpenCV + Pillow
- **OCR**: Tesseract (pytesseract)
- **Security**: python-magic, regex validation

### System Requirements

- **Operating System**: Fedora Linux (or compatible RHEL-based)
- **Python**: 3.12 or higher
- **System Dependencies**: tesseract, libmagic
- **Disk Space**: ~100MB (plus vault storage)

### Installation

**Via RPM Package (Recommended):**

```bash
# Install system dependencies
sudo dnf install -y python3 tesseract tesseract-langpack-eng file-libs

# Download from GitHub Releases
wget https://github.com/OP-88/Capture/releases/download/v1.0.0/capture-1.0.0-1.fc*.noarch.rpm

# Install
sudo dnf install ./capture-1.0.0-1.fc*.noarch.rpm

# Run
capture
```

**From Source:**

```bash
git clone https://github.com/OP-88/Capture.git
cd Capture
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

### Known Issues

None at this time. All core functionality tested and verified.

### Bug Fixes in This Release

- Fixed SQLAlchemy metadata column conflict (#1)
- Resolved import path issues

### Testing

All modules tested and verified:
- ✅ Database operations
- ✅ Image processing (sharpen, highlight)
- ✅ PII detection (IPv4, emails, API keys)
- ✅ Security validation
- ✅ Metadata handling and EXIF stripping

### Future Roadmap

- Interactive highlight tool with color picker
- AI upscaling integration (Real-ESRGAN)
- Batch processing mode
- Tag management UI
- Export templates for security reports
- Keyboard shortcuts
- Multiple language support for OCR

### Contributors

Built for the cybersecurity and DevOps community.

### License

GNU General Public License v3.0

---

## Download

**RPM Package (Fedora):**  
[capture-1.0.0-1.*.noarch.rpm](https://github.com/OP-88/Capture/releases/tag/v1.0.0)

**Source Code:**  
[GitHub Repository](https://github.com/OP-88/Capture)

---

## Support

- **Issues**: https://github.com/OP-88/Capture/issues
- **Documentation**: See README.md and INSTALL.md in the repository
