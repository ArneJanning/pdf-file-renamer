# Test Suite Summary

This document provides an overview of the comprehensive test suite for the PDF File Renamer application.

## Test Coverage

The test suite covers all major components and functionality:

### 1. Unit Tests (`test_models.py`)
- **BibliographicInfo Model**: 15 tests covering:
  - Object creation with various field combinations
  - Property calculations (`author_or_editor`, `author_or_editor_last`)
  - Filename formatting with different templates
  - Special character cleaning and filename safety
  - Long text truncation
  - Template variable substitution

### 2. PDF Extraction Tests (`test_pdf_extractor.py`)
- **PDF Text Extraction**: 8 tests covering:
  - Successful text extraction from multi-page PDFs
  - Page limit handling
  - Empty/corrupted PDF handling
  - Error handling and logging
- **PDF File Discovery**: 8 tests covering:
  - Directory scanning for PDF files
  - Handling of nested directories
  - Special filename characters
  - Non-existent directories and error cases

### 3. AI Integration Tests (`test_ai_extractor.py`)
- **BibliographicExtractor**: 12 tests covering:
  - Successful AI API integration
  - Complex name handling (international names, et al.)
  - Error handling and API failures
  - Environment variable management
  - System prompt content validation

### 4. CLI Tests (`test_cli.py`)
- **Configuration Loading**: 3 tests covering:
  - Environment variable parsing
  - Default value handling
  - Missing API key detection
- **PDF Processing**: 5 tests covering:
  - Successful processing workflow
  - Dry-run mode
  - Error handling (no text, no bibliographic info)
  - Duplicate filename handling
- **Directory Processing**: 3 tests covering:
  - Batch processing multiple files
  - Empty directory handling
  - Error recovery for individual files
- **CLI Interface**: 8 tests covering:
  - Help message display
  - Command-line argument parsing
  - Output directory creation
  - Error handling and user feedback

### 5. Integration Tests (`test_integration.py`)
- **End-to-End Workflows**: 4 tests covering:
  - Complete CLI-to-file-rename workflow
  - Error handling workflows
  - Dry-run integration
- **Component Integration**: 4 tests covering:
  - PDF extractor with real file paths
  - File discovery integration
  - Template formatting integration
  - AI extractor with mocked responses
- **Error Handling Integration**: 3 tests covering:
  - Invalid paths
  - Corrupted PDFs
  - API errors
- **Real File Operations**: 2 tests covering:
  - Actual file renaming with filesystem
  - Duplicate filename handling

### 6. Performance Tests (`test_performance.py`)
- **Performance Characteristics**: 6 tests covering:
  - Large directory scanning (100+ files)
  - Large PDF text processing
  - Filename cleaning performance
  - Concurrent processing simulation
  - Memory efficiency
  - Special character handling performance
- **Scalability Tests**: 2 tests covering:
  - Nested directory structures
  - Complex template performance
- **Stress Tests**: 2 tests covering:
  - Extremely long titles (5KB+)
  - Many special characters

### 7. Package Tests (`test_package.py`)
- **Package Integrity**: 3 tests covering:
  - Version definition
  - Import functionality
  - Module execution

## Test Fixtures and Utilities (`conftest.py`)

Comprehensive fixtures providing:
- Sample bibliographic data objects
- Mock extractors and API responses
- Temporary directory structures
- PDF creation utilities
- Environment cleanup
- Test data parameterization

## Test Statistics

- **Total Test Files**: 7
- **Total Test Functions**: ~80
- **Test Categories**:
  - Unit Tests: 40+
  - Integration Tests: 15+
  - Performance Tests: 10+
  - CLI Tests: 15+
- **Mock Coverage**: All external dependencies (Anthropic API, file system operations)
- **Edge Cases**: Comprehensive coverage of error conditions, empty data, invalid inputs

## Running Tests

### Basic Test Run
```bash
pytest tests/ -v
```

### With Coverage
```bash
pytest tests/ --cov=file_renamer --cov-report=term-missing
```

### Performance Tests Only
```bash
pytest tests/test_performance.py -v
```

### Exclude Slow Tests
```bash
pytest tests/ -v -m "not slow"
```

### Using Test Runner
```bash
python run_tests.py --install  # Install dependencies and run tests
```

## Continuous Integration

GitHub Actions workflow (`.github/workflows/tests.yml`) runs:
- Full test suite on Python 3.12
- Coverage reporting
- Code quality checks (ruff, black, isort)
- Automated testing on push/PR

## Test Design Principles

1. **Isolation**: Each test is independent and can run in any order
2. **Mocking**: External dependencies (APIs, file system) are mocked for reliability
3. **Real Data**: Integration tests use real file operations where appropriate
4. **Error Coverage**: Comprehensive testing of error conditions
5. **Performance**: Dedicated performance and scalability testing
6. **Maintainability**: Clear test names and documentation

## Coverage Goals

- **Line Coverage**: >95%
- **Branch Coverage**: >90%
- **Function Coverage**: 100%
- **Integration Coverage**: All major user workflows

## Mock Strategy

- **Anthropic API**: Fully mocked with realistic responses
- **PDF Operations**: Mocked for unit tests, real for integration tests
- **File System**: Mocked for reliability, real for integration verification
- **Environment Variables**: Controlled via fixtures and patches

## Known Limitations

- Tests require `fpdf2` for PDF creation in integration tests
- Performance tests are timing-dependent and may vary by system
- API mocking may not catch all edge cases in real Anthropic API responses
- Some tests are marked as "slow" and excluded from quick test runs