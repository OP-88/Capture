# Production Dockerfile for Capture Application
# Optimized for cross-platform deployment with GUI support

FROM python:3.12-slim

LABEL maintainer="OP-88"
LABEL description="Capture - Local-First Screenshot Enhancement Tool"
LABEL version="1.0.0"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # X11 and GUI libraries for PyQt6
    libxcb-cursor0 \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libxkbcommon0 \
    # OpenGL/EGL support
    libgl1 \
    libegl1 \
    libgles2 \
    # Core GUI libraries
    libglib2.0-0 \
    libdbus-1-3 \
    libfontconfig1 \
    libfreetype6 \
    libx11-xcb1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    # OpenCV dependencies
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    # Tesseract OCR
    tesseract-ocr \
    tesseract-ocr-eng \
    # File type validation
    libmagic1 \
    # Emoji fonts for icon rendering
    fonts-noto-color-emoji \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories with proper permissions
RUN mkdir -p data/vault/originals data/vault/modified && \
    chmod -R 755 data

# Set environment variables for Qt
ENV QT_X11_NO_MITSHM=1 \
    QT_QPA_PLATFORM=xcb \
    PYTHONUNBUFFERED=1

# Run as non-root user for security (optional, commented out for easier volume access)
# RUN useradd -m -u 1000 capture && \
#     chown -R capture:capture /app
# USER capture

# Entry point
CMD ["python3", "run.py"]
