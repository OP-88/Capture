#!/bin/bash
# Capture - Docker run script for macOS
# Launches the Capture GUI application in a Docker container with XQuartz

set -e

echo "🐳 Starting Capture in Docker (macOS)..."

# Check if XQuartz is installed
if ! command -v xquartz &> /dev/null && ! [ -d /Applications/XQuartz.app ]; then
    echo "❌ Error: XQuartz is not installed"
    echo "Please install XQuartz from: https://www.xquartz.org/"
    exit 1
fi

# Check if XQuartz is running
if ! pgrep -x "Xquartz" > /dev/null; then
    echo "⚠️  XQuartz is not running. Starting XQuartz..."
    echo "Please allow XQuartz to start, then run this script again."
    open -a XQuartz
    exit 0
fi

# Get IP address for XQuartz
IP=$(ifconfig en0 | grep "inet " | awk '{print $2}')
if [ -z "$IP" ]; then
    IP=$(ifconfig en1 | grep "inet " | awk '{print $2}')
fi

if [ -z "$IP" ]; then
    echo "❌ Error: Could not determine IP address"
    exit 1
fi

echo "Using IP: $IP"

# Allow connections from localhost
xhost + $IP

# Set DISPLAY for XQuartz
export DISPLAY=$IP:0

# Run the container
echo "Launching Capture GUI..."
docker run --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v capture-data:/app/data \
    --name capture \
    capture:latest

echo "✅ Capture stopped"
