#!/bin/bash
# RPM Build Script for Capture

set -e

# Configuration
NAME="capture"
VERSION="1.0.0"
RELEASE="1"
SPEC_FILE="${NAME}.spec"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Capture RPM Build Script ===${NC}"

# Check if running on Fedora/RHEL
if ! [ -f /etc/fedora-release ] && ! [ -f /etc/redhat-release ]; then
    echo -e "${RED}Warning: This script is designed for Fedora/RHEL systems${NC}"
fi

# Install build dependencies
echo -e "${GREEN}[1/6] Installing build dependencies...${NC}"
sudo dnf install -y rpm-build rpmdevtools python3-devel

# Set up RPM build environment
echo -e "${GREEN}[2/6] Setting up RPM build environment...${NC}"
rpmdev-setuptree

# Create source tarball
echo -e "${GREEN}[3/6] Creating source tarball...${NC}"
cd ..
tar --exclude='Capture/.git' \
    --exclude='Capture/venv' \
    --exclude='Capture/__pycache__' \
    --exclude='Capture/src/__pycache__' \
    --exclude='Capture/src/*/__pycache__' \
    --exclude='Capture/data' \
    --exclude='Capture/.gitignore' \
    -czf ~/rpmbuild/SOURCES/${NAME}-${VERSION}.tar.gz \
    --transform "s/^Capture/${NAME}-${VERSION}/" \
    Capture
cd Capture

# Copy spec file
echo -e "${GREEN}[4/6] Copying spec file...${NC}"
cp ${SPEC_FILE} ~/rpmbuild/SPECS/

# Build RPM
echo -e "${GREEN}[5/6] Building RPM package...${NC}"
cd ~/rpmbuild/SPECS
rpmbuild -ba ${SPEC_FILE}

# Copy RPM to current directory
echo -e "${GREEN}[6/6] Copying built RPM...${NC}"
cd -
cp ~/rpmbuild/RPMS/noarch/${NAME}-${VERSION}-${RELEASE}.*.noarch.rpm .

echo -e "${GREEN}=== Build Complete! ===${NC}"
echo -e "RPM package: ${GREEN}${NAME}-${VERSION}-${RELEASE}.*.noarch.rpm${NC}"
echo ""
echo "To install:"
echo "  sudo dnf install ./${NAME}-${VERSION}-${RELEASE}.*.noarch.rpm"
echo ""
echo "To run after installation:"
echo "  capture"
