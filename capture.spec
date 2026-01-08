Name:           capture
Version:        1.0.0
Release:        1%{?dist}
Summary:        Local-first screenshot enhancement and library tool for security professionals

License:        GPLv3
URL:            https://github.com/OP-88/Capture
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

Requires:       python3 >= 3.12
Requires:       python3-PyQt6 >= 6.6.0
Requires:       python3-opencv >= 4.8.0
Requires:       python3-pillow >= 10.1.0
Requires:       python3-sqlalchemy >= 2.0.23
Requires:       python3-pytesseract >= 0.3.10
Requires:       python3-magic >= 0.4.27
Requires:       python3-dateutil >= 2.8.2
Requires:       tesseract
Requires:       file-libs

%description
Capture is a local-first screenshot enhancement and library tool designed for
security professionals on Fedora GNOME. It provides forensic-grade screenshot
management with PII sanitization, chain-of-custody tracking, and report-ready
image enhancement.

Features:
- Screenshot library with grid view and search
- Image enhancement (sharpen, highlight, upscale)
- PII sanitization with OCR + regex detection
- Secure export with EXIF stripping
- 100% local processing (zero cloud uploads)

%prep
%setup -q

%build
# No build step needed for pure Python

%install
rm -rf %{buildroot}

# Create installation directories
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/pixmaps
mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}/vault/originals
mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}/vault/modified

# Install application files
cp -r src %{buildroot}%{_datadir}/%{name}/
cp run.py %{buildroot}%{_datadir}/%{name}/
cp requirements.txt %{buildroot}%{_datadir}/%{name}/
cp README.md %{buildroot}%{_datadir}/%{name}/
cp LICENSE %{buildroot}%{_datadir}/%{name}/

# Create executable wrapper
cat > %{buildroot}%{_bindir}/capture << 'EOF'
#!/bin/bash
cd %{_datadir}/%{name}
export CAPTURE_DATA_DIR="%{_localstatedir}/lib/%{name}"
exec python3 run.py "$@"
EOF
chmod +x %{buildroot}%{_bindir}/capture

# Create desktop file
cat > %{buildroot}%{_datadir}/applications/capture.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Capture
Comment=Screenshot Enhancement Tool for Security Professionals
Exec=capture
Icon=capture
Terminal=false
Categories=Graphics;Photography;Security;
Keywords=screenshot;security;pii;sanitize;
EOF

# Create icon (minimal 1x1 PNG)
python3 -c "
import base64
# Minimal 1x1 transparent PNG
png_data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==')
with open('%{buildroot}%{_datadir}/pixmaps/capture.png', 'wb') as f:
    f.write(png_data)
"

%files
%license LICENSE
%doc README.md
%{_bindir}/capture
%{_datadir}/%{name}
%{_datadir}/applications/capture.desktop
%{_datadir}/pixmaps/capture.png
%dir %attr(0755,root,root) %{_localstatedir}/lib/%{name}
%dir %attr(0755,root,root) %{_localstatedir}/lib/%{name}/vault
%dir %attr(0755,root,root) %{_localstatedir}/lib/%{name}/vault/originals
%dir %attr(0755,root,root) %{_localstatedir}/lib/%{name}/vault/modified

%post
# Create data directories in user's home if needed
if [ "$1" -eq 1 ]; then
    echo "Capture installed successfully!"
    echo "Run 'capture' to launch the application"
fi

%changelog
* Wed Jan 08 2026 OP-88 <op88@example.com> - 1.0.0-1
- Initial release
- PyQt6 GUI with dark GNOME-native theme
- SQLAlchemy database for chain-of-custody tracking
- Image processor with sharpen, highlight, and upscale features
- PII sanitizer with OCR + regex detection
- Secure export with clipboard and EXIF stripping
- Comprehensive security validation
