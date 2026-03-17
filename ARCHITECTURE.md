# Capture - Technical Architecture & System Design

**Version**: 1.0.4  
**Document Type**: Technical Presentation  
**Last Updated**: January 2026  
**Author**: OP-88

---

## Executive Summary

**Capture** is a local-first screenshot management and PII sanitization tool designed for security professionals and privacy-conscious users. Built with Python and PyQt6, it provides enterprise-grade screenshot management with automated PII detection and redaction capabilities using OCR and computer vision.

### Key Capabilities
- 🔒 **PII Sanitization**: Automated detection and redaction of sensitive data
- 📝 **OCR Integration**: Text extraction using Tesseract
- 🖼️ **Image Processing**: Real-time adjustments with OpenCV
- 💾 **Local-First**: Zero cloud dependencies, complete privacy
- 📦 **Multi-Platform**: Flatpak, Docker, RPM distribution

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  MainWindow   │  │ LibraryView  │  │ AdjustmentPanel  │  │
│  │   (PyQt6)     │  │   (PyQt6)    │  │     (PyQt6)      │  │
│  └───────┬───────┘  └──────┬───────┘  └─────────┬────────┘  │
└──────────┼──────────────────┼───────────────────┼───────────┘
           │                  │                   │
┌──────────┼──────────────────┼───────────────────┼───────────┐
│          │        Business Logic Layer          │           │
│  ┌───────┴────────┐  ┌─────┴──────┐  ┌────────┴────────┐   │
│  │ ImageProcessor │  │ PIISanitizer│  │   Exporter      │   │
│  │   (OpenCV)     │  │ (OCR + CV)  │  │  (Metadata)     │   │
│  └───────┬────────┘  └─────┬──────┘  └────────┬────────┘   │
└──────────┼──────────────────┼───────────────────┼───────────┘
           │                  │                   │
┌──────────┼──────────────────┼───────────────────┼───────────┐
│          │           Data Layer                 │           │
│  ┌───────┴─────────┐  ┌────┴────────┐  ┌──────┴─────────┐  │
│  │ DatabaseManager │  │  Screenshot  │  │ SecurityValidator││
│  │  (SQLAlchemy)   │  │   (Model)    │  │  (FileSystem)   │  │
│  └─────────────────┘  └──────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
           │                                      │
┌──────────┼──────────────────────────────────────┼───────────┐
│          │        External Dependencies         │           │
│  ┌───────┴────────┐  ┌──────────────┐  ┌──────┴─────────┐  │
│  │  Tesseract OCR │  │    OpenCV    │  │     SQLite     │  │
│  │   (C++ lib)    │  │  (Computer   │  │   (Database)   │  │
│  │                │  │    Vision)   │  │                │  │
│  └────────────────┘  └──────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Presentation Layer (GUI)

#### MainWindow (`src/gui/main_window.py`)
**Purpose**: Primary application window and UI orchestration

**Responsibilities**:
- Application lifecycle management
- Toolbar and menu coordination
- Screenshot import/export workflow
- Real-time preview rendering
- Event handling and user interactions

**Key Methods**:
```python
__init__()                      # Initialize UI components
import_screenshots()            # Handle file import dialog
on_screenshot_selected(id)      # Load and display screenshot
on_adjustments_changed(dict)    # Apply real-time edits
sanitize_current()              # Trigger PII sanitization
export_current()                # Export with metadata
```

**Dependencies**:
- PyQt6 (QMainWindow, QToolBar, QPushButton)
- Database Manager (screenshot persistence)
- Image Processor (real-time adjustments)
- PII Sanitizer (redaction operations)

#### LibraryView (`src/gui/library_view.py`)
**Purpose**: Screenshot library grid display

**Features**:
- Thumbnail grid layout (200x200px previews)
- Lazy loading for performance
- Search and filter capabilities
- Selection state management
- Tag-based organization

#### AdjustmentPanel (`src/gui/adjustment_panel.py`)
**Purpose**: Real-time image editing controls

**Controls**:
- Brightness (-100 to +100)
- Contrast (0 to 2.0)
- Sharpness (0 to 2.0)
- Saturation (0 to 2.0)
- Live preview updates

**Implementation**: Qt Sliders with debounced callbacks (250ms) to prevent UI lag

---

### 2. Business Logic Layer

#### ImageProcessor (`src/core/image_processor.py`)
**Purpose**: Core image manipulation engine

**Capabilities**:
```python
adjust_brightness(image, value)     # -100 to +100
adjust_contrast(image, factor)      # 0.0 to 2.0
sharpen(image, strength)            # Unsharp mask filter
apply_filter(image, filter_type)    # Gaussian, median, bilateral
resize_image(image, dimensions)     # Smart resizing
```

**Technology Stack**:
- OpenCV (cv2) for all image operations
- NumPy arrays for efficient matrix operations
- Pillow for I/O operations

**Performance**: All operations are non-destructive; maintains original in memory

#### PIISanitizer (`src/core/sanitizer.py`)
**Purpose**: Automated PII detection and redaction

**Architecture**:
```
┌─────────────────────────────────────────────┐
│          PIISanitizer                        │
│  ┌──────────────────────────────────────┐   │
│  │     PIIDetector                       │   │
│  │  ┌─────────────────────────────────┐ │   │
│  │  │  Regex Patterns                  │ │   │
│  │  │  - IPv4/IPv6                     │ │   │
│  │  │  - Email addresses               │ │   │
│  │  │  - API keys (AWS, GitHub,etc)    │ │   │
│  │  │  - JWT tokens                    │ │   │
│  │  │  - Private keys                  │ │   │
│  │  └─────────────────────────────────┘ │   │
│  │                                       │   │
│  │  ┌─────────────────────────────────┐ │   │
│  │  │  Tesseract OCR                   │ │   │
│  │  │  - Text extraction               │ │   │
│  │  │  - Bounding box detection        │ │   │
│  │  └─────────────────────────────────┘ │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  Redaction Methods:                          │
│  - blur_region()      (Gaussian blur)        │
│  - pixelate_region()  (Block pixelation)     │
└─────────────────────────────────────────────┘
```

**Detection Patterns**:
| Pattern Type | Regex | Example |
|--------------|-------|---------|
| IPv4 | `\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b` | 192.168.1.1 |
| IPv6 | `\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\b` | ::1 |
| Email | `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z\|a-z]{2,}\b` | user@example.com |
| AWS Key | `\bAKIA[0-9A-Z]{16}\b` | AKIAIOSFODNN7EXAMPLE |
| GitHub Token | `\bghp_[A-Za-z0-9]{36}\b` | ghp_xxxx... |
| JWT | `\beyJ[A-Za-z0-9-_=]+\.eyJ...` | eyJhbGc... |

**Workflow**:
1. **Text Extraction**: OCR scans entire image
2. **Pattern Matching**: Regex against known PII patterns
3. **Location Detection**: Find bounding boxes via Tesseract
4. **Redaction**: Apply blur/pixelation with padding
5. **Logging**: Record detected types for audit trail

#### Exporter (`src/core/exporter.py`)
**Purpose**: Safe export with  metadata handling

**Features**:
- EXIF metadata stripping
- Secure file handling
- Format conversion (PNG, JPG, WebP)
- Chain-of-custody logging

---

### 3. Data Layer

#### DatabaseManager (`src/core/database.py`)
**Purpose**: SQLite database abstraction with SQLAlchemy ORM

**Schema**:
```sql
CREATE TABLE screenshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_path VARCHAR(512) NOT NULL,
    modified_path VARCHAR(512),
    import_date DATETIME NOT NULL,
    last_modified DATETIME NOT NULL,
    tags VARCHAR(512) DEFAULT '',
    image_metadata JSON DEFAULT '{}',
    sanitization_log TEXT
);
```

**Operations**:
```python
add_screenshot(path, metadata, tags)     # Create
get_screenshot(id)                       # Read
update_screenshot(id, modified_path)     # Update
delete_screenshot(id)                    # Delete (with file cleanup)
search_by_tags(tag)                      # Query
```

**Data Storage**:
- **Database**: `~/.local/share/capture/capture.db` (XDG-compliant)
- **Images**: `~/.local/share/capture/images/`
  - `original/` - Unmodified imports
  - `modified/` - Edited versions
  - `exports/` - Final outputs

**Backup Strategy**: SQLite database + file system, easily portable

#### Screenshot Model
**Fields**:
- `id`: Primary key
- `original_path`: Immutable source
- `modified_path`: Current working version
- `import_date`: Timestamp (UTC)
- `last_modified`: Auto-updated on changes
- `tags`: Comma-separated string
- `image_metadata`: JSON (width, height, format, file_size)
- `sanitization_log`: Audit trail of PII redactions

---

## Data Flow

### Import Workflow
```
User selects files
     │
     ▼
SecurityValidator.validate_file()
  ├─ Check file type (PNG, JPG, WebP)
  ├─ Verify file size (< 50MB)
  ├─ Scan for malicious content
  └─ Validate image integrity
     │
     ▼
MetadataHandler.extract_metadata()
  ├─ Read EXIF tags
  ├─ Extract dimensions
  ├─ Calculate file hash  (SHA-256)
  └─ Store timestamp
     │
     ▼
DatabaseManager.add_screenshot()
  ├─ Copy to original/ directory
  ├─ Generate thumbnail
  ├─ Insert database record
  └─ Return screenshot ID
     │
     ▼
LibraryView.refresh()
  ├─ Query database
  ├─ Load thumbnails
  └─ Update grid display
```

### Sanitization Workflow
```
User clicks "Sanitize"
     │
     ▼
PIIDetector.extract_text_from_image()
  ├─ Load image with OpenCV
  ├─ Convert to grayscale
  ├─ Apply preprocessing (sharpen, denoise)
  └─ Run Tesseract OCR → Extract raw text
     │
     ▼
PIIDetector.detect_in_text()
  ├─ Iterate through regex patterns
  ├─ Find all PII matches
  ├─ Categorize by type (IP, email, key, etc.)
  └─ Return dictionary of findings
     │
     ▼
PIIDetector.find_text_locations()
  ├─ Run Tesseract with bounding boxes
  ├─ Match detected strings to image coordinates
  ├─ Apply padding (5px) for safety
  └─ Return [(x, y, width, height), ...]
     │
     ▼
PIISanitizer.blur_region() / .pixelate_region()
  ├─ Extract ROI from image
  ├─ Apply Gaussian blur (kernel 25x25)
  │   OR downsample and upsample for pixelation
  ├─ Replace original region
  └─ Return modified image
     │
     ▼
DatabaseManager.update_screenshot()
  ├─ Save modified image to modified/ directory
  ├─ Log sanitization actions
  ├─ Update database record
  └─ Refresh preview
```

### Export Workflow
```
User clicks "Export"
     │
     ▼
Exporter.prepare_for_export()
  ├─ Load current working image
  ├─ Strip all EXIF metadata
  ├─ Apply final adjustments
  └─ Convert to target format
     │
     ▼
User chooses destination
     │
     ▼
Exporter.export()
  ├─ Validate output path
  ├─ Write image file
  ├─ Set secure file permissions (0644)
  ├─ Log export event
  └─ Show confirmation dialog
```

---

## Security Model

### Threat Model

**In Scope**:
- Accidental PII exposure in screenshots
- Metadata leakage (EXIF, GPS, camera info)
- File system security (XDG compliance)
- SQL injection (via SQLAlchemy parameterization)

**Out of Scope**:
- Network transmission (local-first design)
- Memory forensics
- Screen recording attack vectors

### Security Features

#### 1. PII Detection & Redaction
**Patterns**: 10+ regex patterns for common sensitive data
**Methods**: 
- **Blur**: Gaussian blur (configurable strength, default 25px kernel)
- **Pixelate**: Downsampling to blocks (default 10px)
**Padding**: 5px safety margin around detected regions

#### 2. Metadata Sanitization
**EXIF Stripping**: All metadata removed on export using Pillow
**Clean Export**: Only pixel data written to output files
**Chain of Custody**: Immutable original + audit log

#### 3. File System Security
**Permissions**:
- Database: `0600` (owner read/write only)
- Images: `0644` (owner write, all read)
- Directories: `0755`

**XDG Base Directory**:
- Config: `~/.config/capture/` (unused currently)
- Data: `~/.local/share/capture/`
- Cache: `~/.cache/capture/thumbnails/`

#### 4. Input Validation
**SecurityValidator checks**:
- File type whitelist (PNG, JPG, JPEG, WebP)
- Magic number verification (prevents extension spoofing)
- File size limits (50MB max)
- Path traversal prevention
- Image integrity validation (via Pillow)

#### 5. Database Security
**SQLAlchemy ORM**: Automatic SQL injection prevention via parameterized queries
**Transactions**: ACID compliance for data integrity
**No External Access**: SQLite file, no network exposure

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Language** | Python | 3.12+ | Core application logic |
| **GUI Framework** | PyQt6 | 6.6.0+ | Cross-platform UI |
| **Image Processing** | OpenCV | 4.8.0+ | Computer vision operations |
| **Image I/O** | Pillow | 10.1.0+ | Image loading/saving |
| **OCR Engine** | Tesseract | 5.3.4 | Text extraction |
| **OCR Wrapper** | pytesseract | 0.3.10+ | Python bindings |
| **Database** | SQLite | 3.x | Local storage |
| **ORM** | SQLAlchemy | 2.0.23+ | Database abstraction |
| **File Type Detection** | python-magic | 0.4.27+ | Magic number validation |
| **Date/Time** | python-dateutil | 2.8.2+ | Timestamp handling |

### Development Dependencies

| Tool | Purpose |
|------|---------|
| **PyInstaller** | Binary packaging (RPM distribution) |
| **Docker** | Containerization |
| **flatpak-builder** | Flatpak packaging |
| **pytest** | Unit testing |
| **git** | Version control |

---

## Performance Characteristics

### Image Processing
- **Real-time adjustments**: <50ms (debounced to 250ms)
- **OCR text extraction**: 1-3 seconds (1080p image)
- **PII sanitization**: 2-5 seconds (depending on text quantity)
- **Import**: <500ms per image (incl. thumbnail generation)

### Memory Usage
- **Base application**: ~150MB
- **Per loaded image**: ~20-30MB (depending on resolution)
- **Thumbnail cache**: ~5MB per 100 screenshots

### Database Performance
- **Query speed**: <10ms (indexed by ID and import_date)
- **Full library load**: <100ms (500 screenshots)
- **Search by tag**: <50ms

---

## Distribution & Deployment

### Packaging Options

#### 1. Flatpak (Universal Linux)
**Runtime**: `org.freedesktop.Platform 24.08`
**Size**: 168 MB (includes all dependencies)
**Sandbox**: Yes (XDG filesystem access only)
**Distribution**: GitHub Releases + Flathub

**Dependencies Bundled**:
- Python 3.12
- PyQt6 6.10.2
- OpenCV 4.10.0
- Tesseract 5.3.4
- All Python packages

#### 2. Docker
**Base Image**: `python:3.12-slim`
**Size**: ~1.2 GB
**Platforms**: AMD64, ARM64
**Registry**: Docker Hub (`ogq0w3efq/capture:latest`)

**Features**:
- X11 forwarding for Linux
- XQuartz support for macOS
- WSL2 compatibility for Windows

#### 3. RPM (Fedora/RHEL)
**Size**: 322 KB (source only, system dependencies)
**Distribution**: GitHub Releases
**Dependencies**: System-provided Python, Qt, OpenCV

#### 4. Source Installation
```bash
git clone https://github.com/OP-88/Capture.git
cd Capture
pip install -r requirements.txt
python run.py
```

---

## API & Extension Points

### Plugin Architecture (Future)
Currently monolithic, but designed for future plugin system:

**Potential Extension Points**:
- Custom PII patterns (regex plugins)
- Additional sanitization methods (e.g., smart blur, AI-based detection)
- Export formats (PDF, encrypted archives)
- Cloud storage integrations (optional, user-controlled)
- Additional OCR engines (Google Vision, AWS Textract)

### Configuration File
**Location**: `~/.config/capture/config.json`
```json
{
  "ocr_language": "eng",
  "default_sanitization": "blur",
  "blur_strength": 25,
  "pixelation_size": 10,
  "auto_sanitize_on_import": false,
  "thumbnail_size": 200,
  "max_file_size_mb": 50,
  "export_quality": 95
}
```

---

## Testing Strategy

### Unit Tests (`test_capture.py`)
**Coverage**: Core modules (PIIDetector, ImageProcessor, DatabaseManager)

**Test Cases**:
```python
test_pii_detection_ipv4()
test_pii_detection_email()
test_pii_detection_api_keys()
test_image_adjustments()
test_database_crud_operations()
test_security_validation()
```

### Integration Tests
- End-to-end import workflow
- Sanitization with OCR
- Export with metadata stripping

### Manual Testing
- UI responsiveness
- Cross-platform compatibility
- Performance with large libraries (1000+ screenshots)

---

## Limitations & Known Issues

### Current Limitations
1. **Single-language OCR**: English only (Tesseract supports 100+ languages, but only English data bundled)
2. **No batch operations**: Sanitize one image at a time
3. **Limited undo/redo**: Only reset to original
4. **No image comparison**: Can't diff original vs modified
5. **No encryption**: Files stored unencrypted on disk

### Planned Enhancements
- Batch PII sanitization
- Multi-language OCR support
- Encrypted storage option
- Cloud backup (optional, user-controlled)
- AI-powered PII detection (beyond regex)
- Advanced search (image similarity)

---

## Development Roadmap

### v1.0.x (Current)
- ✅ Core PII sanitization
- ✅ Real-time image adjustments
- ✅ SQLite database
- ✅ Multi-platform distribution

### v1.1.0 (Q1 2026)
- Batch operations
- Undo/redo stack
- Additional OCR languages
- Performance optimizations

### v1.2.0 (Q2 2026)
- AI-based PII detection (LLM integration)
- Encrypted storage
- Plugin system
- Cloud backup (E2EE)

### v2.0.0 (Q3 2026)
- Complete UI redesign
- Web interface (optional)
- Mobile apps (React Native)
- Enterprise features (LDAP, SSO)

---

## Conclusion

**Capture** represents a robust, local-first approach to screenshot management with enterprise-grade security features. The architecture prioritizes:

1. **Privacy**: Zero cloud dependencies, local-only processing
2. **Security**: Automated PII detection, metadata sanitization
3. **Performance**: Real-time image processing, efficient database
4. **Usability**: Intuitive PyQt6 interface, multi-platform support
5. **Maintainability**: Clean separation of concerns, comprehensive testing

The application is production-ready for security professionals, penetration testers, and anyone requiring secure screenshot management with automated PII redaction.

---

**For more information**:
- GitHub: https://github.com/OP-88/Capture
- Documentation: https://github.com/OP-88/Capture/blob/main/README.md
- Flathub: https://flathub.org/apps/com.github.OP88.Capture
- Docker Hub: https://hub.docker.com/r/ogq0w3efq/capture

**License**: GPL-3.0  
**Maintainer**: OP-88  
**Contact**: Via GitHub Issues
