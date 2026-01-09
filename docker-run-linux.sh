#!/bin/bash
# Capture - Docker run script for Linux
# Launches the Capture GUI application in a Docker container

set -e

echo "🐳 Starting Capture in Docker..."

# Grant X server access to Docker containers
echo "Granting X11 access to Docker..."
xhost +local:docker > /dev/null 2>&1

# Check if running via Docker or Podman
if command -v docker &> /dev/null; then
    DOCKER_CMD="docker"
elif command -v podman &> /dev/null; then
    DOCKER_CMD="podman"
else
    echo "❌ Error: Neither Docker nor Podman is installed"
    exit 1
fi

echo "Using: $DOCKER_CMD"

# Determine image source
if [ "$1" == "--local" ]; then
    IMAGE="capture:latest"
    echo "Using locally built image"
else
    IMAGE="op88/capture:latest"
    echo "Using Docker Hub image (op88/capture:latest)"
    echo "Pulling latest version..."
    $DOCKER_CMD pull $IMAGE
fi

# Run the container
echo "Launching Capture GUI..."
$DOCKER_CMD run --rm \
    --net=host \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    --security-opt label=disable \
    -v capture-data:/app/data \
    --name capture \
    $IMAGE

# Restore X server permissions
echo "Restoring X11 permissions..."
xhost -local:docker > /dev/null 2>&1

echo "✅ Capture stopped"
