# Capture - Deployment Guide

## Quick Installation (Recommended)

### Method 1: Direct Install from GitHub

```bash
# Clone the repository
git clone https://github.com/OP-88/Capture.git
cd Capture

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Capture
python run.py
```

---

## Standalone Installation

### RPM Package for Fedora

**Build the RPM package:**

```bash
# Install build dependencies
sudo dnf install -y rpm-build rpmdevtools python3-devel

# Build the RPM
./build-rpm.sh
```

**Install the RPM:**

```bash
# Install system dependencies first
sudo dnf install -y python3 tesseract file-libs

# Install Capture
sudo dnf install ./capture-1.0.0-1.*.noarch.rpm
```

**Run Capture:**

```bash
capture
```

### System Dependencies

Before installing, ensure these system packages are installed:

```bash
sudo dnf install -y \
    python3 \
    python3-pip \
    tesseract \
    tesseract-langpack-eng \
    file-libs
```

---

## Building from Source

### Prerequisites

- Fedora Linux (or compatible RHEL-based distribution)
- Python 3.12 or higher
- Git

### Steps

1. **Clone and enter the repository:**
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

4. **Create data directories:**
   ```bash
   mkdir -p data/vault/originals data/vault/modified
   ```

5. **Run:**
   ```bash
   python run.py
   ```

---

## Desktop Integration

### Create Desktop Entry (Manual)

If not using the RPM package, you can manually add Capture to your applications menu:

```bash
cat > ~/.local/share/applications/capture.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Capture
Comment=Screenshot Enhancement Tool for Security Professionals
Exec=/home/$(whoami)/Capture/venv/bin/python /home/$(whoami)/Capture/run.py
Icon=camera
Terminal=false
Categories=Graphics;Photography;Security;
Keywords=screenshot;security;pii;sanitize;
EOF
```

Update the `Exec` path to match your Capture installation location.

---

## Uninstallation

### RPM Package

```bash
sudo dnf remove capture
```

### Manual Installation

```bash
cd /path/to/Capture
rm -rf venv
cd ..
rm -rf Capture
```

Remove desktop entry:
```bash
rm ~/.local/share/applications/capture.desktop
```

---

## Troubleshooting

### Missing Dependencies

If you encounter import errors:

```bash
# Ensure system dependencies
sudo dnf install -y tesseract file-libs

# Reinstall Python dependencies
source venv/bin/activate
pip install --force-reinstall -r requirements.txt
```

### OCR Not Working

Install Tesseract language packs:

```bash
sudo dnf install -y tesseract-langpack-eng
```

### PyQt6 Display Issues

Ensure you have proper graphics drivers and X11/Wayland support:

```bash
sudo dnf install -y mesa-dri-drivers
```

---

## Updates

### Git-based Installation

```bash
cd Capture
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### RPM Installation

Download and install the latest RPM from GitHub releases:

```bash
sudo dnf upgrade ./capture-*.rpm
```
