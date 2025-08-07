# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2025-01-08

### Added
- 🎯 **Dual OCR Methods for Screenshots**
  - Tesseract OCR (default): Local processing, fast, free
  - Claude Vision: Direct image analysis, more accurate, no OCR errors
  - New `--ocr-method` CLI option to choose between methods
  - `OCR_METHOD` environment variable for persistent configuration

### Changed
- Screenshot processing now supports both local OCR and cloud-based vision
- Updated documentation with OCR method comparison and recommendations

### Technical
- Added `_extract_from_image()` method using Anthropic API directly for vision
- Made Tesseract optional - only required when using local OCR method

## [0.2.0] - 2025-01-08

### Added
- 🖼️ **Screenshot Processing Support**
  - OCR text extraction using Tesseract for screenshots
  - AI analysis to identify applications, dates, content types, and subjects
  - Support for PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP formats
  - Intelligent categorization (email, chat, error, website, document, etc.)

- 📋 **New Screenshot Model**
  - `ScreenshotInfo` model with application, date, time, content_type, and main_subject fields
  - `ScreenshotExtractor` class for AI-powered screenshot analysis

- 🎯 **Enhanced Configuration**
  - Separate templates for PDFs and screenshots
  - `PDF_FILENAME_TEMPLATE` for PDF files
  - `SCREENSHOT_FILENAME_TEMPLATE` for screenshots
  - Backward compatibility with legacy `FILENAME_TEMPLATE`

- 🔧 **CLI Improvements**
  - `--pdf-template` option to override PDF template
  - `--screenshot-template` option to override screenshot template
  - Mixed directory processing (PDFs and screenshots together)
  - Enhanced progress reporting showing file type counts

- 📦 **New Dependencies**
  - `pytesseract>=0.3.10` for OCR functionality
  - `pillow>=10.0.0` for image processing

### Changed
- Updated CLI help text to reflect support for both PDFs and screenshots
- Enhanced file detection to handle multiple image formats
- Improved logging to distinguish between PDF and screenshot processing
- Renamed `pdf_extractor.py` module to handle both PDFs and screenshots

### Fixed
- Extension preservation in output filenames for screenshots
- Proper handling of missing dates/times in screenshots

## [0.1.0] - 2025-01-07

### Added
- Initial release with PDF processing functionality
- AI-powered bibliographic information extraction
- Customizable filename templates
- Batch processing capabilities
- Dry-run mode for previewing changes
- Comprehensive test suite (80+ tests)
- Support for authors and editors
- Smart last name extraction
- Configurable page extraction limits

### Features
- Claude AI integration for intelligent text analysis
- Flexible template system with multiple variables
- Safe duplicate filename handling
- Support for various naming conventions
- Environment-based configuration
- CLI with intuitive options

[0.2.0]: https://github.com/ArneJanning/pdf-file-renamer/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ArneJanning/pdf-file-renamer/releases/tag/v0.1.0