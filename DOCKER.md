# Running Capture with Docker

Run the Capture screenshot enhancement tool in an isolated container on any operating system.

## Quick Start

### Linux
```bash
# Build the image
docker build -t capture:latest .

# Run with the helper script
./docker-run-linux.sh
```

### macOS
```bash
# Install XQuartz first
brew install --cask xquartz

# Build the image
docker build -t capture:latest .

# Run with the helper script
./docker-run-macos.sh
```

### Windows
```powershell
# Install WSL2 and Docker Desktop
# Install VcXsrv: https://sourceforge.net/projects/vcxsrv/

# Build the image
docker build -t capture:latest .

# Run with the helper script
.\docker-run-windows.ps1
```

---

## Prerequisites

### All Platforms
- **Docker** (or Podman): Container runtime
  - [Docker Desktop](https://www.docker.com/products/docker-desktop) (macOS/Windows)
  - [Docker Engine](https://docs.docker.com/engine/install/) (Linux)

### Linux
- X11 server (usually pre-installed on GNOME/KDE)
- `xhost` utility for X11 access control

### macOS
- **XQuartz**: X11 server for macOS
  ```bash
  brew install --cask xquartz
  ```
  - After installation, log out and log back in
  - Start XQuartz and go to Preferences → Security
  - Enable "Allow connections from network clients"

### Windows
- **WSL2**: Windows Subsystem for Linux 2
  - [Installation guide](https://docs.microsoft.com/en-us/windows/wsl/install)
- **X Server**: VcXsrv or Xming
  - [Download VcXsrv](https://sourceforge.net/projects/vcxsrv/)
  - Run with: XLaunch → Multiple windows → Display 0 → Start no client  → **Check "Disable access control"**

---

## Building the Image

```bash
# From the Capture directory
docker build -t capture:latest .

# Or with Podman
podman build -t capture:latest .
```

**Expected build time**: 3-5 minutes (depending on your connection)  
**Image size**: ~800MB

---

## Running the Container

### Option 1: Helper Scripts (Recommended)

**Linux:**
```bash
./docker-run-linux.sh
```

**macOS:**
```bash
./docker-run-macos.sh
```

**Windows (PowerShell):**
```powershell
.\docker-run-windows.ps1
```

### Option 2: Docker Compose

```bash
# Start
docker-compose up

# Stop (Ctrl+C, then)
docker-compose down
```

### Option 3: Manual Docker Run

**Linux:**
```bash
xhost +local:docker
docker run --rm \
    --net=host \
    -e DISPLAY=$DISPLAY \
   -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    --security-opt label=disable \
    -v capture-data:/app/data \
    --name capture \
    capture:latest
xhost -local:docker
```

**macOS:**
```bash
# Get your IP
IP=$(ifconfig en0 | grep "inet " | awk '{print $2}')
xhost + $IP

docker run --rm \
    -e DISPLAY=$IP:0 \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v capture-data:/app/data \
    --name capture \
    capture:latest
```

**Windows (PowerShell):**
```powershell
$env:DISPLAY = "host.docker.internal:0"

docker run --rm `
    -e DISPLAY=$env:DISPLAY `
    -v capture-data:/app/data `
    --name capture `
    capture:latest
```

---

## Data Persistence

Your screenshots and database are stored in a Docker volume named `capture-data`.

### View Data Location
```bash
docker volume inspect capture-data
```

### Backup Data
```bash
# Create backup
docker run --rm \
    -v capture-data:/data \
    -v $(pwd):/backup \
    alpine tar czf /backup/capture-backup.tar.gz -C /data .

# This creates capture-backup.tar.gz in your current directory
```

### Restore Data
```bash
# Restore from backup
docker run --rm \
    -v capture-data:/data \
    -v $(pwd):/backup \
    alpine tar xzf /backup/capture-backup.tar.gz -C /data
```

### Use Custom Data Directory
Edit `docker-compose.yml` and uncomment:
```yaml
volumes:
  # - capture-data:/app/data  # Comment this line
  - ./data:/app/data           # Uncomment this line
```

---

## Troubleshooting

### Linux: "Cannot connect to display"
```bash
# Grant X11 access
xhost +local:docker

# Check DISPLAY is set
echo $DISPLAY

# If using Wayland, try
export QT_QPA_PLATFORM=wayland
```

### macOS: GUI doesn't appear
1. **Ensure XQuartz is running**: Check menu bar for XQuartz icon
2. **Check XQuartz settings**:
   - Preferences → Security → "Allow connections from network clients" ✓
3. **Restart XQuartz** and try again

### Windows: "X server not found"
1. **Start VcXsrv** with these settings:
   - Multiple windows
   - Display: 0
   - Start no client
   - **Disable access control** ✓
2. **Check Windows Firewall** isn't blocking VcXsrv
3. **Verify WSL2** is installed: `wsl --list --verbose`

### Icons appear as rectangles
**Solution**: Rebuild the image (emoji fonts are now included):
```bash
docker build --no-cache -t capture:latest .
```

### Permission Denied
If you get permission errors with volumes:
```bash
# Linux/macOS
docker run --user $(id -u):$(id -g) ...
```

### Slow Performance
GUI apps in containers can be slower than native. For better performance:
- Use native installation (see main README.md)
- Reduce image quality adjustments
- Close other Docker containers

---

## Advanced Usage

### Run on Remote Server
```bash
# On server
docker run -d \
    -p 5900:5900 \
    -e DISPLAY=:99 \
    -v capture-data:/app/data \
    capture:latest

# Access via VNC client at server-ip:5900
```

### Custom Build Arguments
```bash
# Use different Python version
docker build --build-arg PYTHON_VERSION=3.11-slim -t capture:custom .
```

### Development Mode
Mount your local code for live editing:
```bash
docker run --rm \
    --net=host \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v $(pwd)/src:/app/src:ro \
    -v capture-data:/app/data \
    capture:latest
```

---

## Why Docker?

### Advantages
✅ **Cross-platform**: Run on Linux, macOS, Windows  
✅ **Isolated**: No Python version conflicts  
✅ **Reproducible**: Same environment everywhere  
✅ **Easy cleanup**: Remove container = remove everything  

### Disadvantages
⚠️ **Setup complexity**: Requires X server on macOS/Windows  
⚠️ **Performance**: GUI apps are slower in containers  
⚠️ **File access**: Need volume mounting for file operations  

**Recommendation**: Use Docker for testing/demos. For daily use, install natively (see [INSTALL.md](INSTALL.md)).

---

## Uninstalling

```bash
# Remove container
docker rm -f capture

# Remove image
docker rmi capture:latest

# Remove data volume (⚠️ deletes all screenshots)
docker volume rm capture-data

# Remove all Capture resources
docker-compose down -v
docker rmi capture:latest
```

---

**Need help?** Open an issue on [GitHub](https://github.com/OP-88/Capture/issues)
