<div align="center">

#  Capture

<p align="center">
  <img src="capture_icon.png" alt="Capture Icon" width="200"/>
</p>

**A Local-First Screenshot Enhancement & Library Tool for Security Professionals**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Platform](https://img.shields.io/badge/Platform-Linux-orange.svg)](https://github.com/OP-88/Capture)
[![Python](https://img.shields.io/badge/Python-3.12+-green.svg)](https://www.python.org/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/OP-88/Capture/release.yml)](https://github.com/OP-88/Capture/actions)

> Built on Fedora GNOME | Designed for Cybersecurity Documentation | Zero Cloud Dependencies

</div>

---

## ⚡ Quick Feature Highlights

<table>
<tr>
<td width="25%" align="center">🎨<br/><b>Granular Adjustments</b><br/>Brightness, Contrast, Saturation, Sharpness</td>
<td width="25%" align="center">🔒<br/><b>PII Sanitization</b><br/>Auto-detect & redact sensitive data</td>
<td width="25%" align="center">📚<br/><b>Library Management</b><br/>Grid view with search & tagging</td>
<td width="25%" align="center">💻<br/><b>100% Local</b><br/>Zero cloud uploads, complete privacy</td>
</tr>
</table>

---

## 🎯 The Problem

In high-stakes security audits and full-stack development, the "screenshot" is the primary unit of evidence. However, standard tools are failing us:

- **Low Resolution**: Screenshots lose critical detail when zoomed
- **No PII Protection**: Accidental data leakage (API keys, IPs, credentials)
- **Cloud Security Risks**: Most beautifiers require uploading sensitive codebase captures
- **Poor Organization**: No forensic tracking or chain-of-custody

---

## 🚀 The Solution

**Capture** is a forensic-grade desktop application that:

1. **Enhances Quality**: Granular adjustment controls for professional-grade screenshots
2. **Sanitizes PII**: Automatic detection and redaction of sensitive data
3. **Maintains Chain-of-Custody**: Tracks original vs. modified versions
4. **100% Local**: Zero cloud uploads, all processing happens on your machine

---

## ✨ Features

### The Vault (Library)
- Grid-view gallery of all imported screenshots
- Metadata tracking: date, tags, file size, dimensions
- Search and filter by tags
- Chain-of-custody: separate storage for originals and modified versions
- **Right-click delete**: Remove screenshots from library
- **Dark theme UI**: Seamless GNOME integration

### Enhancement Suite
- **🎨 Granular Adjustments**: Google Photos-style slider controls
  - **Brightness** (-100 to +100): Darken or brighten images
  - **Contrast** (-100 to +100): Adjust tonal range
  - **Saturation** (-100 to +100): Control color intensity
  - **Sharpness** (0 to +100): Unsharp masking for text legibility
  - **Real-Time Preview**: Instant feedback as you adjust
  - **Non-Destructive**: Always processes from the original
- **🔍 One-Click Sharpen**: Quick enhancement for terminal screenshots
- **⬆️ Cumulative Editing**: Adjustments + sanitization stack together (order-independent)

### PII Sanitization
- **Automatic Detection**: Regex + OCR for:
  - IPv4/IPv6 addresses
  - Email addresses
  - API keys (AWS, GitHub, Stripe, generic)
  - JWT tokens
  - Private keys
- **Redaction Methods**: Blur or pixelate
- **Persistent Protection**: Sanitization remains intact when adjusting image quality
- **Audit Log**: Tracks what was sanitized

### Export & Integration
- **📋 Copy to Clipboard**: Direct copy for quick pasting
- **💾 Download to Pictures**: Save to `~/Pictures/Capture/` with timestamp
- **💾 Export**: Save as PNG/JPEG with EXIF metadata stripped
- **🔒 Secure**: All exports sanitized and anonymized

---

## 🔧 Installation

### Quick Start

**For development/testing:**
```bash
git clone https://github.com/OP-88/Capture.git
cd Capture
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

### RPM Package (Recommended for Production)

**Build and install as a standalone application:**

```bash
# Clone the repository
git clone https://github.com/OP-88/Capture.git
cd Capture

# Install system dependencies
sudo dnf install -y python3 tesseract tesseract-langpack-eng file-libs

# Build the RPM package
./build-rpm.sh

# Install Capture (replace with latest version from releases)
sudo dnf install ./capture-1.0.2-1.*.noarch.rpm

# Run from anywhere
capture
```

The RPM package installs Capture as a system application with:
- Desktop menu integration
- Standalone executable (`capture` command)
- Proper dependency management
- System-wide installation

For detailed installation instructions, see [INSTALL.md](INSTALL.md).

### Prerequisites

**Fedora Linux:**
```bash
# Install system dependencies
sudo dnf install -y python3 python3-pip tesseract libmagic

# Optional: Install tesseract language packs for better OCR
sudo dnf install -y tesseract-langpack-eng
```

### Manual Setup (Development)

1. **Clone the repository:**
```bash
git clone https://github.com/OP-88/Capture.git
cd Capture
```

2. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run Capture:**
```bash
python run.py
```

---

## 📸 Screenshots

<div align="center">

### Main Interface
*Grid-based screenshot library with dark GNOME theme*

### Adjustment Panel
*Google Photos-style controls for brightness, contrast, saturation, and sharpness*

### PII Sanitization
*Automatic detection and redaction of sensitive data (IPs, API keys, emails)*

> **Note:** The application features a fully dark-themed interface that integrates seamlessly with GNOME's aesthetic.

</div>

---

## 📖 Usage

### Importing Screenshots

1. Click **📥 Import** in the toolbar
2. Select one or more image files
3. Screenshots are automatically:
   - Validated for security
   - Copied to the vault
   - Added to the library with metadata

### Enhancing Images

1. Select a screenshot from the library
2. Click **🔍 Sharpen** to improve text legibility
3. The modified version is saved separately (chain-of-custody)

### Sanitizing PII

1. Select a screenshot
2. Click **🔒 Sanitize PII**
3. Automatic detection runs (may take a few seconds)
4. If PII is found, it's automatically blurred
5. A log of redacted items is saved to the database

### Exporting

- **Clipboard**: Click **📋 Copy to Clipboard**, then paste anywhere
- **File**: Click **💾 Export**, choose format and location

---

## 🔐 Security Features

### 1. Local-First Processing
- **Zero cloud uploads**: All processing happens on your machine
- No external API calls
- No telemetry or tracking

### 2. Path Traversal Prevention
- Validates all file paths using absolute path resolution
- Prevents directory traversal attacks
- Sanitizes filenames for safe storage

### 3. File Type Validation
- Uses magic number detection (not just extensions)
- Only allows validated image formats
- Prevents malicious file uploads

### 4. EXIF Stripping
- All exports have metadata removed
- Prevents location/device leakage
- Anonymizes exported images

### 5. Input Sanitization
- SQL injection prevention (SQLAlchemy + additional sanitization)
- No shell command execution (`shell=True` is never used)
- Secure file handling throughout

---

## 🏗️ Architecture

```
Capture/
├── src/
│   ├── main.py              # Application entry point
│   ├── gui/                 # PyQt6 UI components
│   │   ├── main_window.py   # Main application window
│   │   ├── library_view.py  # Screenshot gallery
│   │   └── styles.py        # Dark theme
│   ├── core/                # Core functionality
│   │   ├── database.py      # SQLAlchemy models
│   │   ├── image_processor.py  # Enhancement engine
│   │   ├── sanitizer.py     # PII detection/redaction
│   │   └── exporter.py      # Export functionality
│   └── utils/               # Utilities
│       ├── security.py      # Security validation
│       └── metadata.py      # EXIF handling
├── data/
│   ├── vault/
│   │   ├── originals/       # Original screenshots
│   │   └── modified/        # Enhanced/sanitized versions
│   └── capture.db          # SQLite database
└── run.py                   # Launch script
```

---

## 🧪 Tech Stack

- **Backend**: Python 3.12+
- **GUI**: PyQt6 (dark-themed, GNOME-native)
- **Database**: SQLite with SQLAlchemy ORM
- **Image Processing**: OpenCV + Pillow
- **OCR**: Tesseract (pytesseract)
- **Security**: python-magic, regex validation

---

## 🛣️ Roadmap

- [ ] Interactive highlight tool with color selection
- [ ] AI upscaling integration (Real-ESRGAN)
- [ ] Batch processing mode
- [ ] Tag management UI
- [ ] Export templates for security reports
- [ ] Keyboard shortcuts
- [ ] Dark mode toggle

<div align="center">

## 🤝 Contributing

**We Welcome All Developers!** 

</div>

**Capture** is an open-source project built for the community, by the community. Whether you're a security researcher, a Python developer, a UI/UX enthusiast, or just someone with a great idea - **your contributions are warmly welcomed!**

<div align="center">

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/OP-88/Capture/pulls)
[![Contributors](https://img.shields.io/github/contributors/OP-88/Capture)](https://github.com/OP-88/Capture/graphs/contributors)
[![Issues](https://img.shields.io/github/issues/OP-88/Capture)](https://github.com/OP-88/Capture/issues)

⭐ **If you find Capture useful, please star the repository!** It helps others discover the project.

</div>

### How to Contribute

1. **Fork the repository** and create a feature branch
2. **Make your changes** with clear, descriptive commit messages
3. **Test thoroughly** on Fedora GNOME (or your Linux distribution)
4. **Submit a pull request** with a description of what you've improved

### Guidelines

- Follow the existing code style (PEP 8 for Python)
- Maintain the local-first, security-focused philosophy
- Add tests for new features when applicable
- Update documentation for user-facing changes

**Found a bug or have a feature idea?** Open an issue on GitHub! We appreciate all feedback.

---

## 📝 License

GNU General Public License v3.0 - See LICENSE for details

---

## 🙏 Acknowledgments

- Built for the cybersecurity and DevOps community
- Inspired by the need for secure, local-first tooling
- Designed with input from security professionals

---

**Philosophy:**

> **🔒 Local is King**: Nothing leaves the machine  
> **✨ Clarity is Truth**: If you can't read it, it failed  
> **💻 Developer-Focused**: Understands code and terminal aesthetics  
> **📋 Chain of Custody**: Maintains integrity for documentation

<div align="center">

---

**Made with ❤️ for the Security Community**

</div>
